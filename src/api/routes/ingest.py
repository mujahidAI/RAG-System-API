"""Ingestion route for document processing.

This module provides the POST /ingest endpoint for loading and indexing documents.
"""

from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, status

from src.api.schemas import IngestRequest, IngestResponse
from src.ingestion.chunker import TextChunker
from src.ingestion.cleaner import TextCleaner
from src.ingestion.loader import DocumentLoader
from src.embeddings.embedder import Embedder
from src.vectorstore.qdrant_store import QdrantStore
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/ingest",
    tags=["Ingestion"],
)


def get_components() -> tuple[DocumentLoader, TextCleaner, TextChunker, Embedder, QdrantStore]:
    """Get required components for ingestion."""
    from src.embeddings.embedder import get_embedder
    from src.vectorstore.qdrant_store import get_qdrant_store

    loader = DocumentLoader()
    cleaner = TextCleaner()
    chunker = TextChunker()
    embedder = get_embedder()
    store = get_qdrant_store(embedder=embedder)

    return loader, cleaner, chunker, embedder, store


@router.post("", response_model=IngestResponse, summary="Ingest documents")
async def ingest_documents(request: IngestRequest) -> IngestResponse:
    """Ingest documents from files or directory.

    Args:
        request: Ingest request with file paths or directory

    Returns:
        IngestResponse with status and counts
    """
    logger.info(
        "Ingest request received",
        extra={
            "directory": request.directory_path,
            "file_count": len(request.file_paths) if request.file_paths else 0,
        },
    )

    try:
        loader, cleaner, chunker, embedder, store = get_components()

        if not request.directory_path and not request.file_paths:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either directory_path or file_paths must be provided",
            )

        documents = []

        if request.directory_path:
            dir_path = Path(request.directory_path)
            documents = loader.load_directory(dir_path)
        elif request.file_paths:
            for file_path in request.file_paths:
                docs = loader.load_file(Path(file_path))
                documents.extend(docs)

        if not documents:
            return IngestResponse(
                success=False,
                message="No documents found",
                collection_name=store.collection_name,
            )

        logger.info("Cleaning documents")
        documents = cleaner.clean_documents(documents)

        logger.info("Chunking documents")
        chunks = chunker.chunk_documents(documents)

        logger.info("Upserting to vector store")
        result = store.upsert_documents(
            chunks,
            batch_size=request.batch_size,
        )

        return IngestResponse(
            success=True,
            message=f"Successfully indexed {result['upserted_count']} chunks",
            documents_loaded=len(documents),
            documents_indexed=result["upserted_count"],
            collection_name=store.collection_name,
        )

    except Exception as e:
        logger.error("Ingestion failed", extra={"error": str(e)})
        # Try to get collection_name; fall back to default if components failed
        try:
            collection_name = store.collection_name
        except Exception:
            from src.utils.config import get_settings

            collection_name = get_settings().qdrant.collection_name
        return IngestResponse(
            success=False,
            message="Ingestion failed",
            collection_name=collection_name,
            error=str(e),
        )
