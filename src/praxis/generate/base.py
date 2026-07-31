"""Контракт генератора ответа: из найденных норм собирает Answer со ссылками."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from ..core.models import Answer, RetrievedProvision


@runtime_checkable
class Answerer(Protocol):
    def answer(
        self, question: str, provisions: Sequence[RetrievedProvision], top_k: int = 5
    ) -> Answer: ...
