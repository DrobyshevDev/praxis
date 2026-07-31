"""Anthropic Claude — реальный LLM-провайдер (opt-in). Extra `llm`.

Включается, когда задан ANTHROPIC_API_KEY. Дефолтная модель — claude-sonnet-5
(баланс качества/латентности/цены для продукта); можно переопределить. Ленивая
инициализация клиента.
"""

from __future__ import annotations

import os


class AnthropicClient:
    def __init__(
        self,
        model: str = "claude-sonnet-5",
        api_key: str | None = None,
        max_tokens: int = 1024,
    ) -> None:
        self.model = model
        self.max_tokens = max_tokens
        self._api_key = api_key
        self._client = None

    def _ensure(self):
        if self._client is None:
            import anthropic

            key = self._api_key or os.environ.get("ANTHROPIC_API_KEY")
            if not key:
                raise RuntimeError("ANTHROPIC_API_KEY не задан")
            self._client = anthropic.Anthropic(api_key=key)
        return self._client

    def complete(
        self, prompt: str, *, system: str | None = None, max_tokens: int | None = None
    ) -> str:
        client = self._ensure()
        message = client.messages.create(
            model=self.model,
            max_tokens=max_tokens or self.max_tokens,
            system=system or "",
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(
            block.text for block in message.content if getattr(block, "type", "") == "text"
        )
