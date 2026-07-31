"""Ingestion: сырые акты → нормализация → легал-aware чанкинг → нормы."""

from __future__ import annotations

from ..core.models import Provision
from .chunker import build_provisions
from .schema import RawAct, RawArticle
from .sources import SAMPLE_ACTS
from .sources.json_loader import act_from_dict, load_act_json
from .statute_parser import parse_statute_text


def load_sample_provisions() -> list[Provision]:
    """Нормы корпуса. Если задан PRAXIS_CORPUS_DIR — грузим оттуда, иначе образец."""
    import os

    corpus_dir = os.environ.get("PRAXIS_CORPUS_DIR")
    if corpus_dir:
        from .corpus import load_corpus_dir

        acts = load_corpus_dir(corpus_dir)
    else:
        acts = SAMPLE_ACTS

    provisions: list[Provision] = []
    for raw in acts:
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
