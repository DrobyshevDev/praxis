"""LLM-провайдеры: Claude (реальный, opt-in) + Mock (детерминированный)."""

from __future__ import annotations

import os

from .base import LLMClient
from .mock import MockLLM

__all__ = ["LLMClient", "MockLLM", "default_glia_llm", "default_llm"]


def default_glia_llm():
    """glia-провайдер Claude, если задан ключ и установлены glia+anthropic; иначе None.

    Используется агентным путём на glia (см. agent.glia_agent). Без ключа/glia — None,
    и пайплайн остаётся на детерминированном SelfRAG.
    """
    from ..runtime import is_offline

    if is_offline() or not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    try:
        from glia.providers import ClaudeLLM

        return ClaudeLLM()
    except Exception:
        return None


def default_llm() -> LLMClient | None:
    """Claude, если задан ANTHROPIC_API_KEY и установлен SDK; иначе None.

    None означает «работаем без LLM» — генератор откатывается на экстрактивный
    (дословные цитаты, ноль галлюцинаций).
    """
    from ..runtime import is_offline

    if is_offline() or not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    try:
        from .anthropic_client import AnthropicClient

        return AnthropicClient()
    except Exception:
        return None
