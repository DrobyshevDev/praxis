"""Промежуточный формат сырого акта до нарезки на нормы.

Реальный пайплайн (v1) будет получать это из официальных машиночитаемых текстов
(pravo.gov.ru): парсер структуры → RawAct → chunker → list[Provision].
На v0 тем же контрактом пользуется образец корпуса.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..core.models import ActKind


@dataclass
class RawArticle:
    """Статья до нарезки. Либо цельный `text`, либо разбита на `points`."""

    number: str
    title: str
    text: str | None = None
    points: list[tuple[str, str]] = field(default_factory=list)  # (path, text)


@dataclass
class RawAct:
    """Сырой акт: метаданные + список статей."""

    id: str
    kind: ActKind
    title: str
    short_title: str
    articles: list[RawArticle]
    number: str | None = None
    date: str | None = None
    edition: str | None = None
