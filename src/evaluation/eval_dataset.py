"""Evaluation dataset generator for RAGAS metrics.

This module generates Q&A datasets from documents for evaluation.
"""

import json
from pathlib import Path
from typing import Any

from langchain_core.documents import Document

from src.utils.logger import get_logger
from src.utils.config import get_settings

logger = get_logger(__name__)

SAMPLE_QUESTIONS = {
    "science": [
        "What is wave-particle duality?",
        "Explain quantum superposition",
    ],
    "history": [
        "What was the Renaissance?",
        "Who were key Renaissance figures?",
    ],
    "geography": [
        "What are biogeographic regions?",
        "Describe the Palearctic region",
    ],
    "technology": [
        "What is artificial intelligence?",
        "Explain machine learning",
    ],
    "space": [
        "What are exoplanets?",
        "How do we detect exoplanets?",
    ],
}


class EvalDatasetGenerator:
    """Generator for evaluation Q&A datasets."""

    def __init__(self, dataset_size: int = 20):
        self.dataset_size = dataset_size

    def generate(self, documents: list[Document]) -> list[dict[str, Any]]:
        """Generate Q&A pairs from documents."""
        qa_pairs = []
        for doc in documents:
            source = doc.metadata.get("source_file", "").lower()
            for topic, questions in SAMPLE_QUESTIONS.items():
                if topic in source:
                    for q in questions:
                        qa_pairs.append(
                            {
                                "question": q,
                                "answer": doc.page_content[:150] + "...",
                            }
                        )
                    break
            if len(qa_pairs) >= self.dataset_size:
                break
        return qa_pairs[: self.dataset_size]
