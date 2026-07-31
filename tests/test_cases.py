from praxis.cases import SAMPLE_CASES, build_case_index, related_cases
from praxis.pipeline import build_pipeline


def test_case_index_and_related():
    index = build_case_index(SAMPLE_CASES)
    assert ("gk-rf-1", "450") in index
    cases = related_cases([("gk-rf-1", "450")], index)
    assert cases
    assert all("450" in c.cited_articles for c in cases)


def test_related_cases_dedupe_and_limit():
    index = build_case_index(SAMPLE_CASES)
    cases = related_cases([("gk-rf-1", "450"), ("gk-rf-1", "431")], index, limit=10)
    ids = [c.id for c in cases]
    assert len(ids) == len(set(ids))  # без дублей


def test_case_index_is_act_scoped():
    # (act_id, статья) не путает ст.450 разных кодексов
    index = build_case_index(SAMPLE_CASES)
    assert ("uk-rf", "450") not in index  # образец — только ГК


def test_pipeline_attaches_related_cases():
    answer = build_pipeline().answer("Можно ли расторгнуть договор через суд при нарушении?")
    assert answer.related_cases
    assert any("450" in c.cited_articles for c in answer.related_cases)


def test_pipeline_cases_can_be_disabled():
    answer = build_pipeline(use_cases=False).answer("Что такое свобода договора?")
    assert answer.related_cases == []
