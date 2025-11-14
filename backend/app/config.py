"""后台配置中心，所有运行期参数均集中在此处。"""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """定义所有可通过环境变量覆盖的配置。"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    project_name: str = "LangChain Milvus RAG"
    api_v1_prefix: str = "/api/v1"

    # Milvus 连接设置
    milvus_host: str = "localhost"
    milvus_port: str = "19530"
    milvus_collection: str = "rag_documents"

    # 存储目录
    upload_dir: Path = Path("backend/storage/uploads")
    registry_filename: str = "registry.json"

    # 文本切分与向量化策略
    chunk_size: int = 800
    chunk_overlap: int = 150
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    embedding_device: str = "cpu"

    # RAG 控制策略
    auto_retrieval_min_chars: int = 16
    auto_retrieval_keywords: tuple[str, ...] = ("文档", "资料", "文件", "报告")


@lru_cache
def get_settings() -> Settings:
    """返回缓存后的配置对象，避免重复解析环境变量。"""

    settings = Settings()
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    return settings
