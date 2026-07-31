"""Self-RAG на glia — реальное использование библиотеки glia (DrobyshevDev).

Здесь поиск норм оформлен как glia-инструмент `search_law`, а весь цикл ведёт
glia.Agent: модель сама решает, что искать, вызывает инструмент по корпусу Praxis и
отвечает со ссылками. Трейс рассуждения берём из glia-trajectory (glass-box), а не пишем
руками. Ответ проходит ту же пер-тезисную проверку Citation Verifier.

Путь включается, когда доступен LLM-провайдер (ANTHROPIC_API_KEY) и установлена glia; без
ключа пайплайн остаётся на детерминированном SelfRAG. Тестируется оффлайн со scripted
glia.providers.EchoLLM — без сети и ключей.
"""

from __future__ import annotations

import asyncio
import re

from ..core.models import Answer, Citation, Verdict
from ..retrieve.base import Reranker, Retriever
from ..span import find_support_span
from ..verify.base import CitationVerifier

_SYSTEM = (
    "Ты — юридический ассистент по праву РФ. Обязательно вызови инструмент search_law, "
    "чтобы найти применимые нормы, и отвечай СТРОГО по найденному, ссылаясь на статьи так "
    "же, как в источнике (например, «ст. 159 УК РФ»). Не выдумывай нормы и номера статей."
)
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


class GliaLegalAgent:
    """Реализует контракт пайплайна: `.answer(question) -> Answer`, `.retriever`."""

    def __init__(
        self,
        llm,
        retriever: Retriever,
        verifier: CitationVerifier,
        reranker: Reranker | None = None,
        *,
        top_k: int = 6,
        max_steps: int = 6,
    ) -> None:
        self.llm = llm
        self.retriever = retriever
        self.verifier = verifier
        self.reranker = reranker
        self.top_k = top_k
        self.max_steps = max_steps

    def answer(self, question: str) -> Answer:
        return asyncio.run(self._run(question))

    async def _run(self, question: str) -> Answer:
        from glia import Agent, tool

        found: dict = {}  # provision.id -> Provision (накопление по всем вызовам поиска)

        @tool
        async def search_law(query: str) -> str:
            """Найти применимые нормы права РФ по запросу (поиск по корпусу)."""
            hits = self.retriever.search(query, top_k=self.top_k * 3)
            if self.reranker is not None:
                hits = self.reranker.rerank(query, hits, top_k=self.top_k)
            else:
                hits = hits[: self.top_k]
            lines = []
            for h in hits:
                found[h.provision.id] = h.provision
                lines.append(f"[{h.provision.citation}] {h.provision.article_title}: {h.provision.text}")
            return "\n".join(lines) if lines else "Ничего не найдено."

        agent = Agent(self.llm, tools=[search_law], system=_SYSTEM, max_steps=self.max_steps)
        result = await agent.run(question)
        text = (result.output or "").strip()

        used = [p for p in found.values() if p.citation in text] or list(found.values())[: self.top_k]

        # Пер-тезисная проверка синтезированного ответа против найденных норм.
        verified, unverified = [], []
        for sentence in [s.strip() for s in _SENTENCE_RE.split(text) if len(s.strip()) > 15]:
            best = None
            for p in used:
                vc = self.verifier.verify(sentence, Citation(p))
                if best is None or vc.score > best.score:
                    best = vc
            if best is not None and best.verdict == Verdict.SUPPORTS:
                verified.append(best)
            elif best is not None:
                unverified.append(sentence)

        citations = [Citation(p, span=find_support_span(question, p.text)) for p in used]
        total = len(verified) + len(unverified)
        confidence = round(len(verified) / total, 3) if total else 0.0
        return Answer(
            question=question,
            text=text,
            citations=citations,
            verified=verified,
            unverified_claims=unverified,
            confidence=confidence,
            steps=self._trace(result),
        )

    def _trace(self, result) -> list[str]:
        """Человекочитаемый трейс из glia-trajectory (glass-box)."""
        steps: list[str] = []
        for e in result.trajectory.events:
            if e.kind == "tool_called":
                steps.append(f"glia · инструмент search_law(«{e.arguments.get('query', '')}»)")
            elif e.kind == "tool_returned":
                n = 0 if e.content == "Ничего не найдено." else e.content.count("\n") + 1
                steps.append(f"glia · найдено норм: {n}")
            elif e.kind == "model_response" and e.text:
                steps.append("glia · модель сформулировала ответ по нормам")
        return steps or [f"glia · шагов агента: {result.steps}"]
