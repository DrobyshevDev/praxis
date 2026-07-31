"""Извлечение перекрёстных ссылок между нормами и построение графа «норма→норма».

В праве нормы ссылаются друг на друга («в соответствии со статьёй 15», «(статья 422)»).
Это готовый граф знаний — не нужно строить искусственно. Парсим номера статей из текста
норм и получаем рёбра для GraphRAG (multi-hop поиск по цепочкам ссылок).
"""

from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Iterable

from ..core.models import Provision

# «статья/статьи/статьёй/статьями … <номера>» → номера упомянутых статей.
_REF_RE = re.compile(r"стат[а-яё]{1,4}\s+([\d\s,и]+\d)", re.IGNORECASE)


def extract_references(text: str) -> set[str]:
    refs: set[str] = set()
    for m in _REF_RE.finditer(text):
        refs.update(re.findall(r"\d+", m.group(1)))
    return refs


def build_reference_graph(
    provisions: Iterable[Provision],
) -> dict[tuple[str, str], set[tuple[str, str]]]:
    """Граф ссылок с привязкой к акту: (act_id, статья) → {(act_id, упомянутая статья)}.

    Ключ включает акт, иначе при нескольких кодексах «статья 15» в ГК ошибочно
    связалась бы со ст. 15 ТК. Ссылки считаем внутри того же акта («настоящего Кодекса»).
    """
    graph: dict[tuple[str, str], set[tuple[str, str]]] = defaultdict(set)
    for p in provisions:
        key = (p.act.id, p.article_number)
        for ref in extract_references(p.text):
            if ref != p.article_number:
                graph[key].add((p.act.id, ref))
    return dict(graph)
