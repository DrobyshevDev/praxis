"""Парсер официального plaintext-текста кодекса/закона в структуру RawAct.

Реальный путь ингестии: официальный текст (pravo.gov.ru) → этот парсер → нормы.
Распознаёт заголовки «Статья N. Название» и нумерованные пункты «N. ...» с
многострочным телом. Абзацы без номера внутри статьи собираются в её общий текст.
"""

from __future__ import annotations

import re

from ..core.models import ActKind
from .schema import RawAct, RawArticle

_ARTICLE_RE = re.compile(r"^Статья\s+(\d+(?:\.\d+)?)\.\s*(.+)$")
_POINT_RE = re.compile(r"^(\d+)\.\s+(.*)$")


def parse_statute_text(
    text: str,
    *,
    id: str,
    title: str,
    short_title: str,
    kind: ActKind = ActKind.CODE,
    number: str | None = None,
    date: str | None = None,
    edition: str | None = None,
) -> RawAct:
    articles: list[RawArticle] = []
    art: dict | None = None

    def flush() -> None:
        if art is None:
            return
        if art["points"]:
            points = [(f"п. {num}", " ".join(lines).strip()) for num, lines in art["points"]]
            articles.append(RawArticle(number=art["number"], title=art["title"], points=points))
        else:
            body = " ".join(art["text"]).strip()
            articles.append(RawArticle(number=art["number"], title=art["title"], text=body or None))

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        m_article = _ARTICLE_RE.match(line)
        if m_article:
            flush()
            art = {
                "number": m_article.group(1),
                "title": m_article.group(2).strip(),
                "points": [],
                "text": [],
            }
            continue

        if art is None:
            continue  # преамбула до первой статьи — пропускаем

        m_point = _POINT_RE.match(line)
        if m_point:
            art["points"].append((m_point.group(1), [m_point.group(2)]))
        elif art["points"]:
            art["points"][-1][1].append(line)
        else:
            art["text"].append(line)

    flush()
    return RawAct(
        id=id,
        kind=kind,
        title=title,
        short_title=short_title,
        number=number,
        date=date,
        edition=edition,
        articles=articles,
    )
