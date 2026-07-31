"""Метрики качества ретривера и ответа (детерминированные, без LLM).

Ретривер: recall@k, precision@k, MRR по номерам релевантных статей.
Ответ: citation precision (доля процитированных статей, что реально релевантны),
hit (попал ли хоть раз). Faithfulness (RAGAS) требует LLM — хук в runner, по умолчанию
считаем то, что можно посчитать честно и офлайн.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence


def dedupe(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def recall_at_k(ranked: Sequence[str], relevant: Iterable[str], k: int = 5) -> float:
    rel = set(relevant)
    if not rel:
        return 0.0
    return len(set(ranked[:k]) & rel) / len(rel)


def precision_at_k(ranked: Sequence[str], relevant: Iterable[str], k: int = 5) -> float:
    top = ranked[:k]
    if not top:
        return 0.0
    return len(set(top) & set(relevant)) / len(top)


def mrr(ranked: Sequence[str], relevant: Iterable[str]) -> float:
    rel = set(relevant)
    for i, article in enumerate(ranked, start=1):
        if article in rel:
            return 1.0 / i
    return 0.0


def citation_precision(cited: Sequence[str], relevant: Iterable[str]) -> float:
    if not cited:
        return 0.0
    return len(set(cited) & set(relevant)) / len(cited)
