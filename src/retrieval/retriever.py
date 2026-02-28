"""Hybrid retrieval combining dense and sparse (BM25) methods.

This module implements hybrid retrieval using an ensemble of dense
(semantic) and sparse (BM25) retrievers for improved recall.
"""

from typing import Optional

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_community.retrievers import BM25Retriever

from src.embeddings.embedder import Embedder
from src.vectorstore.qdrant_store import QdrantStore
from src.utils.logger import get_logger
from src.utils.config import get_settings

logger = get_logger(__name__)


class HybridRetriever:
    """Hybrid retriever combining dense and sparse methods.

    Combines:
    - Dense retrieval (semantic search via Qdrant)
    - Sparse retrieval (BM25 keyword search)

    Uses weighted ensemble with configurable weights.
    """

    def __init__(
        self,
        qdrant_store: QdrantStore,
        embedder: Embedder,
        dense_weight: float = 0.6,
        sparse_weight: float = 0.4,
        top_k: int = 10,
    ):
        """Initialize the hybrid retriever.

        Args:
            qdrant_store: Qdrant vector store instance.
            embedder: Embedding model instance.
            dense_weight: Weight for dense retrieval score (0-1).
            sparse_weight: Weight for sparse retrieval score (0-1).
            top_k: Number of candidates to retrieve before re-ranking.
        """
        settings = get_settings()

        self.qdrant_store = qdrant_store
        self.embedder = embedder
        self.dense_weight = dense_weight
        self.sparse_weight = sparse_weight
        self.top_k = top_k or settings.retrieval.top_k

        self._dense_retriever: Optional[BaseRetriever] = None
        self._sparse_retriever: Optional[BM25Retriever] = None
        self._documents: list[Document] = []

        logger.info(
            "HybridRetriever initialized",
            extra={
                "dense_weight": self.dense_weight,
                "sparse_weight": self.sparse_weight,
                "top_k": self.top_k,
            },
        )

    def set_documents(self, documents: list[Document]) -> None:
        """Set documents for BM25 sparse retrieval.

        Must be called before retrieve() if sparse retrieval is needed.
        Resets cached sparse and ensemble retrievers on update.

        Args:
            documents: List of LangChain Document objects to index.
        """
        self._documents = documents
        # Reset cached retrievers so they are rebuilt with new documents
        self._sparse_retriever = None

        logger.info(
            "Documents set for hybrid retriever",
            extra={"document_count": len(documents)},
        )

    @property
    def dense_retriever(self) -> BaseRetriever:
        """Lazily build and return the dense (Qdrant) retriever.

        Returns:
            A LangChain retriever backed by Qdrant vector search.

        Raises:
            Exception: If Qdrant collection cannot be accessed.
        """
        if self._dense_retriever is None:
            try:
                from langchain_qdrant import QdrantVectorStore

                qdrant_vs = QdrantVectorStore.from_existing_collection(
                    embedding=self.embedder,
                    collection_name=self.qdrant_store.collection_name,
                    host=self.qdrant_store.host,
                    port=self.qdrant_store.port,
                )
                self._dense_retriever = qdrant_vs.as_retriever(search_kwargs={"k": self.top_k})
                logger.info("Dense retriever initialized from Qdrant collection")
            except Exception as e:
                logger.error(
                    "Failed to initialize dense retriever",
                    extra={"error": str(e)},
                )
                raise

        return self._dense_retriever

    @property
    def sparse_retriever(self) -> BM25Retriever:
        """Lazily build and return the sparse (BM25) retriever.

        Returns:
            A BM25Retriever built from the set documents.

        Raises:
            ValueError: If no documents have been set.
            Exception: If BM25Retriever fails to initialize.
        """
        if self._sparse_retriever is None:
            if not self._documents:
                raise ValueError(
                    "No documents set for sparse retriever. "
                    "Call set_documents() before retrieval."
                )
            try:
                self._sparse_retriever = BM25Retriever.from_documents(self._documents, k=self.top_k)
                logger.info(
                    "BM25 sparse retriever initialized",
                    extra={"document_count": len(self._documents)},
                )
            except Exception as e:
                logger.error(
                    "Failed to initialize BM25 retriever",
                    extra={"error": str(e)},
                )
                raise

        return self._sparse_retriever

    def _weighted_ensemble(self, query: str) -> list[Document]:
        """Run both retrievers and merge results with weighted dedup.

        Each retriever returns ranked results. Documents are scored by
        weighted reciprocal rank and deduplicated by page_content.

        Args:
            query: Natural language query string.

        Returns:
            Merged and deduplicated list of Document objects.
        """
        dense_docs = self.dense_retriever.invoke(query)
        sparse_docs = self.sparse_retriever.invoke(query)

        # Score by weighted reciprocal rank fusion (RRF)
        doc_scores: dict[str, tuple[Document, float]] = {}
        rrf_k = 60  # standard RRF constant

        for rank, doc in enumerate(dense_docs):
            key = doc.page_content
            score = self.dense_weight / (rrf_k + rank + 1)
            if key in doc_scores:
                doc_scores[key] = (doc, doc_scores[key][1] + score)
            else:
                doc_scores[key] = (doc, score)

        for rank, doc in enumerate(sparse_docs):
            key = doc.page_content
            score = self.sparse_weight / (rrf_k + rank + 1)
            if key in doc_scores:
                doc_scores[key] = (doc, doc_scores[key][1] + score)
            else:
                doc_scores[key] = (doc, score)

        # Sort by combined score descending
        ranked = sorted(doc_scores.values(), key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in ranked[: self.top_k]]

    def retrieve(self, query: str) -> list[Document]:
        """Retrieve top-K documents for a query using hybrid search.

        Args:
            query: Natural language query string.

        Returns:
            List of retrieved Document objects, ordered by ensemble score.

        Raises:
            ValueError: If documents are not set for sparse retrieval.
            Exception: If retrieval fails.
        """
        logger.info(
            "Starting hybrid retrieval",
            extra={
                "query_preview": query[:80],
                "top_k": self.top_k,
            },
        )

        try:
            results = self._weighted_ensemble(query)
            logger.info(
                "Hybrid retrieval complete",
                extra={"result_count": len(results)},
            )
            return results
        except Exception as e:
            logger.error(
                "Hybrid retrieval failed",
                extra={"error": str(e), "query_preview": query[:80]},
            )
            raise

    def retrieve_with_scores(self, query: str) -> list[tuple[Document, float]]:
        """Retrieve documents paired with placeholder relevance scores.

        EnsembleRetriever does not expose per-document scores directly.
        Scores are set to 1.0 as a placeholder; use reranker scores
        for meaningful ranking downstream.

        Args:
            query: Natural language query string.

        Returns:
            List of (Document, score) tuples.
        """
        docs = self.retrieve(query)
        return [(doc, 1.0) for doc in docs]

    def get_relevant_documents(self, query: str) -> list[Document]:
        """LangChain-compatible retrieval interface.

        Args:
            query: Natural language query string.

        Returns:
            List of relevant Document objects.
        """
        return self.retrieve(query)

    async def aget_relevant_documents(self, query: str) -> list[Document]:
        """Async LangChain-compatible retrieval interface.

        Currently wraps the synchronous retrieve() method.
        Replace with true async implementation if latency becomes critical.

        Args:
            query: Natural language query string.

        Returns:
            List of relevant Document objects.
        """
        return self.retrieve(query)


def get_hybrid_retriever(
    qdrant_store: Optional[QdrantStore] = None,
    embedder: Optional[Embedder] = None,
    documents: Optional[list[Document]] = None,
) -> HybridRetriever:
    """Factory function to build a configured HybridRetriever.

    Loads configuration from settings. Initializes embedder and
    Qdrant store if not provided.

    Args:
        qdrant_store: Optional pre-initialized QdrantStore instance.
        embedder: Optional pre-initialized Embedder instance.
        documents: Optional documents to pre-load into BM25 retriever.

    Returns:
        Fully configured HybridRetriever instance.

    Raises:
        Exception: If embedder or Qdrant store initialization fails.
    """
    from src.embeddings.embedder import get_embedder
    from src.vectorstore.qdrant_store import get_qdrant_store

    settings = get_settings()

    if embedder is None:
        logger.info("No embedder provided, initializing default embedder")
        embedder = get_embedder()

    if qdrant_store is None:
        logger.info("No QdrantStore provided, initializing default store")
        qdrant_store = get_qdrant_store(embedder=embedder)

    retriever = HybridRetriever(
        qdrant_store=qdrant_store,
        embedder=embedder,
        dense_weight=settings.retrieval.dense_weight,
        sparse_weight=settings.retrieval.sparse_weight,
        top_k=settings.retrieval.top_k,
    )

    if documents:
        retriever.set_documents(documents)

    return retriever
