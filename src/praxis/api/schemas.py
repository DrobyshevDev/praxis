"""Pydantic-схемы HTTP-API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(5, ge=1, le=20)


class CitationOut(BaseModel):
    id: str
    citation: str
    article_number: str
    article_title: str
    text: str
    verdict: str | None = None
    span: list[int] | None = None  # [start, end) подтверждающего фрагмента в text


class CaseOut(BaseModel):
    citation: str
    court: str
    number: str
    date: str
    summary: str
    cited_articles: list[str]


class AnswerOut(BaseModel):
    question: str
    text: str
    confidence: float
    citations: list[CitationOut]
    unverified_claims: list[str]
    steps: list[str]
    related_cases: list[CaseOut] = []


class SearchHit(BaseModel):
    citation: str
    article_title: str
    text: str
    score: float
    method: str
