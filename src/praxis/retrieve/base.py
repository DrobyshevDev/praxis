"""Контракты слоя поиска. Baseline v0 — BM25; v1 добавит dense, fusion, rerank."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ..core.models import Provision, RetrievedProvision


@runtime_checkable
class Retriever(Protocol):
    """Любой ретривер отдаёт отранжированные нормы под запрос."""

    def search(self, query: str, top_k: int = 5) -> list[RetrievedProvision]: ...


@runtime_checkable
class Reranker(Protocol):
    """Cross-encoder переранжирование топ-N кандидатов (v1: bge-reranker-v2-m3)."""

    def rerank(
        self, query: str, candidates: list[RetrievedProvision], top_k: int = 5
    ) -> list[RetrievedProvision]: ...


def reciprocal_rank_fusion(
    runs: list[list[RetrievedProvision]], k: int = 60, top_k: int = 10
) -> list[RetrievedProvision]:
    """RRF-слияние нескольких прогонов (BM25 + dense) в один список.

    Используется гибридным ретривером v1. Вынесено сюда, потому что не зависит от
    конкретных ретриверов и легко тестируется.
    """
    scores: dict[str, float] = {}
    best: dict[str, RetrievedProvision] = {}
    for run in runs:
        for rank, item in enumerate(run):
            pid = item.provision.id
            scores[pid] = scores.get(pid, 0.0) + 1.0 / (k + rank + 1)
            best.setdefault(pid, item)
    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    out: list[RetrievedProvision] = []
    for pid, score in ranked[:top_k]:
        prov: Provision = best[pid].provision
        out.append(RetrievedProvision(provision=prov, score=score, method="hybrid"))
    return out
