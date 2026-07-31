"""Реальный эмбеддер BAAI/bge-m3 (multilingual). Требует extra `ml`, гоняется на GPU.

Ленивая загрузка: torch/sentence-transformers импортируются и модель качается только
при первом обращении, чтобы импорт пакета оставался лёгким. По умолчанию device=cuda
при наличии (RTX 4060), иначе cpu.
"""

from __future__ import annotations

from collections.abc import Sequence


class BGEM3Embedder:
    dim: int = 1024

    def __init__(self, model_name: str = "BAAI/bge-m3", device: str | None = None) -> None:
        self._model_name = model_name
        self._device = device
        self._model = None

    def _ensure(self):
        if self._model is None:
            import torch
            from sentence_transformers import SentenceTransformer

            device = self._device or ("cuda" if torch.cuda.is_available() else "cpu")
            self._model = SentenceTransformer(self._model_name, device=device)
        return self._model

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        model = self._ensure()
        vectors = model.encode(
            list(texts), normalize_embeddings=True, convert_to_numpy=True
        )
        return [row.tolist() for row in vectors]

    def embed_query(self, text: str) -> list[float]:
        return self.embed([text])[0]
