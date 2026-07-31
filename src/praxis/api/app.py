"""FastAPI-приложение Praxis: /ask, /search, /health + веб-UI.

Пайплайн собирается один раз при первом обращении (build_pipeline с настройками из
окружения). По умолчанию — офлайн-fallback; с extra `ml`/`llm` и ключами включаются
реальные модели и Claude без изменения кода.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from ..config import config_from_env
from ..pipeline import build_pipeline
from .schemas import (
    AnswerOut,
    AskRequest,
    CaseOut,
    CitationOut,
    SearchHit,
    SearchRequest,
)
from .ui import INDEX_HTML

app = FastAPI(
    title="Praxis API",
    version="0.1.0",
    description="Юридический ассистент по праву РФ с проверяемыми цитатами.",
)

_pipeline = None


def get_pipeline():
    global _pipeline
    if _pipeline is None:
        _pipeline = build_pipeline(config=config_from_env())
    return _pipeline


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return INDEX_HTML


@app.post("/ask", response_model=AnswerOut)
def ask(req: AskRequest) -> AnswerOut:
    answer = get_pipeline().answer(req.question)
    verdict_by_id = {
        vc.citation.provision.id: vc.verdict.value for vc in answer.verified
    }
    citations = [
        CitationOut(
            id=c.provision.id,
            citation=c.provision.citation,
            article_number=c.provision.article_number,
            article_title=c.provision.article_title,
            text=c.provision.text,
            verdict=verdict_by_id.get(c.provision.id),
            span=list(c.span) if c.span else None,
        )
        for c in answer.citations
    ]
    cases = [
        CaseOut(
            citation=case.citation,
            court=case.court,
            number=case.number,
            date=case.date,
            summary=case.summary,
            cited_articles=sorted(case.cited_articles),
        )
        for case in answer.related_cases
    ]
    return AnswerOut(
        question=answer.question,
        text=answer.text,
        confidence=answer.confidence,
        citations=citations,
        unverified_claims=answer.unverified_claims,
        steps=answer.steps,
        related_cases=cases,
    )


@app.post("/search", response_model=list[SearchHit])
def search(req: SearchRequest) -> list[SearchHit]:
    # Ретривер может расширять пул (graph-hops) сверх top_k — на выдаче режем до top_k.
    hits = get_pipeline().retriever.search(req.query, top_k=req.top_k)[: req.top_k]
    return [
        SearchHit(
            citation=h.provision.citation,
            article_title=h.provision.article_title,
            text=h.provision.text,
            score=round(h.score, 4),
            method=h.method,
        )
        for h in hits
    ]
