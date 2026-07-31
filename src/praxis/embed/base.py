"""Контракт эмбеддера. Реализации: BGE-M3 (реальная, GPU) и hashing (fallback)."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, runtime_checkable


@runtime_checkable
class Embedder(Protocol):
    """Кодирует тексты в плотные векторы фиксированной размерности."""

    dim: int

    def embed(self, texts: Sequence[str]) -> list[list[float]]: ...

    def embed_query(self, text: str) -> list[float]: ...
