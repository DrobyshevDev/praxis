"""Ingestion: сырые акты → нормализация → легал-aware чанкинг → нормы."""

from __future__ import annotations

from ..core.models import Provision
from .chunker import build_provisions
from .schema import RawAct, RawArticle
from .sources import SAMPLE_ACTS
from .sources.json_loader import act_from_dict, load_act_json
from .statute_parser import parse_statute_text


def load_sample_provisions() -> list[Provision]:
    """Загружает образец корпуса (v0) в плоский список цитируемых норм."""
    provisions: list[Provision] = []
    for raw in SAMPLE_ACTS:
        provisions.extend(build_provisions(raw))
    return provisions


__all__ = [
    "RawAct",
    "RawArticle",
    "act_from_dict",
    "build_provisions",
    "load_act_json",
    "load_sample_provisions",
    "parse_statute_text",
]
