"""FastAPI-приложение Praxis: открытый API (/v1) + веб-UI.

Одно API-ядро обслуживает все клиенты: веб-UI, будущие desktop/mobile и сторонних
ML-специалистов. CORS открыт (API только на чтение), интерактивная схема — на /docs,
машиночитаемая — на /openapi.json. Пайплайн строится один раз при первом обращении.
"""

from __future__ import annotations

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from .. import __version__
from ..config import config_from_env
from ..pipeline import build_pipeline
from ..sources import act_reference, verify_url
from ..tasks import (
    build_claim,
    build_lawsuit,
    claim_applicable,
    court_fee,
    interest_395,
    penalty,
    review_contract,
)
from .schemas import (
    AnswerOut,
    AskRequest,
    BasisOut,
    CaseOut,
    CitationOut,
    ClaimOut,
    ClaimRequest,
    ContractCheckOut,
    ContractRequest,
    ContractReviewOut,
    FeeOut,
    FeeRequest,
    InterestOut,
    InterestRequest,
    PenaltyOut,
    PenaltyRequest,
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
            source_url=verify_url(c.provision.act.id, c.provision.article_number),
            act_ref=act_reference(c.provision.act.number, c.provision.act.date),
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
        claim_applicable=claim_applicable(answer),
    )


@v1.post("/claim", response_model=ClaimOut, summary="Собрать досудебную претензию")
def claim(req: ClaimRequest) -> ClaimOut:
    """Готовая претензия по вопросу: обоснование из найденных норм + статутные блоки,
    факты — плейсхолдеры. Применимо к гражданско-потребительским вопросам."""
    answer = get_pipeline().answer(req.question)
    result = build_claim(answer)
    return ClaimOut(
        applicable=result.applicable,
        text=result.text,
        based_on=result.based_on,
        note=result.note,
        disclaimer=result.disclaimer,
    )


@v1.post("/lawsuit", response_model=ClaimOut, summary="Собрать исковое заявление")
def lawsuit(req: ClaimRequest) -> ClaimOut:
    """Исковое заявление по вопросу: обоснование из найденных норм + просительная
    часть, досудебный порядок, подсудность и госпошлина. Гражданско-потребительские
    вопросы; для потребителя — требования по ЗоЗПП (неустойка, штраф, моральный вред)."""
    result = build_lawsuit(get_pipeline().answer(req.question))
    return ClaimOut(
        applicable=result.applicable, text=result.text, based_on=result.based_on,
        note=result.note, disclaimer=result.disclaimer,
    )


@v1.post("/penalty", response_model=PenaltyOut, summary="Калькулятор неустойки (ЗоЗПП)")
def calc_penalty(req: PenaltyRequest) -> PenaltyOut:
    """Неустойка потребителю за просрочку: товар 1%/день (ст. 23 ЗоЗПП),
    услуга 3%/день с потолком в цену услуги (ст. 28 ЗоЗПП)."""
    try:
        r = penalty(req.price, req.days, kind=req.kind)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return PenaltyOut(
        amount=r.amount, per_day=r.per_day, days=r.days, rate_pct=r.rate_pct,
        capped=r.capped, breakdown=r.breakdown,
        basis=BasisOut(citation=r.basis.citation, source_url=r.basis.source_url, note=r.basis.note),
    )


@v1.post("/fee", response_model=FeeOut, summary="Калькулятор госпошлины (НК РФ)")
def calc_fee(req: FeeRequest) -> FeeOut:
    """Госпошлина при подаче имущественного иска в суд общей юрисдикции
    (ст. 333.19 НК, ред. 259-ФЗ). Для исков о защите прав потребителей —
    льгота ст. 333.36 НК (до 1 000 000 ₽ пошлина не уплачивается)."""
    try:
        r = court_fee(req.amount, consumer=req.consumer)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return FeeOut(
        fee=r.fee, exempt=r.exempt, breakdown=r.breakdown,
        basis=BasisOut(citation=r.basis.citation, source_url=r.basis.source_url, note=r.basis.note),
    )


@v1.post("/contract", response_model=ContractReviewOut, summary="Чек-лист договора")
def contract(req: ContractRequest) -> ContractReviewOut:
    """Проверка текста договора по нормам: существенные условия и рискованные пункты,
    каждый со ссылкой на статью. Прозрачные правила, не заменяет юриста."""
    r = review_contract(req.text)
    return ContractReviewOut(
        ok=r.ok,
        checks=[
            ContractCheckOut(label=c.label, status=c.status, citation=c.citation,
                             source_url=c.source_url, note=c.note)
            for c in r.checks
        ],
        summary=r.summary, note=r.note, disclaimer=r.disclaimer,
    )


@v1.post("/interest", response_model=InterestOut, summary="Калькулятор процентов (ст. 395 ГК)")
def calc_interest(req: InterestRequest) -> InterestOut:
    """Проценты за пользование чужими денежными средствами (ст. 395 ГК) за период с
    неизменной ключевой ставкой ЦБ (ставку задаёт пользователь: она регулярно меняется)."""
    try:
        r = interest_395(req.principal, req.rate_pct, req.days)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return InterestOut(
        amount=r.amount, breakdown=r.breakdown,
        basis=BasisOut(citation=r.basis.citation, source_url=r.basis.source_url, note=r.basis.note),
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
