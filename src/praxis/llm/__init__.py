"""LLM-провайдеры: Claude (реальный, opt-in) + Mock (детерминированный)."""

from __future__ import annotations

import os

from .base import LLMClient
from .mock import MockLLM

__all__ = ["LLMClient", "MockLLM", "default_llm"]


def default_llm() -> LLMClient | None:
    """Claude, если задан ANTHROPIC_API_KEY и установлен SDK; иначе None.

    None означает «работаем без LLM» — генератор откатывается на экстрактивный
    (дословные цитаты, ноль галлюцинаций).
    """
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    try:
        from .anthropic_client import AnthropicClient

        return AnthropicClient()
    except Exception:
        return None
