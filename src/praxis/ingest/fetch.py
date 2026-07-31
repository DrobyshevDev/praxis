"""Тонкий загрузчик официальных текстов по URL (для ингестии).

pravo.gov.ru — официальное опубликование НПА (кодексы, ФЗ) в машиночитаемом виде.
Пайплайн: fetch_text(url) → parse_statute_text(...) → нормы. Сеть намеренно изолирована
от остальной системы; конкретные эндпоинты/реквизиты pravo.gov.ru подключаются под задачу.
"""

from __future__ import annotations

import urllib.request

_UA = "praxis-ingest/0.1 (+https://github.com/DrobyshevDev/praxis)"


def fetch_text(url: str, *, timeout: int = 30, encoding: str = "utf-8") -> str:
    request = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
        return response.read().decode(encoding, errors="replace")
