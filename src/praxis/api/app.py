"""FastAPI-приложение Praxis: открытый API (/v1) + веб-UI.

Одно API-ядро обслуживает все клиенты: веб-UI, будущие desktop/mobile и сторонних
ML-специалистов. CORS открыт (API только на чтение), интерактивная схема — на /docs,
машиночитаемая — на /openapi.json. Пайплайн строится один раз при первом обращении.
"""

from __future__ import annotations

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from .. import __version__
from ..config import config_from_env
from ..pipeline import build_pipeline
from .schemas import (
    AnswerOut,
    AskRequest,
    CaseOut,
    CitationOut,
    SearchHit,
    SearchRequest,
    StatsOut,
)
from .ui import INDEX_HTML

app = FastAPI(
    title="Praxis API",
    version=__version__,
    description=(
        "Юридический ассистент по праву РФ с проверяемыми цитатами. "
        "Открытый API на чтение: /v1/ask отвечает со ссылками на нормы и проверкой "
        "цитат, /v1/search — сырой поиск по корпусу. Схема: /openapi.json."
    ),
    contact={"name": "DrobyshevDev", "url": "https://github.com/DrobyshevDev/praxis"},
    license_info={"name": "Apache-2.0"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

_pipeline = None


def get_pipeline():
    global _pipeline
    if _pipeline is None:
        _pipeline = build_pipeline(config=config_from_env())
    return _pipeline


@app.get("/health", tags=["service"])
def health() -> dict:
    return {"status": "ok", "version": __version__}


_stats: StatsOut | None = None


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index() -> str:
    return INDEX_HTML


v1 = APIRouter(prefix="/v1", tags=["v1"])


@v1.post("/ask", response_model=AnswerOut, summary="Ответ на юридический вопрос")
def ask(req: AskRequest) -> AnswerOut:
    """Вопрос → ответ со ссылками на нормы, span-подсветкой, проверкой цитат,
    трейсом рассуждения и релевантной судебной практикой."""
    answer = get_pipeline().answer(req.question)
    verdict_by_id = {
        vc.citation.provision.id: vc.verdict.value for vc in answer.verified
    }
    citations = [
        CitationOut(
            id=c.provision.id,
            citation=c.provision.citation,
            code=c.provision.act.short_title,
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


@v1.post("/search", response_model=list[SearchHit], summary="Поиск норм по запросу")
def search(req: SearchRequest) -> list[SearchHit]:
    """Сырой поиск по корпусу (для ML-специалистов): гибрид + reranker, без генерации."""
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


@v1.get("/stats", response_model=StatsOut, summary="Статистика корпуса")
def stats() -> StatsOut:
    global _stats
    if _stats is None:
        from ..ingest import load_sample_provisions

        provisions = load_sample_provisions()
        _stats = StatsOut(
            acts=len({p.act.id for p in provisions}),
            provisions=len(provisions),
            codes=sorted({p.act.short_title for p in provisions}),
        )
    return _stats


app.include_router(v1)
