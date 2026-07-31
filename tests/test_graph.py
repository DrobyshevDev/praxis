from praxis.core.models import RetrievedProvision
from praxis.graph.expander import GraphExpandingRetriever
from praxis.graph.refs import build_reference_graph, extract_references
from praxis.ingest import load_sample_provisions


def test_extract_references():
    assert extract_references("в соответствии со статьёй 15 настоящего Кодекса") == {"15"}
    assert extract_references("по основаниям, предусмотренным статьёй 450") == {"450"}
    assert extract_references("определяются статьями 15 и 393 настоящего Кодекса") == {"15", "393"}
    assert extract_references("здесь нет ссылок на нормы") == set()


def test_build_graph_has_expected_edges():
    graph = build_reference_graph(load_sample_provisions())
    assert "422" in graph.get("421", set())  # ст.421 п.4 → (статья 422)
    assert "15" in graph.get("393", set())   # ст.393 п.2 → статьёй 15
    assert "450" in graph.get("452", set())  # ст.452 п.2 → статьёй 450


class _FakeBase:
    def __init__(self, hit: RetrievedProvision) -> None:
        self.hit = hit

    def search(self, query: str, top_k: int = 5):
        return [self.hit]


def test_graph_expander_adds_referenced_article():
    provisions = load_sample_provisions()
    p393 = next(p for p in provisions if p.article_number == "393" and "2" in p.path)
    base = _FakeBase(RetrievedProvision(p393, score=1.0, method="bm25"))

    expander = GraphExpandingRetriever(base, provisions)
    hits = expander.search("возмещение убытков", top_k=5)

    articles = {h.provision.article_number for h in hits}
    assert "393" in articles
    assert "15" in articles  # дотянуто графом (393 → статья 15)
    assert any(h.method == "graph" for h in hits)


def test_pipeline_with_graph_multi_hop():
    from praxis.pipeline import build_pipeline

    answer = build_pipeline(use_graph=True).answer(
        "обязан ли должник возместить убытки за нарушение обязательства"
    )
    assert answer.citations
