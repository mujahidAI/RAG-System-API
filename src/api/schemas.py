"""Pydantic schemas for API request/response models.

This module defines all request and response models for the FastAPI endpoints.
"""

from typing import Any, Optional

from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    """Request model for document ingestion."""

    directory_path: Optional[str] = Field(
        default=None, description="Path to directory containing documents"
    )
    file_paths: Optional[list[str]] = Field(
        default=None, description="List of specific file paths to ingest"
    )
    batch_size: int = Field(default=100, description="Batch size for embedding")


class IngestResponse(BaseModel):
    """Response model for document ingestion."""

    success: bool
    message: str
    documents_loaded: int = 0
    documents_indexed: int = 0
    collection_name: str
    error: Optional[str] = None


class QueryRequest(BaseModel):
    """Request model for query endpoint."""

    question: str = Field(..., description="User question", min_length=1, max_length=1000)
    top_k: int = Field(default=4, description="Number of documents to retrieve", ge=1, le=20)
    include_sources: bool = Field(
        default=True, description="Whether to include source documents in response"
    )


class SourceDocument(BaseModel):
    """Source document model."""

    content: str
    source: str
    chunk_index: int


class QueryResponse(BaseModel):
    """Response model for query endpoint."""

    success: bool
    answer: str
    sources: list[SourceDocument] = []
    context_doc_count: int = 0
    latency_ms: float = 0.0
    error: Optional[str] = None


class EvaluateRequest(BaseModel):
    """Request model for evaluation endpoint."""

    questions: list[str] = Field(
        ..., description="List of questions to evaluate", min_length=1, max_length=50
    )
    output_path: Optional[str] = Field(default=None, description="Path to save evaluation report")


class EvaluateResponse(BaseModel):
    """Response model for evaluation endpoint."""

    success: bool
    metrics: dict[str, float] = {}
    result_count: int = 0
    report_path: Optional[str] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str
    version: str
    services: dict[str, str]
