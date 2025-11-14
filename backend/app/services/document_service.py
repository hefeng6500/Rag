"""Utility functions that manage uploads and document parsing.

Stage one focuses on building a predictable, well-instrumented pipeline. Actual
parsers for DOCX/PDF/IMG files will be integrated in later stages; the helpers
below merely store files and generate traceable metadata structures that can be
consumed by LangChain components.
"""
from __future__ import annotations

import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

from fastapi import UploadFile
from loguru import logger

from app.config import get_settings
from app.models.schemas import DocumentChunk


def persist_upload(file: UploadFile) -> Path:
    """Write the incoming upload to disk and return its location."""

    settings = get_settings()
    upload_dir = Path(__file__).resolve().parents[1] / settings.upload_dir
    upload_dir.mkdir(parents=True, exist_ok=True)

    document_id = uuid.uuid4().hex
    destination = upload_dir / f"{document_id}_{file.filename}"
    logger.debug("Saving upload %s to %s", file.filename, destination)
    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return destination


def stub_chunk_generator(file_path: Path) -> Iterable[DocumentChunk]:
    """Generate placeholder chunks until real parsers are connected.

    The placeholder mirrors the metadata shape expected by the retriever. Once
    actual parsing is available we can replace this function without touching
    the API layer.
    """

    uploaded_at = datetime.utcnow()
    yield DocumentChunk(
        content=f"Placeholder chunk for {file_path.name}.",
        source=str(file_path),
        page=None,
        uploaded_at=uploaded_at,
    )


def prepare_chunks(files: List[UploadFile]) -> List[DocumentChunk]:
    """Persist uploads and return normalized document chunks."""

    chunks: List[DocumentChunk] = []
    for file in files:
        stored_path = persist_upload(file)
        chunks.extend(list(stub_chunk_generator(stored_path)))
    logger.info("Prepared %s placeholder chunks", len(chunks))
    return chunks
