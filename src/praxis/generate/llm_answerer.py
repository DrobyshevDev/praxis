"""LLM-генератор: синтез ответа СТРОГО поверх приведённых норм.

Промпт жёстко ограничивает модель предоставленным контекстом и требует ссылок в
формате [n]. Пер-тезисную проверку сгенерированного текста против норм делает пайплайн
через Citation Verifier — неподтверждённые утверждения не попадают в факты.
"""

from __future__ import annotations

from collections.abc import Sequence

from ..core.models import Answer, Citation, RetrievedProvision
from ..llm.base import LLMClient

_SYSTEM = (
    "Ты — юридический ассистент по праву РФ. Отвечай СТРОГО на основе приведённых норм. "
    "Каждое утверждение опирай на конкретную норму и ссылайся на неё в формате [n]. "
    "Если предоставленных норм недостаточно — прямо скажи, что ответа в материалах нет. "
    "Категорически не выдумывай нормы, номера статей и реквизиты."
)

_NO_MATCH = "В предоставленных материалах нет применимых норм для ответа на вопрос."


class LLMAnswerer:
    """Реализует протокол `generate.base.Answerer`."""

    synthesizes = True  # текст синтезирован — каждый тезис проверяется отдельно

    def __init__(self, client: LLMClient) -> None:
        self.client = client

    def answer(
        self, question: str, provisions: Sequence[RetrievedProvision], top_k: int = 5
    ) -> Answer:
        top = list(provisions)[:top_k]
        if not top:
            return Answer(question=question, text=_NO_MATCH, confidence=0.0)

        context = "\n\n".join(
            f"[{i + 1}] {r.provision.citation} — {r.provision.article_title}\n{r.provision.text}"
            for i, r in enumerate(top)
        )
        prompt = (
            f"Вопрос: {question}\n\n"
            f"Применимые нормы:\n{context}\n\n"
            "Дай краткий ответ по существу, ссылаясь на нормы в формате [n]."
        )
        text = self.client.complete(prompt, system=_SYSTEM)
        citations = [Citation(r.provision) for r in top]
        return Answer(
            question=question, text=text.strip(), citations=citations, confidence=0.0
        )
