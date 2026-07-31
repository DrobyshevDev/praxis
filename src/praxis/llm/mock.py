"""Детерминированный LLM-заглушка для тестов/оффлайна (без сети)."""

from __future__ import annotations


class MockLLM:
    def __init__(self, reply: str = "Ответ на основе приведённых норм [1].") -> None:
        self.reply = reply
        self.last_prompt: str | None = None

    def complete(
        self, prompt: str, *, system: str | None = None, max_tokens: int | None = None
    ) -> str:
        self.last_prompt = prompt
        return self.reply
