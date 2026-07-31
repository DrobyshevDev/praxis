"""Agentic self-RAG оркестратор (glass-box луп, философия glia)."""

from .self_rag import SelfRAG, SelfRAGConfig

__all__ = ["GliaLegalAgent", "SelfRAG", "SelfRAGConfig"]


def __getattr__(name: str):
    # GliaLegalAgent тянет glia лениво — импорт agent не требует установленной glia.
    if name == "GliaLegalAgent":
        from .glia_agent import GliaLegalAgent

        return GliaLegalAgent
    raise AttributeError(name)
