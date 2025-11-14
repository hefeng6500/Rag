"""集中封装 LangChain 相关组件，便于在多个入口复用。"""
from __future__ import annotations

from datetime import datetime
from functools import lru_cache
from time import perf_counter
from typing import List

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from loguru import logger

from app.config import get_settings
from app.models.schemas import ChatResponse, DocumentChunk
from app.services.vectorstore import VectorStoreManager


class RagPipeline:
    """对外暴露切分、向量化、检索与答案生成的统一接口。"""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.embeddings = self._build_embeddings()
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
        )
        self.vector_store = VectorStoreManager(self.embeddings)

    def _build_embeddings(self) -> Embeddings:
        """使用 HuggingFace 模型，避免依赖云端 API。"""

        logger.info("加载嵌入模型：%s", self.settings.embedding_model)
        return HuggingFaceEmbeddings(
            model_name=self.settings.embedding_model,
            model_kwargs={"device": self.settings.embedding_device},
        )

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """切分原始文档，输出 LangChain Document 列表。"""

        return self.splitter.split_documents(documents)

    def index_documents(self, documents: List[Document]) -> int:
        """写入向量数据库。"""

        return self.vector_store.upsert_documents(documents)

    def should_query_store(self, query: str) -> bool:
        """简单的启发式判断是否需要检索知识库。"""

        normalized = query.strip()
        if len(normalized) >= self.settings.auto_retrieval_min_chars:
            return True
        return any(keyword in normalized for keyword in self.settings.auto_retrieval_keywords)

    def similarity_search(self, query: str, k: int) -> List[Document]:
        """执行 Milvus 检索。"""

        return self.vector_store.similarity_search(query, k)

    def generate_answer(self, query: str, documents: List[Document]) -> str:
        """基于检索结果生成可读答案。"""

        if not documents:
            return (
                "当前知识库暂无匹配内容，我将根据已有上下文进行推理："
                f"{query}。如需更准确的结果，请先上传相关资料。"
            )
        bullet = "\n".join(
            f"- 来自《{doc.metadata.get('source', '未知来源')}》：{doc.page_content[:160]}" for doc in documents
        )
        return (
            f"针对“{query}”，从知识库中检索到如下重点：\n{bullet}\n"
            "请结合以上要点完成决策或继续提问。"
        )

    def documents_to_chunks(self, documents: List[Document]) -> List[DocumentChunk]:
        """将 LangChain Document 转为 API 需要的结构。"""

        chunks: List[DocumentChunk] = []
        for index, doc in enumerate(documents):
            metadata = doc.metadata or {}
            uploaded_at = metadata.get("uploaded_at")
            if isinstance(uploaded_at, str):
                uploaded_time = datetime.fromisoformat(uploaded_at)
            elif isinstance(uploaded_at, datetime):
                uploaded_time = uploaded_at
            else:
                uploaded_time = datetime.utcnow()
            chunk_id = metadata.get("chunk_id") or f"{metadata.get('document_id', 'unknown')}_{index}"
            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    document_id=metadata.get("document_id", "unknown"),
                    content=doc.page_content,
                    source=metadata.get("source", "未知来源"),
                    page=metadata.get("page"),
                    uploaded_at=uploaded_time,
                )
            )
        return chunks

    def chat(self, query: str, top_k: int) -> ChatResponse:
        """统一处理聊天请求。"""

        start = perf_counter()
        retrieval_used = self.should_query_store(query)
        documents = self.similarity_search(query, top_k) if retrieval_used else []
        answer = self.generate_answer(query, documents)
        elapsed = (perf_counter() - start) * 1000
        sources = self.documents_to_chunks(documents)
        return ChatResponse(
            answer=answer,
            sources=sources,
            retrieval_used=retrieval_used,
            latency_ms=round(elapsed, 2),
        )


@lru_cache
def get_pipeline() -> RagPipeline:
    """以单例形式暴露管道，避免重复初始化大模型。"""

    return RagPipeline()
