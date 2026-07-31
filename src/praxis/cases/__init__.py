"""Судебная практика и граф «норма ↔ дело».

Реальная практика — Постановления Пленума ВС РФ (см. wikisource.py), выгружается в
corpus/practice.json. Если файла нет — образец (для тестов/офлайна).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from ..core.models import CaseDecision
from .index import build_case_index, related_cases
from .sample import SAMPLE_CASES

__all__ = ["SAMPLE_CASES", "build_case_index", "load_practice", "related_cases"]


def load_practice() -> list[CaseDecision]:
    """Реальная практика из corpus/practice.json (если задан PRAXIS_CORPUS_DIR); иначе образец."""
    corpus_dir = os.environ.get("PRAXIS_CORPUS_DIR")
    if corpus_dir:
        path = Path(corpus_dir) / "practice.json"
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            return [
                CaseDecision(
                    id=d["id"],
                    court=d["court"],
                    number=d["number"],
                    date=d["date"],
                    summary=d["summary"],
                    act_id=d.get("act_id", ""),
                    cited_articles=frozenset(d.get("cited_articles", [])),
                )
                for d in data
            ]
    return SAMPLE_CASES
