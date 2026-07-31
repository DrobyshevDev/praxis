"""Индекс «норма → дела» и подбор практики по процитированным статьям."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from ..core.models import CaseDecision


def build_case_index(cases: Iterable[CaseDecision]) -> dict[str, list[CaseDecision]]:
    index: dict[str, list[CaseDecision]] = defaultdict(list)
    for case in cases:
        for article in case.cited_articles:
            index[article].append(case)
    return dict(index)


def related_cases(
    article_numbers: Iterable[str],
    index: dict[str, list[CaseDecision]],
    limit: int = 5,
) -> list[CaseDecision]:
    seen: set[str] = set()
    out: list[CaseDecision] = []
    for article in article_numbers:
        for case in index.get(article, ()):
            if case.id not in seen:
                seen.add(case.id)
                out.append(case)
    return out[:limit]
