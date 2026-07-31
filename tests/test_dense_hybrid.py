from praxis.embed import HashingEmbedder
from praxis.ingest import load_sample_provisions
from praxis.retrieve.bm25 import BM25Retriever
from praxis.retrieve.dense import DenseRetriever, _cosine
from praxis.retrieve.hybrid import HybridRetriever


def test_hashing_embedder_shape_and_determinism():
    emb = HashingEmbedder(dim=128)
    a = emb.embed_query("толкование договора")
    b = emb.embed_query("толкование договора")
    assert len(a) == 128
    assert a == b  # детерминизм
    assert abs(_cosine(a, a) - 1.0) < 1e-9


def test_dense_retriever_returns_ranked():
    provisions = load_sample_provisions()
    dense = DenseRetriever(provisions, HashingEmbedder())
    res = dense.search("свобода заключения договора", top_k=3)
    assert res
    assert all(r.method == "dense" for r in res)
    scores = [r.score for r in res]
    assert scores == sorted(scores, reverse=True)


def test_hybrid_merges_bm25_and_dense():
    provisions = load_sample_provisions()
    bm25 = BM25Retriever(provisions)
    dense = DenseRetriever(provisions, HashingEmbedder())
    hybrid = HybridRetriever(bm25, dense)
    res = hybrid.search("толкование условий договора", top_k=5)
    assert res
    assert all(r.method == "hybrid" for r in res)
    assert any(r.provision.article_number == "431" for r in res)
