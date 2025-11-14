"""FastAPI entry point for the LangChain Milvus RAG service."""
from __future__ import annotations

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.models.schemas import SearchRequest, SearchResult, UploadResponse
from app.services import document_service, rag_pipeline

settings = get_settings()
app = FastAPI(title=settings.project_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    """Expose a lightweight probe for orchestration platforms."""

    return {"status": "ok", "service": settings.project_name}


@app.post(f"{settings.api_v1_prefix}/documents", response_model=list[UploadResponse])
async def upload_documents(files: list[UploadFile] = File(...)) -> list[UploadResponse]:
    """Persist uploaded documents and produce placeholder chunk metadata."""

    chunks = document_service.prepare_chunks(files)
    # Placeholder response; later revisions will persist chunk embeddings to Milvus.
    return [
        UploadResponse(document_id=str(index), filename=file.filename, status="stored")
        for index, file in enumerate(files)
    ]


@app.post(f"{settings.api_v1_prefix}/search", response_model=SearchResult)
async def search_documents(payload: SearchRequest) -> SearchResult:
    """Return a stubbed answer referencing uploaded chunks."""

    # Stage one operates entirely on placeholder chunks.
    documents = rag_pipeline.chunks_to_documents([])
    answer = rag_pipeline.build_stub_answer(payload.query, documents)
    return SearchResult(answer=answer, sources=[])
