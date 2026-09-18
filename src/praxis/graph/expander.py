"""Graph-expansion ретривер: дотягивает нормы, на которые ссылаются найденные.

Оборачивает любой базовый ретривер. После поиска берёт топ-хиты и по графу ссылок
добавляет упомянутые в них статьи (multi-hop). Это включает рассуждение по цепочкам:
вопрос про убытки за нарушение договора → ст. 393 → (ссылается на) ст. 15. Реранкер и
Citation Verifier ниже отсеивают нерелевантное, поэтому расширение безопасно.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from ..core.models import Provision, RetrievedProvision
from ..retrieve.base import Retriever
from .refs import build_reference_graph


class GraphExpandingRetriever:
    """Реализует протокол `retrieve.base.Retriever`."""

    def __init__(
        self,
        base: Retriever,
        provisions: Iterable[Provision],
        # (act_id, article) -> {(act_id, referenced article)}. The act has to be
        # in the key: without it article 15 of the Civil Code links to article 15
        # of the Labour Code, which is what build_reference_graph's docstring
        # warns about. The annotation said dict[str, set[str]] and invited
        # exactly that.
        graph: dict[tuple[str, str], set[tuple[str, str]]] | None = None,
        *,
        hops: int = 1,
        expand_from: int = 5,
        weight: float = 0.5,
    ) -> None:
        self.base = base
        provisions = list(provisions)
        self.by_article: dict[tuple[str, str], list[Provision]] = defaultdict(list)
        for p in provisions:
            self.by_article[(p.act.id, p.article_number)].append(p)
        self.graph = graph if graph is not None else build_reference_graph(provisions)
        self.hops = hops
        self.expand_from = expand_from
        self.weight = weight

    def search(self, query: str, top_k: int = 5) -> list[RetrievedProvision]:
        hits = self.base.search(query, top_k=top_k)
        seen = {h.provision.id for h in hits}
        extra: list[RetrievedProvision] = []

        frontier = [
            ((h.provision.act.id, h.provision.article_number), h.score)
            for h in hits[: self.expand_from]
        ]
        for _ in range(self.hops):
            next_frontier: list[tuple[tuple[str, str], float]] = []
            for key, score in frontier:
                for ref_key in self.graph.get(key, ()):
                    for p in self.by_article.get(ref_key, ()):
                        if p.id in seen:
                            continue
                        seen.add(p.id)
                        w = score * self.weight
                        extra.append(RetrievedProvision(p, score=w, method="graph"))
                        next_frontier.append((ref_key, w))
            frontier = next_frontier

        return hits + extra
