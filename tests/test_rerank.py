from praxis.ingest import load_sample_provisions
from praxis.rerank.lexical import LexicalReranker
from praxis.retrieve.bm25 import BM25Retriever


def test_lexical_reranker_orders_by_score_and_limits():
    provisions = load_sample_provisions()
    bm25 = BM25Retriever(provisions)
    candidates = bm25.search("расторжение договора по решению суда", top_k=6)
    reranker = LexicalReranker()
    out = reranker.rerank("расторжение договора по решению суда", candidates, top_k=3)

    assert len(out) <= 3
    assert all(r.method == "rerank" for r in out)
    scores = [r.score for r in out]
    assert scores == sorted(scores, reverse=True)
    # Статья 450 (изменение и расторжение договора) должна быть в топе.
    assert any(r.provision.article_number == "450" for r in out)


def test_reranker_empty_candidates():
    assert LexicalReranker().rerank("что угодно", [], top_k=5) == []
