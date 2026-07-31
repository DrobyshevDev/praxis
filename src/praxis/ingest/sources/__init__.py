"""Источники сырых актов. На v0 — образец; на v1 — парсеры pravo.gov.ru."""

from .gk_rf_part1 import GK_RF_PART1

SAMPLE_ACTS = [GK_RF_PART1]

__all__ = ["GK_RF_PART1", "SAMPLE_ACTS"]
