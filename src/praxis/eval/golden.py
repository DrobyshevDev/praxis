"""Golden set — эталонные вопросы с ожидаемыми нормами (по образцу корпуса).

На v1 расширяется до 100–200 реальных юр-вопросов с разметкой юриста. Пока покрывает
все статьи образца ГК РФ ч.1 и служит регрессионным набором для метрик ретривера.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GoldenCase:
    question: str
    relevant: frozenset[str] = field(default_factory=frozenset)  # номера статей


GOLDEN: list[GoldenCase] = [
    GoldenCase("Можно ли расторгнуть договор через суд при существенном нарушении?", frozenset({"450"})),
    GoldenCase("По каким основаниям можно изменить или расторгнуть договор?", frozenset({"450"})),
    GoldenCase("Когда договор можно расторгнуть по соглашению сторон?", frozenset({"450"})),
    GoldenCase("Как суд толкует неясные условия договора?", frozenset({"431"})),
    GoldenCase("Как определить действительную общую волю сторон договора?", frozenset({"431"})),
    GoldenCase("Что учитывается при толковании договора помимо буквального значения слов?", frozenset({"431"})),
    GoldenCase("Что такое свобода договора?", frozenset({"421"})),
    GoldenCase("Обязаны ли стороны заключать договор?", frozenset({"421"})),
    GoldenCase("Что такое злоупотребление правом?", frozenset({"10"})),
    GoldenCase("Может ли суд отказать в защите права при злоупотреблении?", frozenset({"10"})),
    GoldenCase("Как должны исполняться обязательства?", frozenset({"309"})),
    GoldenCase("Можно ли в одностороннем порядке отказаться от исполнения обязательства?", frozenset({"310"})),
]
