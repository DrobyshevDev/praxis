"""Загрузка корпуса из JSON — формат для «drop-in» реальных данных.

    {
      "id": "gk-rf-1", "kind": "кодекс", "title": "...", "short_title": "ГК РФ",
      "number": "51-ФЗ", "date": "1994-11-30", "edition": "...",
      "articles": [
        {"number": "421", "title": "Свобода договора",
         "points": [["п. 1", "..."], ["п. 4", "..."]]},
        {"number": "309", "title": "...", "text": "..."}
      ]
    }
"""

from __future__ import annotations

import json
from pathlib import Path

from ...core.models import ActKind
from ..schema import RawAct, RawArticle


def act_from_dict(data: dict) -> RawAct:
    articles = [
        RawArticle(
            number=str(a["number"]),
            title=a["title"],
            text=a.get("text"),
            points=[(str(p[0]), str(p[1])) for p in a.get("points", [])],
        )
        for a in data.get("articles", [])
    ]
    return RawAct(
        id=data["id"],
        kind=ActKind(data.get("kind", "иное")),
        title=data["title"],
        short_title=data["short_title"],
        number=data.get("number"),
        date=data.get("date"),
        edition=data.get("edition"),
        articles=articles,
    )


def load_act_json(path: str | Path) -> RawAct:
    with open(path, encoding="utf-8") as f:
        return act_from_dict(json.load(f))
