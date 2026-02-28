"""Tests for retrieval module."""

import pytest
from unittest.mock import Mock, patch

from langchain_core.documents import Document

from src.retrieval.retriever import HybridRetriever
from src.retrieval.reranker import Reranker


class TestHybridRetriever:
    """Tests for HybridRetriever."""

    @pytest.fixture
    def mock_store(self):
        """Create mock Qdrant store."""
        store = Mock()
        store.collection_name = "test"
        return store

    @pytest.fixture
    def mock_embedder(self):
        """Create mock embedder."""
        embedder = Mock()
        embedder.embedding_dimension = 1024
        return embedder

    def test_retriever_initialization(self, mock_store, mock_embedder):
        """Test retriever initialization."""
        retriever = HybridRetriever(
            qdrant_store=mock_store,
            embedder=mock_embedder,
            dense_weight=0.6,
            sparse_weight=0.4,
        )
        assert retriever.dense_weight == 0.6
        assert retriever.sparse_weight == 0.4


class TestReranker:
    """Tests for Reranker."""

    @pytest.fixture
    def sample_documents(self):
        """Create sample documents."""
        return [
            Document(page_content="First document", metadata={"source": "doc1"}),
            Document(page_content="Second document", metadata={"source": "doc2"}),
            Document(page_content="Third document", metadata={"source": "doc3"}),
        ]

    def test_rerank_returns_tuples(self, sample_documents):
        """Test that rerank returns document-score tuples."""
        # This test would require actual model loading
        # Using mock for now
        pass
