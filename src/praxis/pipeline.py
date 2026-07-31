"""Фабрика пайплайна: собирает end-to-end Praxis из компонентов.

Каждый компонент через `default_*()` сам выбирает реальную (GPU/LLM) или
детерминированную оффлайн-реализацию по наличию зависимостей и ключей. Значит один и
тот же `build_pipeline()` работает и «в бою», и локально без единой зависимости.
"""

from __future__ import annotations

from collections.abc import Iterable

from .agent.self_rag import SelfRAG, SelfRAGConfig
from .cases import SAMPLE_CASES
from .core.models import Provision
from .embed import default_embedder
from .generate import default_answerer
from .graph.expander import GraphExpandingRetriever
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
    use_graph: bool = True,
    use_cases: bool = True,
    use_glia: bool = True,
):
    corpus = load_sample_provisions() if provisions is None else list(provisions)

    bm25 = BM25Retriever(corpus)
    if use_dense:
        dense = DenseRetriever(corpus, default_embedder())
        retriever = HybridRetriever(bm25, dense)
    else:
        retriever = bm25

    if use_graph:
        retriever = GraphExpandingRetriever(retriever, corpus)

    # LLM-режим на glia: если есть провайдер (ключ) и установлена glia — агентный путь.
    if use_glia:
        from .llm import default_glia_llm

        glia_llm = default_glia_llm()
        if glia_llm is not None:
            from .agent.glia_agent import GliaLegalAgent

            return GliaLegalAgent(
                glia_llm, retriever, default_verifier(), reranker=default_reranker()
            )

    return SelfRAG(
        retriever=retriever,
        verifier=default_verifier(),
        answerer=default_answerer(),
        reranker=default_reranker(),
        config=config,
        cases=SAMPLE_CASES if use_cases else None,
    )
