"""Детерминированный hashing-эмбеддер — dev/fallback без зависимостей.

Bag-of-words с хэш-проекцией в фиксированную размерность и L2-нормировкой. Семантики
как у BGE-M3 не даёт (это не нейросеть), но детерминирован, мгновенный и позволяет
тестировать/демонстрировать весь dense+hybrid пайплайн без скачивания моделей и GPU.
Реальную семантику включает `BGEM3Embedder` (extra `ml`).
"""

from __future__ import annotations

import hashlib
import math
from collections.abc import Sequence

from ..retrieve.bm25 import tokenize


class HashingEmbedder:
    dim: int

    def __init__(self, dim: int = 256) -> None:
        self.dim = dim

    def _vector(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for tok in tokenize(text):
            h = int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dim
            sign = 1.0 if (h // self.dim) % 2 == 0 else -1.0
            vec[idx] += sign
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        return [self._vector(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vector(text)
