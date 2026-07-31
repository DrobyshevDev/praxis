"""Легал-aware чанкинг: режем по структурным единицам, а не по токенам.

Единица цитирования в праве — пункт/часть статьи. Поэтому одна норма (Provision) =
один пункт (или вся статья, если она без внутреннего деления). Это делает каждую
ссылку осмысленной и точной, а не «фрагмент №7 из документа».
"""

from __future__ import annotations

from ..core.models import Act, Provision
from .schema import RawAct


def build_provisions(raw: RawAct) -> list[Provision]:
    """Разворачивает сырой акт в плоский список цитируемых норм."""
    act = Act(
        id=raw.id,
        kind=raw.kind,
        title=raw.title,
        short_title=raw.short_title,
        number=raw.number,
        date=raw.date,
        edition=raw.edition,
    )

    provisions: list[Provision] = []
    position = 0
    for article in raw.articles:
        units: list[tuple[str, str]]
        if article.points:
            units = list(article.points)
        elif article.text:
            units = [("", article.text)]
        else:  # пустая статья — пропускаем
            continue

        for path, text in units:
            text = text.strip()
            if not text:
                continue
            key = _path_key(path) if path else "0"
            provisions.append(
                Provision(
                    id=f"{act.id}:{article.number}:{key}",
                    act=act,
                    article_number=article.number,
                    article_title=article.title,
                    path=path,
                    text=text,
                    position=position,
                    edition=act.edition,
                )
            )
            position += 1

    return provisions


def _path_key(path: str) -> str:
    """'п. 2' -> '2', 'ч. 1' -> '1'. Для стабильного id нормы."""
    digits = "".join(ch for ch in path if ch.isdigit())
    return digits or path.replace(" ", "_")
