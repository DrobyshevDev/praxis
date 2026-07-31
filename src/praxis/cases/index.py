"""Индекс «(акт, статья) → дела» и подбор практики по процитированным нормам."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from ..core.models import CaseDecision


def build_case_index(
    cases: Iterable[CaseDecision],
) -> dict[tuple[str, str], list[CaseDecision]]:
    """Ключ (act_id, статья) → дела, толкующие эту статью."""
    index: dict[tuple[str, str], list[CaseDecision]] = defaultdict(list)
    for case in cases:
        for article in case.cited_articles:
            index[(case.act_id, article)].append(case)
    return dict(index)


def related_cases(
    keys: Iterable[tuple[str, str]],
    index: dict[tuple[str, str], list[CaseDecision]],
    limit: int = 5,
) -> list[CaseDecision]:
    seen: set[str] = set()
    out: list[CaseDecision] = []
    for key in keys:
        for case in index.get(key, ()):
            if case.id not in seen:
                seen.add(case.id)
                out.append(case)
    return out[:limit]
