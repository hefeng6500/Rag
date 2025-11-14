"""FastAPI 入口，负责编排 RAG 服务的 HTTP API。"""
from __future__ import annotations

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.models.schemas import ChatRequest, ChatResponse, DocumentListResponse, UploadResponse
from app.services import document_service
from app.services.rag_pipeline import get_pipeline

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
    """健康检查接口，供探活使用。"""

    return {"status": "ok", "service": settings.project_name}


@app.get(f"{settings.api_v1_prefix}/documents", response_model=DocumentListResponse)
def list_documents() -> DocumentListResponse:
    """返回已上传文档的历史记录，供前端侧边栏展示。"""

    return DocumentListResponse(documents=document_service.list_documents())


@app.post(f"{settings.api_v1_prefix}/documents", response_model=list[UploadResponse])
async def upload_documents(files: list[UploadFile] = File(...)) -> list[UploadResponse]:
    """上传并索引多种格式的文件。"""

    if not files:
        raise HTTPException(status_code=400, detail="未检测到可处理的文件")
    return document_service.ingest_uploads(files)


@app.post(f"{settings.api_v1_prefix}/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    """聊天端点，根据需要自动触发检索。"""

    pipeline = get_pipeline()
    return pipeline.chat(payload.message, payload.top_k)
