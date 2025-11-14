"""Lightweight wrapper around Milvus collections.

This stage only establishes the client connection and schema bootstrap logic.
Future stages will evolve this abstraction to manage indexes, TTL policies, and
multi-tenant namespaces.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List

from loguru import logger
from pymilvus import (Collection, CollectionSchema, DataType, FieldSchema,
                      MilvusException, connections, utility)

from app.config import get_settings


@dataclass
class MilvusVectorStore:
    """Encapsulates Milvus connectivity and simplified CRUD helpers."""

    collection_name: str

    def __post_init__(self) -> None:
        settings = get_settings()
        connections.connect(alias="default", host=settings.milvus_host, port=settings.milvus_port)
        logger.info("Connected to Milvus at %s:%s", settings.milvus_host, settings.milvus_port)
        self._bootstrap_collection()

    @property
    def collection(self) -> Collection:
        """Return the Milvus collection handle, creating it if necessary."""

        return Collection(self.collection_name)

    def _bootstrap_collection(self) -> None:
        """Create the collection schema the first time the service runs."""

        if utility.has_collection(self.collection_name):
            return

        logger.info("Creating Milvus collection %s", self.collection_name)
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=2048),
            FieldSchema(name="metadata", dtype=DataType.JSON),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536),
        ]
        schema = CollectionSchema(fields=fields, description="RAG document chunks")
        Collection(name=self.collection_name, schema=schema)

    def insert(self, payloads: List[Any]) -> None:
        """Placeholder insert helper for stage one.

        ``payloads`` is expected to mirror the order of fields configured above.
        Later stages will replace this primitive method with LangChain's
        Milvus vector store integration.
        """

        try:
            self.collection.insert(payloads)
        except MilvusException as exc:
            logger.error("Milvus insert failed: %s", exc)
            raise
