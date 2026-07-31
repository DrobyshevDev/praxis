"""Baseline BM25 (Okapi) без внешних зависимостей.

Достаточно для v0-среза и как «половина» гибрида: BM25 хорошо ловит точные
формулировки и номера статей, dense (v1) добавит семантику. Токенизация —
простая, по буквенно-цифровым словам; лемматизация/стоп-слова — улучшение v1.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from collections.abc import Iterable

from ..core.models import Provision, RetrievedProvision

_TOKEN_RE = re.compile(r"[а-яёa-z0-9]+", re.IGNORECASE)


def tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


class BM25Retriever:
    """Реализует протокол `retrieve.base.Retriever`."""

    def __init__(
        self, provisions: Iterable[Provision], k1: float = 1.5, b: float = 0.75
    ) -> None:
        self.provisions: list[Provision] = list(provisions)
        # Индексируем текст нормы вместе с названием статьи — оно несёт сигнал.
        self._docs: list[list[str]] = [
            tokenize(f"{p.article_title} {p.text}") for p in self.provisions
        ]
        self._n = len(self._docs)
        self._avgdl = (sum(len(d) for d in self._docs) / self._n) if self._n else 0.0
        self.k1 = k1
        self.b = b

        self._tf: list[Counter[str]] = [Counter(d) for d in self._docs]
        self._df: Counter[str] = Counter()
        for doc in self._docs:
            self._df.update(set(doc))

    def _idf(self, term: str) -> float:
        n = self._df.get(term, 0)
        return math.log((self._n - n + 0.5) / (n + 0.5) + 1.0)

    def search(self, query: str, top_k: int = 5) -> list[RetrievedProvision]:
        q_terms = tokenize(query)
        scored: list[tuple[int, float]] = []
        for i, tf in enumerate(self._tf):
            dl = len(self._docs[i])
            if dl == 0:
                continue
            score = 0.0
            for term in q_terms:
                freq = tf.get(term, 0)
                if not freq:
                    continue
                idf = self._idf(term)
                denom = freq + self.k1 * (1 - self.b + self.b * dl / self._avgdl)
                score += idf * (freq * (self.k1 + 1)) / denom
            if score > 0:
                scored.append((i, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [
            RetrievedProvision(self.provisions[i], score=s, method="bm25")
            for i, s in scored[:top_k]
        ]
