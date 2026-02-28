"""Evaluation module for RAG pipeline evaluation.

This module provides RAGAS-based evaluation metrics for assessing
the quality of retrieval and generation.
"""

from src.evaluation.evaluator import RAGEvaluator
from src.evaluation.eval_dataset import EvalDatasetGenerator

__all__ = [
    "RAGEvaluator",
    "EvalDatasetGenerator",
]
