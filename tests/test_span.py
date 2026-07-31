from praxis.pipeline import build_pipeline
from praxis.span import find_support_span


def test_find_support_span_locates_relevant_sentence():
    text = "Первое предложение про налоги. Второе про толкование договора судом при неясности."
    span = find_support_span("как суд толкует условие договора", text)
    assert span is not None
    start, end = span
    assert "толкование договора" in text[start:end]


def test_find_support_span_none_for_empty():
    assert find_support_span("", "какой-то текст") is None
    assert find_support_span("вопрос", "") is None


def test_pipeline_attaches_spans_within_bounds():
    answer = build_pipeline().answer("Можно ли расторгнуть договор через суд при нарушении?")
    assert answer.citations
    assert any(c.span is not None for c in answer.citations)
    for c in answer.citations:
        if c.span is not None:
            start, end = c.span
            assert 0 <= start < end <= len(c.provision.text)
