"""Эвристический верификатор — детерминированный fallback.

Оценивает, насколько содержательные токены тезиса покрыты текстом нормы (с частичным
кредитом за префиксное совпадение — грубая поправка на морфологию). Отличает
SUPPORTS/UNRELATED; распознавание CONTRADICTS требует настоящей NLI-модели
(`NLIVerifier`). Нужен, чтобы весь конвейер проверки цитат работал без GPU и моделей.
"""

from __future__ import annotations

from ..core.models import Citation, Verdict, VerifiedClaim
from ..retrieve.bm25 import tokenize

_STOP = {
    "и", "в", "во", "не", "что", "он", "на", "с", "со", "как", "а", "то", "все",
    "так", "его", "но", "да", "к", "у", "же", "вы", "за", "бы", "по", "только",
    "от", "о", "из", "для", "при", "быть", "может", "если", "или", "чтобы", "этом",
    "том", "этой", "этот", "того", "также", "иных", "иное", "иными", "случаях",
    "настоящим", "настоящей", "предусмотренных", "другими", "либо", "об", "их",
}


class HeuristicVerifier:
    """Реализует протокол `verify.base.CitationVerifier`."""

    def __init__(self, support_threshold: float = 0.5) -> None:
        self.support_threshold = support_threshold

    def verify(self, claim: str, citation: Citation) -> VerifiedClaim:
        claim_tokens = {
            t for t in tokenize(claim) if len(t) > 2 and t not in _STOP
        }
        if not claim_tokens:
            return VerifiedClaim(claim, citation, Verdict.UNRELATED, 0.0)

        prov_tokens = set(tokenize(citation.provision.text))
        prov_prefixes = {t[:4] for t in prov_tokens}

        hits = 0.0
        for t in claim_tokens:
            if t in prov_tokens:
                hits += 1.0
            elif t[:4] in prov_prefixes:
                hits += 0.5
        score = hits / len(claim_tokens)

        verdict = (
            Verdict.SUPPORTS if score >= self.support_threshold else Verdict.UNRELATED
        )
        return VerifiedClaim(claim, citation, verdict, score)
