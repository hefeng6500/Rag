"""Pydantic schemas shared by multiple API routes."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class UploadResponse(BaseModel):
    """Metadata returned after a successful document upload."""

    document_id: str
    filename: str
    status: str


class SearchRequest(BaseModel):
    """Payload describing a question asked by the front end."""

    query: str
    top_k: int = 4
    include_sources: bool = True


class DocumentChunk(BaseModel):
    """Normalized representation of a parsed document chunk."""

    content: str
    source: str
    page: Optional[int] = None
    uploaded_at: datetime


class SearchResult(BaseModel):
    """Response payload summarizing the model answer and retrieved sources."""

    answer: str
    sources: List[DocumentChunk] = []
