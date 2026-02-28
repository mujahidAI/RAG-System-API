"""Embedding model wrapper for document and query embeddings.

This module provides a unified interface for generating embeddings using
HuggingFace models with configurable batch sizes and caching.
"""

from typing import Any, Callable, Optional

from langchain_core.embeddings import Embeddings
from langchain_huggingface import HuggingFaceEmbeddings

from src.utils.logger import get_logger
from src.utils.config import get_settings

logger = get_logger(__name__)


class Embedder(Embeddings):
    """Wrapper for embedding model with batch processing support.

    Provides unified interface for document and query embeddings
    using HuggingFace models with configurable batch processing.
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        device: Optional[str] = None,
        batch_size: Optional[int] = None,
        normalize_embeddings: bool = True,
        encode_kwargs: Optional[dict[str, Any]] = None,
    ):
        """Initialize the embedder.

        Args:
            model_name: HuggingFace model name
            device: Device to use (cpu/cuda)
            batch_size: Batch size for encoding
            normalize_embeddings: Whether to normalize embeddings
            encode_kwargs: Additional encoding arguments
        """
        settings = get_settings()

        self.model_name = model_name or settings.embedding.model_name
        self.device = device or settings.embedding.device
        self.batch_size = batch_size or settings.embedding.batch_size

        self.encode_kwargs = encode_kwargs or {
            "normalize_embeddings": normalize_embeddings,
        }

        logger.info(
            "Initializing embedding model",
            extra={
                "model_name": self.model_name,
                "device": self.device,
                "batch_size": self.batch_size,
            },
        )

        self._embeddings_model = HuggingFaceEmbeddings(
            model_name=self.model_name,
            model_kwargs={"device": self.device},
            encode_kwargs=self.encode_kwargs,
        )

        self._embedding_dimension = None

        logger.info("Embedding model initialized", extra={"model_name": self.model_name})

    @property
    def embedding_dimension(self) -> int:
        """Get the dimension of the embedding vectors.

        Returns:
            Dimension of embedding vectors
        """
        if self._embedding_dimension is None:
            test_embedding = self.embed_query("test")
            self._embedding_dimension = len(test_embedding)

            logger.info(
                "Embedding dimension determined", extra={"dimension": self._embedding_dimension}
            )

        return self._embedding_dimension

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of documents.

        Args:
            texts: List of document texts

        Returns:
            List of embedding vectors
        """
        logger.info(
            "Embedding documents",
            extra={"document_count": len(texts), "batch_size": self.batch_size},
        )

        embeddings = self._embeddings_model.embed_documents(texts)

        logger.info(
            "Documents embedded",
            extra={
                "document_count": len(texts),
                "embedding_dim": len(embeddings[0]) if embeddings else 0,
            },
        )

        return embeddings

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query.

        Args:
            text: Query text

        Returns:
            Query embedding vector
        """
        return self._embeddings_model.embed_query(text)

    def embed_documents_batched(
        self, texts: list[str], callback: Optional[Callable[[int, int], None]] = None
    ) -> list[list[float]]:
        """Embed documents with explicit batching.

        Args:
            texts: List of document texts
            callback: Optional callback(batch_idx, total_batches)

        Returns:
            List of embedding vectors
        """
        all_embeddings = []
        total_batches = (len(texts) + self.batch_size - 1) // self.batch_size

        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            batch_idx = i // self.batch_size

            logger.debug(
                "Processing batch",
                extra={
                    "batch_idx": batch_idx,
                    "total_batches": total_batches,
                    "batch_size": len(batch),
                },
            )

            batch_embeddings = self.embed_documents(batch)
            all_embeddings.extend(batch_embeddings)

            if callback:
                callback(batch_idx, total_batches)

        return all_embeddings

    def embed_with_metadata(
        self, documents: list[dict[str, Any]]
    ) -> tuple[list[list[float]], list[dict[str, Any]]]:
        """Embed documents while preserving metadata.

        Args:
            documents: List of dicts with 'page_content' and 'metadata'

        Returns:
            Tuple of (embeddings, metadata_list)
        """
        texts = [doc["page_content"] for doc in documents]
        embeddings = self.embed_documents(texts)
        metadata = [doc.get("metadata", {}) for doc in documents]

        return embeddings, metadata

    def get_embedding_stats(self) -> dict[str, Any]:
        """Get statistics about the embedding model.

        Returns:
            Dictionary with model statistics
        """
        return {
            "model_name": self.model_name,
            "device": self.device,
            "batch_size": self.batch_size,
            "embedding_dimension": self.embedding_dimension,
            "normalize_embeddings": self.encode_kwargs.get("normalize_embeddings", True),
        }


def get_embedder() -> Embedder:
    """Get a configured Embedder instance.

    Returns:
        Configured Embedder instance
    """
    settings = get_settings()

    return Embedder(
        model_name=settings.embedding.model_name,
        device=settings.embedding.device,
        batch_size=settings.embedding.batch_size,
    )
