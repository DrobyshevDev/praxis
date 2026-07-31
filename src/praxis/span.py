"""Поиск подтверждающего span — какая часть текста нормы отвечает на запрос.

Возвращает символьные смещения предложения нормы с наибольшим пересечением токенов с
запросом (с префиксным кредитом на морфологию). Используется для подсветки в UI: юрист
сразу видит, какая фраза нормы относится к его вопросу, а не читает статью целиком.
"""

from __future__ import annotations

import re

from .retrieve.bm25 import tokenize

_SENTENCE_RE = re.compile(r"[^.!?]+[.!?]?")


def find_support_span(claim: str, text: str) -> tuple[int, int] | None:
    claim_tokens = set(tokenize(claim))
    if not claim_tokens or not text:
        return None

    best: tuple[int, int] | None = None
    best_score = 0.0
    for m in _SENTENCE_RE.finditer(text):
        segment = m.group()
        stripped = segment.strip()
        if not stripped:
            continue
        start = m.start() + (len(segment) - len(segment.lstrip()))
        end = start + len(stripped)

        tokens = set(tokenize(stripped))
        if not tokens:
            continue
        prefixes = {t[:4] for t in tokens}
        hits = 0.0
        for t in claim_tokens:
            if t in tokens:
                hits += 1.0
            elif t[:4] in prefixes:
                hits += 0.5
        score = hits / len(claim_tokens)
        if score > best_score:
            best_score = score
            best = (start, end)

    return best if best_score > 0 else None
