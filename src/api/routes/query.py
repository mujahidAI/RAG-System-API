"""Query route for RAG question answering.

This module provides the POST /query endpoint for asking questions.
"""

import time
from typing import Any

from fastapi import APIRouter, HTTPException, status

from src.api.schemas import QueryRequest, QueryResponse, SourceDocument
from src.generation.generator import Generator
from src.retrieval.retriever import HybridRetriever
from src.retrieval.reranker import Reranker
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/query",
    tags=["Query"],
)


def get_generator() -> Generator:
    """Get the generator instance."""
    from src.embeddings.embedder import get_embedder
    from src.vectorstore.qdrant_store import get_qdrant_store
    from src.retrieval.retriever import get_hybrid_retriever
    from src.retrieval.reranker import get_reranker

    embedder = get_embedder()
    store = get_qdrant_store(embedder=embedder)
    retriever = get_hybrid_retriever(qdrant_store=store, embedder=embedder)
    reranker = get_reranker()

    from langchain_groq import ChatGroq
    from src.utils.config import get_settings

    settings = get_settings()

    llm = ChatGroq(
        model=settings.llm.groq_model,
        temperature=settings.llm.temperature,
        max_tokens=settings.llm.max_tokens,
    )

    return Generator(
        llm=llm,
        retriever=retriever,
        reranker=reranker,
    )


@router.post("", response_model=QueryResponse, summary="Query the RAG system")
async def query_documents(request: QueryRequest) -> QueryResponse:
    """Ask a question and get an answer from the RAG system.

    Args:
        request: Query request with question

    Returns:
        QueryResponse with answer and sources
    """
    start_time = time.time()

    logger.info(
        "Query request received",
        extra={
            "question": request.question[:50] + "...",
        },
    )

    try:
        generator = get_generator()

        result = generator.generate(request.question)

        sources = []
        if request.include_sources:
            for s in result.get("sources", []):
                sources.append(
                    SourceDocument(
                        content=s.get("content", ""),
                        source=s.get("source", "unknown"),
                        chunk_index=s.get("chunk_index", 0),
                    )
                )

        latency_ms = (time.time() - start_time) * 1000

        return QueryResponse(
            success=True,
            answer=result.get("answer", ""),
            sources=sources,
            context_doc_count=result.get("context_doc_count", 0),
            latency_ms=latency_ms,
        )

    except Exception as e:
        logger.error("Query failed", extra={"error": str(e)})

        return QueryResponse(
            success=False,
            answer="",
            error=str(e),
            latency_ms=(time.time() - start_time) * 1000,
        )
