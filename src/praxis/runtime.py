"""Рантайм-переключатели.

PRAXIS_OFFLINE=1 форсит детерминированные fallback-компоненты (без GPU-моделей и сети)
даже если тяжёлые зависимости установлены. Нужен, чтобы тесты и быстрое демо не тянули
модели; реальные модели — по явному запуску (флаг снят).
"""

from __future__ import annotations

import os

_TRUE = {"1", "true", "yes", "on"}


def is_offline() -> bool:
    return os.environ.get("PRAXIS_OFFLINE", "").strip().lower() in _TRUE
