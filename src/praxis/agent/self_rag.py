"""Self-RAG оркестратор — прозрачный (glass-box) луп.

    поиск → rerank → оценка достаточности → (доп-поиск/переформулировка) → ответ →
    проверка цитат

Каждый шаг пишется в `Answer.steps`, чтобы рассуждение было видимым (философия glia).
Останавливается, когда релевантность найденного достаточна, либо после `max_rounds`.
Проверку сгенерированного ответа делает Citation Verifier: у LLM-ответа каждый тезис
проверяется против норм (неподтверждённое — в unverified и не выдаётся за факт); у
экстрактивного ответа текст дословно взят из закона и грунтован по построению.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from ..core.models import Answer, Citation, Verdict
from ..generate.base import Answerer
from ..retrieve.base import Reranker, Retriever
from ..verify.base import CitationVerifier

_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


@dataclass
class SelfRAGConfig:
    retrieve_pool: int = 20
    rerank_top_k: int = 6
    answer_top_k: int = 5
    max_rounds: int = 2
    sufficiency_score: float = 0.35  # ниже — делаем доп-раунд с переформулировкой
    relevance_floor: float = 0.15  # абсолютный минимум релевантности нормы
    keep_ratio: float = 0.6  # держим нормы со скором >= keep_ratio * лучший (шкало-независимо)


class SelfRAG:
    def __init__(
        self,
        retriever: Retriever,
        verifier: CitationVerifier,
        answerer: Answerer,
        reranker: Reranker | None = None,
        config: SelfRAGConfig | None = None,
    ) -> None:
        self.retriever = retriever
        self.verifier = verifier
        self.answerer = answerer
        self.reranker = reranker
        self.config = config or SelfRAGConfig()

    def answer(self, question: str) -> Answer:
        cfg = self.config
        steps: list[str] = []
        pool: dict = {}  # provision.id -> RetrievedProvision (лучший скор)
        query = question

        for rnd in range(1, cfg.max_rounds + 1):
            cands = self.retriever.search(query, top_k=cfg.retrieve_pool)
            if self.reranker is not None:
                cands = self.reranker.rerank(query, cands, top_k=cfg.rerank_top_k)
            else:
                cands = cands[: cfg.rerank_top_k]

            for c in cands:
                cur = pool.get(c.provision.id)
                if cur is None or c.score > cur.score:
                    pool[c.provision.id] = c

            top_score = cands[0].score if cands else 0.0
            steps.append(
                f"Раунд {rnd}: «{query}» → {len(cands)} кандидатов (топ score {top_score:.2f})"
            )
            if cands and top_score >= cfg.sufficiency_score:
                steps.append("Релевантность достаточная — формирую ответ.")
                break
            if rnd < cfg.max_rounds:
                query = self._reformulate(question, cands)
                steps.append("Релевантность низкая — переформулирую запрос и до-ищу.")

        ranked = sorted(pool.values(), key=lambda r: r.score, reverse=True)
        provisions = ranked[: cfg.answer_top_k]

        if not provisions:
            answer = self.answerer.answer(question, provisions)
            answer.confidence = 0.0
            answer.steps = steps + ["Норм не найдено."]
            return answer

        if getattr(self.answerer, "synthesizes", False):
            answer = self.answerer.answer(question, provisions)
            verified, unverified = self._verify_synthesized(answer, provisions)
            answer.verified = verified
            answer.unverified_claims = unverified
            total = len(verified) + len(unverified)
            answer.confidence = round(len(verified) / total, 3) if total else 0.0
        else:
            # Оцениваем релевантность каждой нормы вопросу, отбрасываем шум и
            # оставляем хотя бы самую релевантную. Уверенность — по лучшей норме.
            scored = sorted(
                (
                    (r, self.verifier.verify(question, Citation(r.provision)))
                    for r in provisions
                ),
                key=lambda pair: pair[1].score,
                reverse=True,
            )
            # Относительный порог (шкало-независимо для эвристики и NLI): держим нормы
            # со скором не ниже доли от лучшего; иначе — хотя бы самую релевантную.
            top_score = scored[0][1].score
            threshold = max(cfg.relevance_floor, top_score * cfg.keep_ratio)
            kept = [(r, vc) for r, vc in scored if vc.score >= threshold] or scored[:1]
            answer = self.answerer.answer(question, [r for r, _ in kept])
            answer.verified = [vc for _, vc in kept]
            answer.confidence = round(max(vc.score for _, vc in kept), 3)

        supported = sum(1 for vc in answer.verified if vc.verdict == Verdict.SUPPORTS)
        answer.steps = steps + [
            f"Проверка цитат: норм в ответе {len(answer.citations)}, "
            f"подтверждают вопрос {supported}, без опоры {len(answer.unverified_claims)}."
        ]
        return answer

    def _reformulate(self, question: str, cands) -> str:
        titles = " ".join(dict.fromkeys(c.provision.article_title for c in cands[:3]))
        return f"{question} {titles}".strip() if titles else question

    def _verify_synthesized(self, answer: Answer, provisions):
        """Пер-тезисная проверка LLM-ответа: каждое предложение против норм."""
        verified = []
        unverified = []
        sentences = [
            s.strip() for s in _SENTENCE_RE.split(answer.text) if len(s.strip()) > 15
        ]
        for sentence in sentences:
            best = None
            for r in provisions:
                vc = self.verifier.verify(sentence, Citation(r.provision))
                if best is None or vc.score > best.score:
                    best = vc
            if best is not None and best.verdict == Verdict.SUPPORTS:
                verified.append(best)
            elif best is not None:
                unverified.append(sentence)
        return verified, unverified
