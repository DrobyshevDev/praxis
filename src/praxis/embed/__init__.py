"""Слой эмбеддингов: BGE-M3 (реальный) + hashing (детерминированный fallback)."""

from .base import Embedder
from .hashing import HashingEmbedder

__all__ = ["Embedder", "HashingEmbedder"]


def default_embedder() -> Embedder:
    """BGE-M3, если доступны ML-зависимости; иначе детерминированный hashing."""
    from ..runtime import is_offline

    if is_offline():
        return HashingEmbedder()
    try:
        import sentence_transformers  # noqa: F401
        import torch  # noqa: F401

        from .bge_m3 import BGEM3Embedder

        return BGEM3Embedder()
    except Exception:
        return HashingEmbedder()
