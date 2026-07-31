"""Настройки пайплайна из окружения (для API/CLI)."""

from __future__ import annotations

import os

from .agent.self_rag import SelfRAGConfig


def config_from_env() -> SelfRAGConfig:
    return SelfRAGConfig(
        answer_top_k=int(os.environ.get("PRAXIS_ANSWER_TOP_K", "5")),
        max_rounds=int(os.environ.get("PRAXIS_MAX_ROUNDS", "2")),
        rerank_top_k=int(os.environ.get("PRAXIS_RERANK_TOP_K", "6")),
    )
