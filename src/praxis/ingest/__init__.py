"""Ingestion: сырые акты → нормализация → легал-aware чанкинг → нормы."""

from __future__ import annotations

from ..core.models import Provision
from .chunker import build_provisions
from .schema import RawAct, RawArticle
from .sources import SAMPLE_ACTS


def load_sample_provisions() -> list[Provision]:
    """Загружает образец корпуса (v0) в плоский список цитируемых норм."""
    provisions: list[Provision] = []
    for raw in SAMPLE_ACTS:
        provisions.extend(build_provisions(raw))
    return provisions


__all__ = [
    "RawAct",
    "RawArticle",
    "build_provisions",
    "load_sample_provisions",
]
