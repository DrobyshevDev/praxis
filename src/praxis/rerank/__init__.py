"""Reranking: cross-encoder BGE (реальный) + лексический fallback."""

from ..retrieve.base import Reranker
from .lexical import LexicalReranker

__all__ = ["LexicalReranker", "Reranker", "default_reranker"]


def default_reranker() -> Reranker:
    """BGE cross-encoder, если доступны ML-зависимости; иначе лексический."""
    from ..runtime import is_offline

    if is_offline():
        return LexicalReranker()
    try:
        import sentence_transformers  # noqa: F401
        import torch  # noqa: F401

        from .bge import BGEReranker

        return BGEReranker()
    except Exception:
        return LexicalReranker()
