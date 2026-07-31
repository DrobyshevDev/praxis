"""Интеграция с glia — тест на scripted EchoLLM (оффлайн, без ключей и сети)."""

import pytest

pytest.importorskip("glia")

from glia.providers import EchoLLM, call  # noqa: E402

from praxis.agent.glia_agent import GliaLegalAgent  # noqa: E402
from praxis.ingest import load_sample_provisions  # noqa: E402
from praxis.rerank.lexical import LexicalReranker  # noqa: E402
from praxis.retrieve.bm25 import BM25Retriever  # noqa: E402
from praxis.verify.heuristic import HeuristicVerifier  # noqa: E402


def _agent(reply: str) -> GliaLegalAgent:
    provisions = load_sample_provisions()
    # Скрипт: модель зовёт инструмент поиска, затем отвечает.
    llm = EchoLLM([call("search_law", {"query": "расторжение договора через суд"}), reply])
    return GliaLegalAgent(
        llm, BM25Retriever(provisions), HeuristicVerifier(), reranker=LexicalReranker()
    )


def test_glia_agent_uses_tool_and_grounds_answer():
    agent = _agent(
        "Договор может быть расторгнут по решению суда при существенном нарушении "
        "договора другой стороной (ст. 450 ГК РФ)."
    )
    answer = agent.answer("Можно ли расторгнуть договор через суд?")

    assert answer.citations
    assert any(c.provision.article_number == "450" for c in answer.citations)
    # Трейс взят из glia-trajectory (реальное использование glia).
    assert any("glia" in s for s in answer.steps)
    assert any("search_law" in s for s in answer.steps)


def test_glia_agent_flags_unsupported_sentence():
    agent = _agent(
        "Договор может быть расторгнут судом при существенном нарушении договора другой "
        "стороной. За расторжение договора всегда взимается штраф в миллион рублей."
    )
    answer = agent.answer("Можно ли расторгнуть договор через суд?")
    assert answer.unverified_claims
    flagged = " ".join(answer.unverified_claims).lower()
    assert "штраф" in flagged or "миллион" in flagged
