"""Юридические задачи поверх ядра: готовые документы из найденных норм."""

from __future__ import annotations

from .claim import ClaimResult, build_claim, claim_applicable

__all__ = ["ClaimResult", "build_claim", "claim_applicable"]
