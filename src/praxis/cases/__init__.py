"""Судебная практика и граф «норма ↔ дело» (образец данных, реальный индекс)."""

from .index import build_case_index, related_cases
from .sample import SAMPLE_CASES

__all__ = ["SAMPLE_CASES", "build_case_index", "related_cases"]
