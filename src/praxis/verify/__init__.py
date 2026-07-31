"""Citation Verifier — ядро доверия.

Каждая пара «тезис ответа ↔ процитированная норма» проверяется на entailment.
Неподтверждённые тезисы не выдаются как факт. Реальная реализация — NLI-модель
(`NLIVerifier`); детерминированный fallback — `HeuristicVerifier`.
"""

from .base import CitationVerifier
from .heuristic import HeuristicVerifier

__all__ = ["CitationVerifier", "HeuristicVerifier", "default_verifier"]


def default_verifier() -> CitationVerifier:
    """NLI-модель, если доступны ML-зависимости; иначе эвристика."""
    from ..runtime import is_offline

    if is_offline():
        return HeuristicVerifier()
    try:
        import torch  # noqa: F401
        import transformers  # noqa: F401

        from .nli import NLIVerifier

        return NLIVerifier()
    except Exception:
        return HeuristicVerifier()
