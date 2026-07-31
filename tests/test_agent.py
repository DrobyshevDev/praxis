from praxis.agent.self_rag import SelfRAG, SelfRAGConfig
from praxis.core.models import Answer
from praxis.pipeline import build_pipeline


def test_pipeline_answers_with_grounded_citations():
    pipeline = build_pipeline()
    answer = pipeline.answer("Можно ли расторгнуть договор через суд при нарушении?")
    assert isinstance(answer, Answer)
    assert answer.citations
    assert any(c.provision.article_number == "450" for c in answer.citations)
    assert 0.0 <= answer.confidence <= 1.0
    assert answer.steps  # трейс рассуждения заполнен
    assert answer.verified


def test_pipeline_low_confidence_on_offtopic():
    pipeline = build_pipeline()
    good = pipeline.answer("Как суд толкует неясное условие договора?")
    junk = pipeline.answer("квантовая хромодинамика глюонное поле бозон")
    assert junk.confidence < good.confidence


def test_self_rag_trace_records_rounds():
    pipeline = build_pipeline()
    answer = pipeline.answer("свобода договора")
    assert any("Раунд 1" in s for s in answer.steps)


def test_config_is_respected():
    cfg = SelfRAGConfig(answer_top_k=2)
    pipeline = build_pipeline(config=cfg)
    answer = pipeline.answer("расторжение договора по решению суда")
    assert len(answer.citations) <= 2
