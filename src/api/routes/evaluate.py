"""Evaluation route for RAG pipeline assessment.

This module provides the POST /evaluate endpoint for running RAGAS evaluation.
"""

from pathlib import Path

from fastapi import APIRouter, HTTPException, status

from src.api.schemas import EvaluateRequest, EvaluateResponse
from src.evaluation.eval_dataset import EvalDatasetGenerator
from src.evaluation.evaluator import RAGEvaluator
from src.generation.generator import Generator
from src.utils.logger import get_logger
from src.utils.config import get_settings

logger = get_logger(__name__)

router = APIRouter(
    prefix="/evaluate",
    tags=["Evaluation"],
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
        api_key=settings.llm.groq_api_key,
        model=settings.llm.groq_model,
        temperature=settings.llm.temperature,
        max_tokens=settings.llm.max_tokens,
    )

    return Generator(
        llm=llm,
        retriever=retriever,
        reranker=reranker,
    )


@router.post("", response_model=EvaluateResponse, summary="Evaluate RAG pipeline")
async def evaluate_pipeline(request: EvaluateRequest) -> EvaluateResponse:
    """Evaluate the RAG pipeline using RAGAS metrics.

    Args:
        request: Evaluate request with questions

    Returns:
        EvaluateResponse with metrics
    """
    logger.info(
        "Evaluate request received",
        extra={
            "question_count": len(request.questions),
        },
    )

    try:
        if not request.questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="At least one question is required"
            )

        generator = get_generator()
        evaluator = RAGEvaluator(generator)

        output_path = request.output_path or get_settings().eval.output_path

        results = evaluator.evaluate_and_save(
            questions=request.questions,
            output_path=output_path,
        )

        return EvaluateResponse(
            success=True,
            metrics=results.get("metrics", {}),
            result_count=len(results.get("results", [])),
            report_path=output_path,
        )

    except Exception as e:
        logger.error("Evaluation failed", extra={"error": str(e)})

        return EvaluateResponse(
            success=False,
            error=str(e),
        )
