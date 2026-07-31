"""Загрузка корпуса из каталога JSON-актов (полный корпус подключается сюда)."""

from __future__ import annotations

from pathlib import Path

from .schema import RawAct
from .sources.json_loader import load_act_json


def load_corpus_dir(path: str | Path) -> list[RawAct]:
    """Все *.json из каталога → список актов (детерминированный порядок)."""
    return [load_act_json(f) for f in sorted(Path(path).glob("*.json"))]
