"""Гибридный ретривер: RRF-слияние BM25 (лексика) и dense (семантика).

Продакшн-база 2026: BM25 ловит точные формулировки и номера статей, dense — смысл и
синонимы. Слияние Reciprocal Rank Fusion устойчиво к разным шкалам скоров.
"""

from __future__ import annotations

from ..core.models import RetrievedProvision
from .base import Retriever, reciprocal_rank_fusion


class HybridRetriever:
    """Реализует протокол `retrieve.base.Retriever`."""

    def __init__(self, bm25: Retriever, dense: Retriever, rrf_k: int = 60) -> None:
        self.bm25 = bm25
        self.dense = dense
        self.rrf_k = rrf_k

    def search(
        self, query: str, top_k: int = 5, pool: int = 20
    ) -> list[RetrievedProvision]:
        runs = [
            self.bm25.search(query, top_k=pool),
            self.dense.search(query, top_k=pool),
        ]
        return reciprocal_rank_fusion(runs, k=self.rrf_k, top_k=top_k)
