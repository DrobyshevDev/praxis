"""Юридические задачи поверх ядра: готовые документы из найденных норм."""

from __future__ import annotations

from .calc import FeeResult, PenaltyResult, court_fee, penalty
from .claim import ClaimResult, build_claim, claim_applicable

__all__ = [
    "ClaimResult",
    "FeeResult",
    "PenaltyResult",
    "build_claim",
    "claim_applicable",
    "court_fee",
    "penalty",
]
