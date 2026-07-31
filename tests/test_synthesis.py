"""LLM-синтез с пер-тезисной проверкой цитат.

Показывает киллер-фичу без реального ключа: у синтезированного ответа каждое
предложение проверяется против норм; обоснованное попадает в verified, выдуманное —
в unverified_claims и не подаётся как факт. С ANTHROPIC_API_KEY MockLLM меняется на Claude.
"""

from praxis.agent.self_rag import SelfRAG
from praxis.generate.llm_answerer import LLMAnswerer
from praxis.ingest import load_sample_provisions
from praxis.llm.mock import MockLLM
from praxis.rerank.lexical import LexicalReranker
from praxis.retrieve.bm25 import BM25Retriever
from praxis.verify.heuristic import HeuristicVerifier


def _pipeline_with_reply(reply: str) -> SelfRAG:
    provisions = load_sample_provisions()
    return SelfRAG(
        retriever=BM25Retriever(provisions),
        verifier=HeuristicVerifier(),
        answerer=LLMAnswerer(MockLLM(reply=reply)),
        reranker=LexicalReranker(),
    )


def test_synthesized_answer_flags_unsupported_sentence():
    reply = (
        "Договор может быть расторгнут по решению суда при существенном нарушении "
        "договора другой стороной. "
        "Кроме того, за расторжение договора всегда взимается штраф в размере миллиона рублей."
    )
    answer = _pipeline_with_reply(reply).answer(
        "Можно ли расторгнуть договор через суд при нарушении?"
    )

    assert answer.verified  # обоснованное предложение подтверждено нормой
    assert answer.unverified_claims  # выдуманное — во флаге, а не в фактах
    flagged = " ".join(answer.unverified_claims).lower()
    assert "штраф" in flagged or "миллион" in flagged
    assert 0.0 < answer.confidence < 1.0  # часть тезисов без опоры → не 100%
