"""Плотный (семантический) ретривер поверх любого Embedder.

Хранит векторы норм в памяти и ищет по косинусной близости — этого достаточно для
dev/демо на небольшом корпусе. Продакшн-путь — pgvector (см. index/schema.sql), туда
те же векторы кладутся с HNSW-индексом.
"""

from __future__ import annotations

import math
from collections.abc import Iterable

from ..core.models import Provision, RetrievedProvision
from ..embed.base import Embedder


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


class DenseRetriever:
    """Реализует протокол `retrieve.base.Retriever`."""

    def __init__(self, provisions: Iterable[Provision], embedder: Embedder) -> None:
        self.provisions: list[Provision] = list(provisions)
        self.embedder = embedder
        texts = [f"{p.article_title}. {p.text}" for p in self.provisions]
        self._vectors: list[list[float]] = embedder.embed(texts) if texts else []

    def search(self, query: str, top_k: int = 5) -> list[RetrievedProvision]:
        if not self._vectors:
            return []
        q = self.embedder.embed_query(query)
        scored = [(i, _cosine(q, v)) for i, v in enumerate(self._vectors)]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [
            RetrievedProvision(self.provisions[i], score=s, method="dense")
            for i, s in scored[:top_k]
        ]
