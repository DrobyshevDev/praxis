from praxis.core.models import Citation, Verdict
from praxis.ingest import load_sample_provisions
from praxis.verify.heuristic import HeuristicVerifier


def _provision(number: str, path_hint: str | None = None):
    provisions = load_sample_provisions()
    return next(
        p
        for p in provisions
        if p.article_number == number and (path_hint is None or path_hint in p.path)
    )


def test_supports_when_claim_grounded():
    prov = _provision("450", "2")
    verifier = HeuristicVerifier()
    claim = (
        "Договор может быть расторгнут по решению суда при существенном нарушении "
        "договора другой стороной."
    )
    result = verifier.verify(claim, Citation(prov))
    assert result.verdict == Verdict.SUPPORTS
    assert result.score >= 0.5


def test_unrelated_when_claim_offtopic():
    prov = _provision("450", "2")
    verifier = HeuristicVerifier()
    result = verifier.verify(
        "Ставка налога на добавленную стоимость составляет двадцать процентов.",
        Citation(prov),
    )
    assert result.verdict == Verdict.UNRELATED


def test_empty_claim_is_unrelated():
    prov = _provision("309")
    result = HeuristicVerifier().verify("   ", Citation(prov))
    assert result.verdict == Verdict.UNRELATED
    assert result.score == 0.0
