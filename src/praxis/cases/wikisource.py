"""Выгрузка судебной практики (Постановления Пленума ВС РФ) с Викитеки — по пунктам.

Пленумы ВС — авторитетное толкование норм. Каждый пункт постановления разъясняет
конкретные статьи с конкретным тезисом, поэтому практику разбираем **до пункта**: одна
единица практики = один пункт Пленума со своим тезисом и статьями, которые он толкует.
Тогда граф «норма → практика» ведёт не на постановление целиком, а на релевантный пункт.

Набор Пленумов на Викитеке узкий (по сути ГК и УК); полноценная практика РФ (Обзоры ВС по
подстраницам, отдельные Определения — kad.arbitr, ГАС «Правосудие») — отдельный тяжёлый
пайплайн и главный ров проекта.
"""

from __future__ import annotations

import re

from ..core.models import CaseDecision
from ..graph.refs import extract_references_by_act
from ..ingest.sources.wikisource import clean_wikitext, fetch_wikitext

# (id, заголовок на Викитеке, номер, дата, act_id толкуемого кодекса)
PLENUMS = [
    (
        "plenum-vs-25-2015",
        "Постановление Пленума Верховного Суда РФ от 23.06.2015 № 25",
        "№ 25",
        "2015-06-23",
        "gk-rf",
    ),
    (
        "plenum-vs-11-2011",
        "Постановление Пленума Верховного Суда РФ от 28.06.2011 № 11",
        "№ 11",
        "2011-06-28",
        "uk-rf",
    ),
]

_POINT_RE = re.compile(r"^(\d+)\.\s+(.*)")
# Пункт, ссылающийся на слишком много статей, — это перечисление/вводная рамка, а не
# точечное толкование; такие пропускаем, чтобы не зашумлять граф «норма → пункт».
_MAX_ARTICLES = 6


def parse_plenum_points(text: str) -> list[tuple[int, str]]:
    """Разбить текст постановления на пункты: строка «N. …» открывает пункт,
    последующие строки без номера — его продолжение."""
    points: list[tuple[int, str]] = []
    num: int | None = None
    body: list[str] = []
    for line in text.split("\n"):
        m = _POINT_RE.match(line)
        if m:
            if num is not None:
                points.append((num, " ".join(body).strip()))
            num = int(m.group(1))
            body = [m.group(2)]
        elif num is not None:
            body.append(line)
    if num is not None:
        points.append((num, " ".join(body).strip()))
    return points


def _tezis(body: str, cap: int = 280) -> str:
    """Краткий тезис пункта: до границы предложения в пределах cap."""
    body = " ".join(body.split())
    if len(body) <= cap:
        return body
    cut = body[:cap]
    dot = cut.rfind(". ")
    return cut[: dot + 1] if dot > 120 else cut.rstrip() + "…"


def fetch_practice() -> list[CaseDecision]:
    cases: list[CaseDecision] = []
    for cid, title, number, date, act_id in PLENUMS:
        text = clean_wikitext(fetch_wikitext(title))
        for point_num, body in parse_plenum_points(text):
            refs = extract_references_by_act(body, default_act_id=act_id)
            # оставляем статьи толкуемого кодекса — ключ индекса (act_id, статья).
            articles = frozenset(n for a, n in refs if a == act_id)
            if not articles or len(articles) > _MAX_ARTICLES:
                continue
            cases.append(
                CaseDecision(
                    id=f"{cid}-p{point_num}",
                    court="Пленум ВС РФ",
                    number=f"{number}, п. {point_num}",
                    date=date,
                    summary=_tezis(body),
                    act_id=act_id,
                    cited_articles=articles,
                )
            )
    return cases
