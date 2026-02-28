"""Configuration management for the RAG system.

This module provides centralized configuration using Pydantic Settings,
loading from environment variables with validation and type conversion.
All configuration values are defined here with sensible defaults.
"""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class QdrantSettings(BaseSettings):
    """Qdrant vector database configuration."""

    host: str = Field(default="localhost", description="Qdrant host")
    port: int = Field(default=6333, description="Qdrant REST port")
    grpc_port: int = Field(default=6334, description="Qdrant gRPC port")
    collection_name: str = Field(default="rag_documents", description="Collection name")
    api_key: Optional[str] = Field(default=None, description="API key for authentication")


class EmbeddingSettings(BaseSettings):
    """Embedding model configuration."""

    model_name: str = Field(default="BAAI/bge-large-en-v1.5", description="HuggingFace model name")
    device: str = Field(default="cpu", description="Device for embeddings (cpu/cuda)")
    batch_size: int = Field(default=32, description="Batch size for embedding")
    vector_size: int = Field(default=1024, description="Embedding vector dimension")


class LLMSettings(BaseSettings):
    """LLM configuration for generation."""

    provider: str = Field(default="groq", description="LLM provider (groq/huggingface)")
    groq_api_key: Optional[str] = Field(default=None, description="Groq API key")
    groq_model: str = Field(
        default="moonshotai/kimi-k2-instruct-0905", description="Groq model name"
    )
    temperature: float = Field(default=0.1, description="LLM temperature")
    max_tokens: int = Field(default=512, description="Max tokens to generate")


class RerankerSettings(BaseSettings):
    """Cross-encoder re-ranker configuration."""

    model_name: str = Field(
        default="cross-encoder/ms-marco-MiniLM-L-6-v2", description="Cross-encoder model name"
    )
    top_k: int = Field(default=3, description="Number of results to return after reranking")


class RetrievalSettings(BaseSettings):
    """Retrieval configuration."""

    top_k: int = Field(default=10, description="Number of documents to retrieve")
    dense_weight: float = Field(default=0.6, description="Weight for dense retrieval")
    sparse_weight: float = Field(default=0.4, description="Weight for sparse (BM25) retrieval")


class QueryTransformSettings(BaseSettings):
    """Query transformation configuration."""

    enable_hyde: bool = Field(default=False, description="Enable HyDE query transformation")
    enable_multi_query: bool = Field(default=False, description="Enable multi-query expansion")
    multi_query_count: int = Field(default=3, description="Number of query variants to generate")


class ChunkingSettings(BaseSettings):
    """Text chunking configuration."""

    chunk_size: int = Field(default=512, description="Chunk size in tokens")
    chunk_overlap: int = Field(default=50, description="Overlap between chunks in tokens")


class APISettings(BaseSettings):
    """FastAPI server configuration."""

    host: str = Field(default="0.0.0.0", description="API host")
    port: int = Field(default=8000, description="API port")
    workers: int = Field(default=4, description="Number of worker processes")
    reload: bool = Field(default=False, description="Enable auto-reload")
    api_key: Optional[str] = Field(default=None, description="API key for authentication")


class EvalSettings(BaseSettings):
    """Evaluation configuration."""

    dataset_size: int = Field(default=20, description="Number of Q&A pairs to generate")
    output_path: str = Field(
        default="data/eval_report.json", description="Path to save evaluation report"
    )


class LoggingSettings(BaseSettings):
    """Logging configuration."""

    level: str = Field(default="INFO", description="Log level")
    format: str = Field(default="json", description="Log format (json/text)")


class DataSettings(BaseSettings):
    """Data paths configuration."""

    raw_path: Path = Field(default=Path("data/raw"), description="Raw data directory")
    processed_path: Path = Field(
        default=Path("data/processed"), description="Processed data directory"
    )


class Settings(BaseSettings):
    """Main application settings aggregating all sub-configurations."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    qdrant: QdrantSettings = Field(default_factory=QdrantSettings)
    embedding: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    reranker: RerankerSettings = Field(default_factory=RerankerSettings)
    retrieval: RetrievalSettings = Field(default_factory=RetrievalSettings)
    query_transform: QueryTransformSettings = Field(default_factory=QueryTransformSettings)
    chunking: ChunkingSettings = Field(default_factory=ChunkingSettings)
    api: APISettings = Field(default_factory=APISettings)
    eval: EvalSettings = Field(default_factory=EvalSettings)
    log: LoggingSettings = Field(default_factory=LoggingSettings)
    data: DataSettings = Field(default_factory=DataSettings)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance.

    This function uses lru_cache to ensure settings are only loaded once,
    making it safe to call multiple times throughout the application.

    Returns:
        Singleton Settings instance
    """
    return Settings()
