"""Реальный cross-encoder BAAI/bge-reranker-v2-m3 (multilingual). Extra `ml`, GPU.

Двухстадийность (hybrid → rerank) — основной источник прироста Recall в 2026: по
опубликованным бенчмаркам ~+17% к Recall@5 против чистого гибрида. Ленивая загрузка.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

from ..core.models import RetrievedProvision


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


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
        # Небольшой батч: cross-encoder по длинным текстам иначе даёт спайк памяти
        # на GPU с 8 ГБ (модели уже держат ~5 ГБ).
        scores = model.predict(pairs, batch_size=8)
        # Возвращаем закэшированную аллокатором память GPU — иначе на 8 ГБ карте
        # резерв растёт и следующий запрос упирается в OOM (на Windows нет
        # expandable_segments). Стоит десятки мс, спасает от тормозов/500.
        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass
        ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
        # Логиты cross-encoder → 0..1 через sigmoid, чтобы скор был калиброванной
        # оценкой релевантности (используется как уверенность экстрактивного ответа).
        return [
            RetrievedProvision(c.provision, score=_sigmoid(float(s)), method="rerank")
            for c, s in ranked[:top_k]
        ]
