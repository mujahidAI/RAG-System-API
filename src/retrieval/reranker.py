"""Cross-encoder re-ranking for improved retrieval results.

This module provides cross-encoder based re-ranking to improve
the quality of retrieved documents before generation.
"""

from typing import Any, Optional

from langchain_core.documents import Document
from langchain_community.cross_encoders import HuggingFaceCrossEncoder

from src.utils.logger import get_logger
from src.utils.config import get_settings

logger = get_logger(__name__)


class Reranker:
    """Cross-encoder re-ranker for retrieval results.

    Re-ranks initial retrieval results using a cross-encoder model
    to improve relevance ranking before generation.
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        top_k: int = 3,
    ):
        """Initialize the reranker.

        Args:
            model_name: Cross-encoder model name
            top_k: Number of top results to return after re-ranking
        """
        settings = get_settings()

        self.model_name = model_name or settings.reranker.model_name
        self.top_k = top_k or settings.reranker.top_k

        logger.info(
            "Initializing cross-encoder reranker",
            extra={
                "model_name": self.model_name,
                "top_k": self.top_k,
            },
        )

        self._cross_encoder = HuggingFaceCrossEncoder(
            model_name=self.model_name,
        )

        logger.info("Cross-encoder reranker initialized")

    def rerank(
        self,
        query: str,
        documents: list[Document],
        top_k: Optional[int] = None,
    ) -> list[tuple[Document, float]]:
        """Re-rank documents for a query.

        Args:
            query: Query string
            documents: List of documents to re-rank
            top_k: Number of top results to return

        Returns:
            List of (document, score) tuples sorted by relevance
        """
        k = top_k or self.top_k

        if not documents:
            logger.warning("No documents to rerank")
            return []

        logger.info(
            "Re-ranking documents",
            extra={
                "query": query[:50] + "...",
                "document_count": len(documents),
                "top_k": k,
            },
        )

        doc_texts = [doc.page_content for doc in documents]
        query_doc_pairs = [[query, doc] for doc in doc_texts]

        scores = self._cross_encoder.score(query_doc_pairs)

        doc_scores = list(zip(documents, scores))
        doc_scores.sort(key=lambda x: x[1], reverse=True)

        reranked = doc_scores[:k]

        logger.info(
            "Re-ranking completed",
            extra={
                "result_count": len(reranked),
                "top_score": reranked[0][1] if reranked else 0,
            },
        )

        for doc, score in reranked:
            logger.debug(
                "Reranked result",
                extra={
                    "source": doc.metadata.get("source_file", "unknown"),
                    "score": score,
                },
            )

        return reranked

    def rerank_with_metadata(
        self,
        query: str,
        documents: list[Document],
        top_k: Optional[int] = None,
    ) -> list[dict[str, Any]]:
        """Re-rank documents and return with metadata.

        Args:
            query: Query string
            documents: List of documents to re-rank
            top_k: Number of top results to return

        Returns:
            List of dicts with document content, metadata, and score
        """
        reranked = self.rerank(query, documents, top_k)

        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score),
            }
            for doc, score in reranked
        ]

    def get_scores(
        self,
        query: str,
        documents: list[Document],
    ) -> list[float]:
        """Get relevance scores for query-document pairs.

        Args:
            query: Query string
            documents: List of documents

        Returns:
            List of relevance scores
        """
        doc_texts = [doc.page_content for doc in documents]
        query_doc_pairs = [[query, doc] for doc in doc_texts]

        return self._cross_encoder.score(query_doc_pairs)


def get_reranker(top_k: Optional[int] = None) -> Reranker:
    """Get a configured reranker instance.

    Args:
        top_k: Number of results to return

    Returns:
        Configured Reranker
    """
    return Reranker(top_k=top_k)
