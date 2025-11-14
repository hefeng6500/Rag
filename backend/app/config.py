"""Application configuration helpers.

This module centralizes runtime configuration using ``pydantic-settings`` so that
all services (FastAPI, Milvus, LangChain embeddings) consume consistent values.
The defaults focus on local development, but every field can be overridden by
environment variables in production deployments.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed configuration values for the backend service."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    project_name: str = "LangChain Milvus RAG"
    api_v1_prefix: str = "/api/v1"

    # Milvus connection settings – values can be overridden by a managed cluster.
    milvus_host: str = "localhost"
    milvus_port: str = "19530"
    milvus_collection: str = "rag_documents"

    # Storage locations for uploaded artifacts.
    upload_dir: str = "storage/uploads"

    # LangChain defaults; embeddings/model providers can change per stage.
    embedding_model: str = "text-embedding-3-small"
    chunk_size: int = 800
    chunk_overlap: int = 120


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance to avoid repeated env parsing."""

    return Settings()
