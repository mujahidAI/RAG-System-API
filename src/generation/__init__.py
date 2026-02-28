"""Generation module for LLM-based answer generation.

This module provides the generation chain that combines retrieval,
re-ranking, and LLM generation with proper prompting.
"""

from src.generation.generator import Generator, SimpleGenerator, get_generator
from src.generation.prompt_templates import (
    get_answer_prompt,
    get_citation_prompt,
    format_context,
    format_sources,
)

__all__ = [
    "Generator",
    "SimpleGenerator",
    "get_generator",
    "get_answer_prompt",
    "get_citation_prompt",
    "format_context",
    "format_sources",
]
