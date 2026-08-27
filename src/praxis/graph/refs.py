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
# `[\d\s,и]*\d` (а не `+\d`): чтобы ловились и однозначные статьи (ст. 1–9).
_REF_RE = re.compile(r"стат[а-яё]{1,4}\s+([\d\s,и]*\d)", re.IGNORECASE)


def extract_references(text: str) -> set[str]:
    refs: set[str] = set()
    for m in _REF_RE.finditer(text):
        refs.update(re.findall(r"\d+", m.group(1)))
    return refs


# Маркер кодекса сразу после «статья N …» → act_id корпуса.
_CODE_MARKERS = [
    (re.compile(r"^\s*(?:ГК|Граждан)", re.I), "gk-rf"),
    (re.compile(r"^\s*(?:УК|Уголов)", re.I), "uk-rf"),
    (re.compile(r"^\s*(?:НК|Налог)", re.I), "nk-rf"),
    (re.compile(r"^\s*(?:ТК|Трудов)", re.I), "tk-rf"),
    (re.compile(r"^\s*(?:КоАП|административн\w+ правонаруш)", re.I), "koap-rf"),
    (re.compile(r"^\s*(?:ЖК|Жилищн)", re.I), "zhk-rf"),
    (re.compile(r"^\s*(?:Закона[^.]{0,40}защит[еы] прав потреб|о защите прав потреб)", re.I), "zozpp"),
]
# Кодексы не из корпуса (процессуальные и пр.) — ссылки на них отбрасываем как шум.
_SKIP_MARKER = re.compile(
    r"^\s*(?:ГПК|АПК|УПК|КАС|Конституц|конституционн|Бюджетн|Земельн|Семейн|"
    r"Воздушн|Таможен|Лесн|Водн|Градостроит|процессуальн)", re.I
)


def extract_references_by_act(text: str, default_act_id: str | None = None) -> set[tuple[str, str]]:
    """Ссылки «статья N <Кодекс>» → множество (act_id, номер статьи).

    Кодекс определяется по маркеру сразу после номеров: «статья 10 ГК РФ» → gk-rf.
    Ссылки на кодексы не из корпуса (ГПК, АПК, Конституция…) отбрасываются, чтобы
    «статья 65 АПК» не осела ошибочно в ГК. Если маркера нет — берётся `default_act_id`
    (напр. кодекс, которому посвящён Пленум); при `None` такие ссылки пропускаются.
    """
    out: set[tuple[str, str]] = set()
    for m in _REF_RE.finditer(text):
        nums = re.findall(r"\d+", m.group(1))
        tail = text[m.end():m.end() + 40]
        if _SKIP_MARKER.match(tail):
            continue
        act = default_act_id
        for rx, aid in _CODE_MARKERS:
            if rx.match(tail):
                act = aid
                break
        if act is None:
            continue
        for n in nums:
            out.add((act, n))
    return out


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
