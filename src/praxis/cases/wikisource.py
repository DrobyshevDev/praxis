"""Выгрузка судебной практики (Постановления Пленума ВС РФ) с Викитеки.

Пленумы ВС — авторитетное толкование норм: каждый ссылается на десятки статей кодекса.
Извлекаем эти ссылки и строим реальный граф «норма → практика». Данные настоящие, но
набор на Викитеке узкий; полноценная практика РФ (kad.arbitr, ГАС «Правосудие») — отдельный
тяжёлый пайплайн, и это главный ров проекта.
"""

from __future__ import annotations

from ..core.models import CaseDecision
from ..graph.refs import extract_references
from ..ingest.sources.wikisource import clean_wikitext, fetch_wikitext

# (id, заголовок на Викитеке, номер, дата, act_id толкуемого кодекса, краткое описание)
PLENUMS = [
    (
        "plenum-vs-25-2015",
        "Постановление Пленума Верховного Суда РФ от 23.06.2015 № 25",
        "№ 25",
        "2015-06-23",
        "gk-rf",
        "О применении судами раздела I части первой ГК РФ: основные положения, лица, "
        "объекты, сделки, представительство, сроки, злоупотребление правом.",
    ),
    (
        "plenum-vs-11-2011",
        "Постановление Пленума Верховного Суда РФ от 28.06.2011 № 11",
        "№ 11",
        "2011-06-28",
        "uk-rf",
        "О судебной практике по уголовным делам о преступлениях экстремистской направленности.",
    ),
]


def fetch_practice() -> list[CaseDecision]:
    cases: list[CaseDecision] = []
    for cid, title, number, date, act_id, summary in PLENUMS:
        text = clean_wikitext(fetch_wikitext(title))
        refs = extract_references(text)
        cases.append(
            CaseDecision(
                id=cid,
                court="Пленум ВС РФ",
                number=number,
                date=date,
                summary=summary,
                act_id=act_id,
                cited_articles=frozenset(refs),
            )
        )
    return cases
