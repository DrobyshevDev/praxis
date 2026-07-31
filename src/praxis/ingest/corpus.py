"""Загрузка корпуса из каталога JSON-актов (полный корпус подключается сюда)."""

from __future__ import annotations

from pathlib import Path

from .schema import RawAct
from .sources.json_loader import load_act_json


# Файлы в корпус-каталоге, которые не являются актами (грузятся отдельно).
_NON_ACT = {"practice.json"}


def load_corpus_dir(path: str | Path) -> list[RawAct]:
    """Все *.json-акты из каталога → список актов (без practice.json и служебных)."""
    return [
        load_act_json(f)
        for f in sorted(Path(path).glob("*.json"))
        if f.name not in _NON_ACT
    ]
