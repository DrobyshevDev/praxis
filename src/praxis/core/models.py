"""Доменные модели Praxis.

Право моделируется как структура **Акт → Статья → Норма (Provision) → Цитата**.

Ключевое решение: минимальная единица поиска и цитирования — `Provision`
(пункт/часть/абзац статьи), а не абстрактный «чанк на N токенов». В праве ссылаются
на «ст. 431 ГК РФ, п. 2» — и модель данных отражает это напрямую, чтобы цитата была
осмысленной и проверяемой.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ActKind(str, Enum):
    CODE = "кодекс"
    FEDERAL_LAW = "фз"
    CONSTITUTION = "конституция"
    OTHER = "иное"


@dataclass(frozen=True)
class Act:
    """Нормативный акт (кодекс, ФЗ, ...)."""

    id: str  # напр. "gk-rf-1"
    kind: ActKind
    title: str  # "Гражданский кодекс Российской Федерации (часть первая)"
    short_title: str  # "ГК РФ"
    number: str | None = None  # "51-ФЗ"
    date: str | None = None  # дата принятия
    edition: str | None = None  # редакция / дата актуальности текста


@dataclass(frozen=True)
class Provision:
    """Норма — минимальная цитируемая единица (пункт/часть/абзац статьи)."""

    id: str  # "gk-rf-1:431:2"
    act: Act
    article_number: str  # "431"
    article_title: str  # "Толкование договора"
    path: str  # "п. 2" ("" если статья без внутреннего деления)
    text: str
    position: int  # порядок следования (для стабильной сортировки)
    edition: str | None = None

    @property
    def citation(self) -> str:
        """Человекочитаемая ссылка, напр. 'ст. 431 ГК РФ, п. 2'."""
        base = f"ст. {self.article_number} {self.act.short_title}"
        return f"{base}, {self.path}" if self.path else base


@dataclass(frozen=True)
class Citation:
    """Привязка утверждения к конкретной норме и (опционально) к span-у в её тексте."""

    provision: Provision
    span: tuple[int, int] | None = None  # смещения [начало, конец) в тексте нормы

    @property
    def quoted(self) -> str:
        if self.span is not None:
            start, end = self.span
            return self.provision.text[start:end]
        return self.provision.text

    def __str__(self) -> str:
        return self.provision.citation


@dataclass
class RetrievedProvision:
    """Норма, поднятая ретривером, со скором и меткой метода."""

    provision: Provision
    score: float
    method: str  # "bm25" | "dense" | "hybrid" | "rerank"


class Verdict(str, Enum):
    """Итог проверки Citation Verifier: подтверждает ли норма тезис."""

    SUPPORTS = "подтверждает"
    UNRELATED = "не относится"
    CONTRADICTS = "противоречит"


@dataclass
class VerifiedClaim:
    """Тезис ответа с привязанной цитатой и вердиктом проверки."""

    claim: str
    citation: Citation
    verdict: Verdict
    score: float


@dataclass
class Answer:
    """Итоговый ответ: только проверенные тезисы попадают в text как факты."""

    question: str
    text: str
    citations: list[Citation] = field(default_factory=list)
    verified: list[VerifiedClaim] = field(default_factory=list)
    unverified_claims: list[str] = field(default_factory=list)
    confidence: float = 0.0
