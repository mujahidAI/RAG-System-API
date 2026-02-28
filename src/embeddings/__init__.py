"""Embeddings module for generating document and query embeddings.

This module provides the embedding model wrapper for the RAG pipeline,
supporting various HuggingFace models with batch processing.
"""

from src.embeddings.embedder import Embedder, get_embedder

__all__ = [
    "Embedder",
    "get_embedder",
]
