"""Экстрактивный генератор — дефолт и «режим доверия».

Не синтезирует текст LLM, а дословно приводит применимые нормы с точными ссылками.
Плюс для юр-продукта: физически не может галлюцинировать — каждое слово ответа взято
из закона. Естественный надёжный baseline, поверх которого LLM-синтез опционален.
Итоговую `confidence` проставляет пайплайн после проверки цитат.
"""

from __future__ import annotations

from collections.abc import Sequence

from ..core.models import Answer, Citation, RetrievedProvision

_NO_MATCH = (
    "В доступном корпусе не нашлось применимых норм. Уточните вопрос "
    "или обратитесь к первоисточнику."
)


class ExtractiveAnswerer:
    """Реализует протокол `generate.base.Answerer`."""

    synthesizes = False  # текст дословно из закона — грунтован по построению

    def answer(
        self, question: str, provisions: Sequence[RetrievedProvision], top_k: int = 5
    ) -> Answer:
        top = list(provisions)[:top_k]
        if not top:
            return Answer(question=question, text=_NO_MATCH, confidence=0.0)

        citations = [Citation(r.provision) for r in top]
        lines = ["По вашему вопросу применимы следующие нормы:", ""]
        for r in top:
            p = r.provision
            lines.append(f"• {p.citation} — {p.article_title}:")
            lines.append(f"  {p.text}")
            lines.append("")
        return Answer(
            question=question,
            text="\n".join(lines).strip(),
            citations=citations,
            confidence=0.0,
        )
