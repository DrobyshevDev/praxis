from praxis.core.models import Answer
from praxis.generate.extractive import ExtractiveAnswerer
from praxis.generate.llm_answerer import LLMAnswerer
from praxis.ingest import load_sample_provisions
from praxis.llm.mock import MockLLM
from praxis.retrieve.bm25 import BM25Retriever


def _retrieved(query: str, k: int = 3):
    provisions = load_sample_provisions()
    return BM25Retriever(provisions).search(query, top_k=k)


def test_extractive_answer_has_citations():
    retrieved = _retrieved("расторжение договора по решению суда")
    answer = ExtractiveAnswerer().answer("Можно ли расторгнуть договор через суд?", retrieved)
    assert isinstance(answer, Answer)
    assert answer.citations
    assert "ст." in answer.text
    assert any(c.provision.article_number == "450" for c in answer.citations)


def test_extractive_answer_empty_when_no_provisions():
    answer = ExtractiveAnswerer().answer("любой вопрос", [])
    assert answer.citations == []
    assert answer.confidence == 0.0


def test_llm_answerer_uses_client_and_builds_prompt():
    retrieved = _retrieved("расторжение договора по решению суда")
    llm = MockLLM(reply="Договор может быть расторгнут судом при существенном нарушении [1].")
    answer = LLMAnswerer(llm).answer("Можно ли расторгнуть договор через суд?", retrieved)
    assert "расторгнут" in answer.text
    assert answer.citations
    # Контекст с нормами реально попал в промпт.
    assert llm.last_prompt is not None and "ст. 450" in llm.last_prompt


def test_llm_answerer_no_provisions():
    answer = LLMAnswerer(MockLLM()).answer("вопрос", [])
    assert answer.citations == []
