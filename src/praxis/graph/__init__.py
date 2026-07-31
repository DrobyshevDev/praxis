"""GraphRAG по перекрёстным ссылкам норм (multi-hop по цепочкам «статья→статья»)."""

from .expander import GraphExpandingRetriever
from .refs import build_reference_graph, extract_references

__all__ = ["GraphExpandingRetriever", "build_reference_graph", "extract_references"]
