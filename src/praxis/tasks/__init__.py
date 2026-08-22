"""Юридические задачи поверх ядра: готовые документы из найденных норм."""

from __future__ import annotations

from .calc import (
    FeeResult,
    InterestResult,
    PenaltyResult,
    court_fee,
    interest_395,
    penalty,
)
from .claim import ClaimResult, build_claim, claim_applicable
from .lawsuit import LawsuitResult, build_lawsuit

__all__ = [
    "ClaimResult",
    "FeeResult",
    "InterestResult",
    "LawsuitResult",
    "PenaltyResult",
    "build_claim",
    "build_lawsuit",
    "claim_applicable",
    "court_fee",
    "interest_395",
    "penalty",
]
