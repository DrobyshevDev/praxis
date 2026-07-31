"""Минимальный Python-клиент открытого API Praxis (только стандартная библиотека).

    from praxis_client import PraxisClient
    c = PraxisClient("http://localhost:8077")
    ans = c.ask("можно ли расторгнуть договор через суд при нарушении")
    print(ans["confidence"], ans["text"])
    for hit in c.search("толкование договора", top_k=5):
        print(hit["citation"], hit["score"])
"""

from __future__ import annotations

import json
import urllib.request


class PraxisClient:
    def __init__(self, base_url: str = "http://localhost:8077", timeout: int = 60) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _post(self, path: str, payload: dict) -> dict | list:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.base_url + path,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as r:  # noqa: S310
            return json.load(r)

    def ask(self, question: str) -> dict:
        """Ответ со ссылками на нормы, проверкой цитат и трейсом."""
        return self._post("/v1/ask", {"question": question})  # type: ignore[return-value]

    def search(self, query: str, top_k: int = 5) -> list:
        """Сырой поиск норм по корпусу (гибрид + reranker)."""
        return self._post("/v1/search", {"query": query, "top_k": top_k})  # type: ignore[return-value]

    def health(self) -> dict:
        with urllib.request.urlopen(self.base_url + "/health", timeout=self.timeout) as r:  # noqa: S310
            return json.load(r)


if __name__ == "__main__":
    import sys

    client = PraxisClient()
    question = " ".join(sys.argv[1:]) or "можно ли расторгнуть договор через суд при нарушении"
    answer = client.ask(question)
    print(f"[{answer['confidence']:.0%}] {answer['text'][:400]}")
    for c in answer["citations"]:
        print(" -", c["citation"])
