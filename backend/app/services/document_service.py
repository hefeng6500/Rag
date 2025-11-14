"""负责处理文件上传、解析以及元数据登记。"""
from __future__ import annotations

import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import UploadFile
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredExcelLoader,
    UnstructuredImageLoader,
    UnstructuredPowerPointLoader,
    UnstructuredWordDocumentLoader,
)
from langchain_core.documents import Document
from loguru import logger

from app.config import get_settings
from app.models.schemas import DocumentRecord, UploadResponse
from app.services.rag_pipeline import get_pipeline

SETTINGS = get_settings()
REGISTRY_PATH = SETTINGS.upload_dir / SETTINGS.registry_filename


class DocumentRegistry:
    """基于 JSON 文件的简单注册表，用于记录历史上传。"""

    def __init__(self, registry_path: Path) -> None:
        self.registry_path = registry_path
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> List[DocumentRecord]:
        if not self.registry_path.exists():
            return []
        raw_text = self.registry_path.read_text(encoding="utf-8") or "[]"
        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError as exc:  # pragma: no cover - 防御性容错
            logger.warning("注册表内容异常，将返回空列表：%s", exc)
            return []
        return [DocumentRecord(**item) for item in data]

    def save(self, records: List[DocumentRecord]) -> None:
        payload = [record.model_dump(mode="json") for record in records]
        self.registry_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def upsert(self, record: DocumentRecord) -> None:
        records = self.load()
        records = [item for item in records if item.document_id != record.document_id]
        records.append(record)
        records.sort(key=lambda rec: rec.uploaded_at, reverse=True)
        self.save(records)

    def list_documents(self) -> List[DocumentRecord]:
        return self.load()


REGISTRY = DocumentRegistry(REGISTRY_PATH)


def _destination_for(filename: str, document_id: str) -> Path:
    suffix = Path(filename).suffix
    safe_suffix = suffix if suffix else ""
    return SETTINGS.upload_dir / f"{document_id}{safe_suffix}"


def persist_upload(file: UploadFile, document_id: str) -> Path:
    """将上传文件写入磁盘并返回保存路径。"""

    destination = _destination_for(file.filename or "upload", document_id)
    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    logger.info("文件 %s 已保存到 %s", file.filename, destination)
    return destination


def _build_record(file: UploadFile, stored_path: Path, document_id: str) -> DocumentRecord:
    stats = stored_path.stat()
    return DocumentRecord(
        document_id=document_id,
        filename=file.filename or stored_path.name,
        content_type=file.content_type,
        size=stats.st_size,
        stored_path=str(stored_path),
        uploaded_at=datetime.utcnow(),
    )


def _loader_for(path: Path):
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return PyPDFLoader(str(path))
    if suffix in {".doc", ".docx"}:
        return UnstructuredWordDocumentLoader(str(path))
    if suffix in {".ppt", ".pptx"}:
        return UnstructuredPowerPointLoader(str(path))
    if suffix in {".xls", ".xlsx"}:
        return UnstructuredExcelLoader(str(path))
    if suffix in {".png", ".jpg", ".jpeg"}:
        return UnstructuredImageLoader(str(path))
    return TextLoader(str(path), autodetect_encoding=True)


def _load_documents(path: Path, record: DocumentRecord) -> List[Document]:
    loader = _loader_for(path)
    raw_docs = loader.load()
    for doc in raw_docs:
        doc.metadata.setdefault("document_id", record.document_id)
        doc.metadata.setdefault("source", record.filename)
        doc.metadata.setdefault("uploaded_at", record.uploaded_at.isoformat())
    return raw_docs


def ingest_uploads(files: List[UploadFile]) -> List[UploadResponse]:
    """完整的上传→解析→切分→写入 Milvus 流程。"""

    pipeline = get_pipeline()
    responses: List[UploadResponse] = []
    for file in files:
        document_id = uuid.uuid4().hex
        stored_path = persist_upload(file, document_id)
        record = _build_record(file, stored_path, document_id)
        REGISTRY.upsert(record)
        documents = _load_documents(stored_path, record)
        chunks = pipeline.split_documents(documents)
        for index, chunk in enumerate(chunks):
            chunk.metadata.setdefault("document_id", record.document_id)
            chunk.metadata.setdefault("source", record.filename)
            chunk.metadata.setdefault("uploaded_at", record.uploaded_at.isoformat())
            chunk.metadata.setdefault("page", chunk.metadata.get("page"))
            chunk.metadata["chunk_id"] = f"{record.document_id}_{index}"
        indexed = pipeline.index_documents(chunks)
        responses.append(UploadResponse(document=record, chunks_indexed=indexed))
        logger.success("%s 已索引 %s 条切片", record.filename, indexed)
    return responses


def list_documents() -> List[DocumentRecord]:
    """返回本地注册表中的全部文档。"""

    return REGISTRY.list_documents()
