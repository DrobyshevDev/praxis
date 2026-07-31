"""Citation Verifier — ядро доверия (v1).

Каждая пара «тезис ответа ↔ процитированная норма» проверяется на entailment
(NLI-модель на GPU + LLM-судья как ансамбль). Неподтверждённые тезисы не выдаются
как факт. Контракт — в base.py; реализация — на v1.
"""

from .base import CitationVerifier

__all__ = ["CitationVerifier"]
