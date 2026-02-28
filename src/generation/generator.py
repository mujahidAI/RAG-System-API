"""LLM generator for the RAG pipeline.

This module provides the generation chain that combines:
- Query transformation
- Retrieval
- Re-ranking
- Prompt formatting
- LLM generation
"""

from typing import Any, Optional

from langchain_core.documents import Document
from langchain_core.runnables import Runnable, RunnableSequence

from src.embeddings.embedder import Embedder
from src.generation.prompt_templates import (
    get_answer_prompt,
    format_context,
    format_sources,
)
from src.retrieval.query_transformer import QueryTransformer
from src.retrieval.reranker import Reranker
from src.retrieval.retriever import HybridRetriever
from src.utils.logger import get_logger
from src.utils.config import get_settings

logger = get_logger(__name__)


class Generator:
    """RAG generator combining retrieval and generation.

    Creates an LCEL chain that:
    1. Transforms the query (HyDE, multi-query)
    2. Retrieves relevant documents
    3. Re-ranks documents
    4. Generates answer with context
    """

    def __init__(
        self,
        llm: Any,
        retriever: HybridRetriever,
        reranker: Optional[Reranker] = None,
        query_transformer: Optional[QueryTransformer] = None,
        max_context_docs: int = 5,
    ):
        """Initialize the generator.

        Args:
            llm: Language model instance
            retriever: Hybrid retriever
            reranker: Optional re-ranker
            query_transformer: Optional query transformer
            max_context_docs: Maximum documents to include in context
        """
        settings = get_settings()

        self.llm = llm
        self.retriever = retriever
        self.reranker = reranker
        self.query_transformer = query_transformer
        self.max_context_docs = max_context_docs

        self.prompt = get_answer_prompt()

        self._chain = None

        logger.info(
            "Generator initialized",
            extra={
                "has_reranker": reranker is not None,
                "has_query_transformer": query_transformer is not None,
                "max_context_docs": max_context_docs,
            },
        )

    @property
    def chain(self) -> Runnable:
        """Get the LCEL chain."""
        if self._chain is None:
            self._chain = self.prompt | self.llm
        return self._chain

    def generate(self, query: str) -> dict[str, Any]:
        """Generate answer for a query.

        Args:
            query: User query

        Returns:
            Dictionary with answer, sources, and metadata
        """
        logger.info("Generating answer", extra={"query": query[:50] + "..."})

        transformed_queries = [query]
        if self.query_transformer:
            transformed_queries = self.query_transformer.transform(query)
            logger.info("Queries transformed", extra={"query_count": len(transformed_queries)})

        all_docs = []
        for q in transformed_queries:
            docs = self.retriever.retrieve(q)
            all_docs.extend(docs)

        unique_docs = self._deduplicate_documents(all_docs)

        logger.info("Documents retrieved", extra={"unique_doc_count": len(unique_docs)})

        if self.reranker:
            reranked = self.reranker.rerank(query, unique_docs)
            final_docs = [doc for doc, score in reranked]
            scores = {doc.page_content: score for doc, score in reranked}
        else:
            final_docs = unique_docs[: self.max_context_docs]
            scores = {}

        logger.info("Context prepared", extra={"final_doc_count": len(final_docs)})

        context = format_context(final_docs, self.max_context_docs)

        result = self.chain.invoke(
            {
                "context": context,
                "question": query,
            }
        )
        answer = result.content if hasattr(result, "content") else str(result)

        sources = format_sources(final_docs)

        result = {
            "answer": answer,
            "sources": sources,
            "query": query,
            "context_doc_count": len(final_docs),
            "retrieval_scores": scores,
        }

        logger.info("Answer generated successfully")

        return result

    def _deduplicate_documents(self, documents: list[Document]) -> list[Document]:
        """Remove duplicate documents.

        Args:
            documents: List of documents

        Returns:
            Deduplicated list
        """
        seen = set()
        unique = []

        for doc in documents:
            key = doc.page_content[:100]
            if key not in seen:
                seen.add(key)
                unique.append(doc)

        return unique

    async def agenerate(self, query: str) -> dict[str, Any]:
        """Async version of generate."""
        return self.generate(query)

    def invoke(self, query: str) -> dict[str, Any]:
        """Alias for generate method."""
        return self.generate(query)


class SimpleGenerator:
    """Simplified generator without query transformation or re-ranking."""

    def __init__(self, llm: Any, retriever: HybridRetriever):
        self.generator = Generator(
            llm=llm,
            retriever=retriever,
            reranker=None,
            query_transformer=None,
        )

    def generate(self, query: str) -> dict[str, Any]:
        return self.generator.generate(query)

    def invoke(self, query: str) -> dict[str, Any]:
        return self.generate(query)


def get_generator(
    llm: Any,
    retriever: HybridRetriever,
    reranker: Optional[Reranker] = None,
    query_transformer: Optional[QueryTransformer] = None,
) -> Generator:
    """Get a configured generator.

    Args:
        llm: Language model
        retriever: Hybrid retriever
        reranker: Optional re-ranker
        query_transformer: Optional query transformer

    Returns:
        Configured Generator
    """
    return Generator(
        llm=llm,
        retriever=retriever,
        reranker=reranker,
        query_transformer=query_transformer,
    )
