"""v0 демо: end-to-end срез retrieval на образце корпуса.

    python -m praxis.demo "как суд толкует неясное условие договора"

Показывает вживую цепочку v0: образец ГК → легал-aware нормы → BM25 → цитаты.
Dense-поиск, reranker, Citation Verifier и self-RAG подключаются на v1.
"""

from __future__ import annotations

import sys

from .ingest import load_sample_provisions
from .retrieve.bm25 import BM25Retriever

DEFAULT_QUERY = "как суд толкует неясное условие договора"


def main() -> None:
    query = " ".join(sys.argv[1:]).strip() or DEFAULT_QUERY

    provisions = load_sample_provisions()
    retriever = BM25Retriever(provisions)
    results = retriever.search(query, top_k=5)

    print(f"\n  Вопрос: {query}")
    print(f"  Корпус: {len(provisions)} норм (образец ГК РФ ч.1)\n")
    if not results:
        print("  Ничего не найдено.\n")
        return

    for rank, r in enumerate(results, 1):
        print(f"  {rank}. [{r.score:5.2f}] {r.provision.citation} — {r.provision.article_title}")
        text = r.provision.text
        snippet = text if len(text) <= 220 else text[:217] + "..."
        print(f"        {snippet}\n")


if __name__ == "__main__":
    main()
