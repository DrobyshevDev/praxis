"""Контракт LLM-провайдера. Реализации: Anthropic Claude, Mock (детерминированный)."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class LLMClient(Protocol):
    def complete(
        self, prompt: str, *, system: str | None = None, max_tokens: int | None = None
    ) -> str: ...
