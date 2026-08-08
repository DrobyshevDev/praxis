"""Плотный (семантический) ретривер поверх любого Embedder.

Быстрый путь на numpy (косинус — умножение матрицы на вектор, миллисекунды на десятках
тысяч норм) с чистым stdlib-fallback, чтобы офлайн-режим и CI работали без numpy. Векторы
корпуса кэшируются на диск (PRAXIS_CACHE_DIR): рестарт сервера — мгновенная загрузка вместо
повторного прогона эмбеддера по всему корпусу.
"""

from __future__ import annotations

import hashlib
import math
import os
from collections.abc import Iterable

from ..core.models import Provision, RetrievedProvision
from ..embed.base import Embedder


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


class DenseRetriever:
    """Реализует протокол `retrieve.base.Retriever`."""

    def __init__(
        self,
        provisions: Iterable[Provision],
        embedder: Embedder,
        cache_dir: str | None = None,
    ) -> None:
        self.provisions: list[Provision] = list(provisions)
        self.embedder = embedder
        texts = [f"{p.article_title}. {p.text}" for p in self.provisions]

        vectors = self._load_or_embed(texts, cache_dir)
        self._np = None
        self._mat = None
        self._vectors = vectors  # fallback хранилище
        try:
            import numpy as np

            self._np = np
            # len(), а не `if vectors:` — из кэша приходит numpy-массив, и `if array:`
            # бросает ValueError (ambiguous truth), после чего поиск молча падал на
            # медленный чистый Python (косинус по 12 742×1024 = ~15с/запрос).
            if len(vectors) > 0:
                mat = np.asarray(vectors, dtype="float32")
                norms = np.linalg.norm(mat, axis=1, keepdims=True)
                norms[norms == 0] = 1.0
                self._mat = mat / norms  # нормируем строки — косинус через скалярное
        except Exception:
            self._np = None

    def _load_or_embed(self, texts: list[str], cache_dir: str | None) -> list[list[float]]:
        if not texts:
            return []
        cache_dir = cache_dir or os.environ.get("PRAXIS_CACHE_DIR")
        if not cache_dir:
            return self.embedder.embed(texts)

        try:
            import numpy as np

            os.makedirs(cache_dir, exist_ok=True)
            key = self._cache_key(texts)
            path = os.path.join(cache_dir, f"emb-{key}.npy")
            if os.path.exists(path):
                return np.load(path)  # массив; numpy-путь примет как есть
            vectors = self.embedder.embed(texts)
            np.save(path, np.asarray(vectors, dtype="float32"))
            return vectors
        except Exception:
            return self.embedder.embed(texts)

    def _cache_key(self, texts: list[str]) -> str:
        h = hashlib.md5()
        h.update(type(self.embedder).__name__.encode())
        h.update(str(getattr(self.embedder, "dim", "")).encode())
        h.update(str(len(texts)).encode())
        for t in texts:
            h.update(t.encode("utf-8"))
        return h.hexdigest()[:16]

    def search(self, query: str, top_k: int = 5) -> list[RetrievedProvision]:
        if not self.provisions:
            return []
        q = self.embedder.embed_query(query)

        if self._mat is not None:
            np = self._np
            qv = np.asarray(q, dtype="float32")
            qn = float(np.linalg.norm(qv)) or 1.0
            scores = self._mat @ (qv / qn)
            idx = np.argsort(-scores)[:top_k]
            return [
                RetrievedProvision(self.provisions[int(i)], score=float(scores[int(i)]), method="dense")
                for i in idx
            ]

        scored = [(i, _cosine(q, v)) for i, v in enumerate(self._vectors)]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [
            RetrievedProvision(self.provisions[i], score=s, method="dense")
            for i, s in scored[:top_k]
        ]
