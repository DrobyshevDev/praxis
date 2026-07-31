from praxis.core.models import RetrievedProvision
from praxis.ingest import load_sample_provisions
from praxis.retrieve import reciprocal_rank_fusion
from praxis.retrieve.bm25 import BM25Retriever, tokenize


def test_tokenize_basic():
    assert tokenize("Толкование, договора!") == ["толкование", "договора"]


def test_bm25_finds_relevant_article_on_top():
    provisions = load_sample_provisions()
    retriever = BM25Retriever(provisions)
    results = retriever.search("толкование условий договора судом", top_k=3)
    assert results
    assert any(r.provision.article_number == "431" for r in results[:2])
    # Скоры отсортированы по убыванию.
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_bm25_no_match_returns_empty():
    provisions = load_sample_provisions()
    retriever = BM25Retriever(provisions)
    assert retriever.search("квантовая хромодинамика бозон", top_k=5) == []


def test_rrf_merges_and_dedupes():
    provisions = load_sample_provisions()[:3]
    run_a = [RetrievedProvision(p, score=1.0, method="bm25") for p in provisions]
    run_b = [RetrievedProvision(p, score=1.0, method="dense") for p in reversed(provisions)]
    fused = reciprocal_rank_fusion([run_a, run_b], top_k=10)
    ids = [r.provision.id for r in fused]
    assert len(ids) == len(set(ids)) == 3
    assert all(r.method == "hybrid" for r in fused)
