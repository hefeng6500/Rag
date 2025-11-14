"""定义 FastAPI 所用到的 Pydantic 数据模型。"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class DocumentRecord(BaseModel):
    """描述一个已经存储并可检索的源文件。"""

    document_id: str
    filename: str
    content_type: Optional[str]
    size: int
    stored_path: str
    uploaded_at: datetime


class DocumentChunk(BaseModel):
    """标准化后的文档切片信息，便于追溯来源。"""

    chunk_id: str
    document_id: str
    content: str
    source: str
    page: Optional[int]
    uploaded_at: datetime


class UploadResponse(BaseModel):
    """上传完成后返回的反馈信息。"""

    document: DocumentRecord
    chunks_indexed: int
    status: str = "indexed"


class DocumentListResponse(BaseModel):
    """用于返回当前用户可见的文档清单。"""

    documents: List[DocumentRecord]


class ChatRequest(BaseModel):
    """前端在聊天页提交的内容。"""

    message: str
    top_k: int = 4


class ChatResponse(BaseModel):
    """聊天接口的统一返回结构。"""

    answer: str
    sources: List[DocumentChunk]
    retrieval_used: bool
    latency_ms: float
