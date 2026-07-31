"""Реальный cross-encoder BAAI/bge-reranker-v2-m3 (multilingual). Extra `ml`, GPU.

Двухстадийность (hybrid → rerank) — основной источник прироста Recall в 2026: по
опубликованным бенчмаркам ~+17% к Recall@5 против чистого гибрида. Ленивая загрузка.
"""

from __future__ import annotations

from collections.abc import Sequence

from ..core.models import RetrievedProvision


class BGEReranker:
    """Реализует протокол `retrieve.base.Reranker`."""

    def __init__(
        self, model_name: str = "BAAI/bge-reranker-v2-m3", device: str | None = None
    ) -> None:
        self._model_name = model_name
        self._device = device
        self._model = None

    def _ensure(self):
        if self._model is None:
            import torch
            from sentence_transformers import CrossEncoder

            device = self._device or ("cuda" if torch.cuda.is_available() else "cpu")
            self._model = CrossEncoder(self._model_name, device=device)
        return self._model

    def rerank(
        self, query: str, candidates: Sequence[RetrievedProvision], top_k: int = 5
    ) -> list[RetrievedProvision]:
        candidates = list(candidates)
        if not candidates:
            return []
        model = self._ensure()
        pairs = [
            [query, f"{c.provision.article_title}. {c.provision.text}"]
            for c in candidates
        ]
        scores = model.predict(pairs)
        ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
        return [
            RetrievedProvision(c.provision, score=float(s), method="rerank")
            for c, s in ranked[:top_k]
        ]
