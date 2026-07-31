"""Генерация ответа: экстрактивный (дефолт) + LLM-синтез (opt-in)."""

from .base import Answerer
from .extractive import ExtractiveAnswerer
from .llm_answerer import LLMAnswerer

__all__ = ["Answerer", "ExtractiveAnswerer", "LLMAnswerer", "default_answerer"]


def default_answerer() -> Answerer:
    """LLM-синтез, если доступен провайдер (ANTHROPIC_API_KEY); иначе экстрактивный."""
    from ..llm import default_llm

    client = default_llm()
    if client is not None:
        return LLMAnswerer(client)
    return ExtractiveAnswerer()
