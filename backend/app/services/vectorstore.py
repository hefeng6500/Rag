"""Milvus 相关封装，统一处理连接与检索。"""
from __future__ import annotations

from typing import List

from langchain_community.vectorstores import Milvus
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from loguru import logger
from pymilvus import connections

from app.config import get_settings


class VectorStoreManager:
    """封装 Milvus 连接和 LangChain VectorStore 的常用操作。"""

    def __init__(self, embeddings: Embeddings) -> None:
        self.settings = get_settings()
        self.embeddings = embeddings
        self._connect()
        self.store = Milvus(
            embedding_function=self.embeddings,
            collection_name=self.settings.milvus_collection,
            connection_args={
                "host": self.settings.milvus_host,
                "port": self.settings.milvus_port,
                "alias": "default",
            },
            text_field="content",
            drop_old=False,
        )

    def _connect(self) -> None:
        """建立 Milvus 连接，重复调用也不会抛错。"""

        try:
            connections.connect(
                alias="default",
                host=self.settings.milvus_host,
                port=self.settings.milvus_port,
            )
            logger.info(
                "Milvus 已连接：%s:%s", self.settings.milvus_host, self.settings.milvus_port
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("Milvus 连接失败: %s", exc)
            raise

    def upsert_documents(self, documents: List[Document]) -> int:
        """写入或更新文档切片，并返回成功条数。"""

        if not documents:
            return 0
        logger.debug("准备写入 %s 条切片", len(documents))
        self.store.add_documents(documents)
        return len(documents)

    def similarity_search(self, query: str, k: int) -> List[Document]:
        """执行语义检索。"""

        if not query.strip():
            return []
        return self.store.similarity_search(query, k=k)
