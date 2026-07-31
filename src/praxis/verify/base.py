"""Контракт Citation Verifier. Реализация (NLI/LLM-судья) — v1."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ..core.models import Citation, VerifiedClaim


@runtime_checkable
class CitationVerifier(Protocol):
    """Проверяет, подтверждает ли процитированная норма конкретный тезис."""

    def verify(self, claim: str, citation: Citation) -> VerifiedClaim: ...
