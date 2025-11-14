"""LangChain workflow orchestration helpers."""
from __future__ import annotations

from typing import List

from langchain.schema import Document

from app.models.schemas import DocumentChunk


def chunks_to_documents(chunks: List[DocumentChunk]) -> List[Document]:
    """Convert API-level chunks to LangChain ``Document`` objects."""

    return [
        Document(page_content=chunk.content, metadata={"source": chunk.source, "page": chunk.page})
        for chunk in chunks
    ]


def build_stub_answer(query: str, documents: List[Document]) -> str:
    """Return a deterministic answer until the LLM chain is wired up.

    The placeholder keeps the API functional for the front end without
    requiring access to an embedding provider during stage one.
    """

    sources = ", ".join(doc.metadata.get("source", "unknown") for doc in documents)
    return f"[stubbed-response] '{query}' would be answered using: {sources}"
