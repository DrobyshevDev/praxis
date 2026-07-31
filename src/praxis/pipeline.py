"""Фабрика пайплайна: собирает end-to-end Praxis из компонентов.

Каждый компонент через `default_*()` сам выбирает реальную (GPU/LLM) или
детерминированную оффлайн-реализацию по наличию зависимостей и ключей. Значит один и
тот же `build_pipeline()` работает и «в бою», и локально без единой зависимости.
"""

from __future__ import annotations

from collections.abc import Iterable

from .agent.self_rag import SelfRAG, SelfRAGConfig
from .core.models import Provision
from .embed import default_embedder
from .generate import default_answerer
from .ingest import load_sample_provisions
from .rerank import default_reranker
from .retrieve.bm25 import BM25Retriever
from .retrieve.dense import DenseRetriever
from .retrieve.hybrid import HybridRetriever
from .verify import default_verifier


def build_pipeline(
    provisions: Iterable[Provision] | None = None,
    *,
    config: SelfRAGConfig | None = None,
    use_dense: bool = True,
) -> SelfRAG:
    corpus = load_sample_provisions() if provisions is None else list(provisions)

    bm25 = BM25Retriever(corpus)
    if use_dense:
        dense = DenseRetriever(corpus, default_embedder())
        retriever = HybridRetriever(bm25, dense)
    else:
        retriever = bm25

    return SelfRAG(
        retriever=retriever,
        verifier=default_verifier(),
        answerer=default_answerer(),
        reranker=default_reranker(),
        config=config,
    )
