"""Лексический reranker — детерминированный fallback.

Переранжирует кандидатов по покрытию токенов запроса (с частичным кредитом за
совпадение 4-символьного префикса — грубая поправка на русскую морфологию без
внешнего стеммера). Это стенд-ин: реальное качество даёт cross-encoder `BGEReranker`.
"""

from __future__ import annotations

from collections.abc import Sequence

from ..core.models import RetrievedProvision
from ..retrieve.bm25 import tokenize


class LexicalReranker:
    """Реализует протокол `retrieve.base.Reranker`."""

    def rerank(
        self, query: str, candidates: Sequence[RetrievedProvision], top_k: int = 5
    ) -> list[RetrievedProvision]:
        q_tokens = set(tokenize(query))
        if not q_tokens:
            return list(candidates)[:top_k]

        rescored: list[RetrievedProvision] = []
        for c in candidates:
            toks = set(tokenize(f"{c.provision.article_title} {c.provision.text}"))
            prefixes = {t[:4] for t in toks}
            score = 0.0
            for t in q_tokens:
                if t in toks:
                    score += 1.0
                elif t[:4] in prefixes:
                    score += 0.5
            rescored.append(
                RetrievedProvision(c.provision, score=score / len(q_tokens), method="rerank")
            )

        rescored.sort(key=lambda r: r.score, reverse=True)
        return rescored[:top_k]
