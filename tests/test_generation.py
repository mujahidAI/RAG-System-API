"""Tests for generation module."""

import pytest
from unittest.mock import Mock, patch

from langchain_core.documents import Document

from src.generation.prompt_templates import (
    get_answer_prompt,
    format_context,
    format_sources,
)


class TestPromptTemplates:
    """Tests for prompt templates."""

    def test_get_answer_prompt(self):
        """Test answer prompt retrieval."""
        prompt = get_answer_prompt()
        assert prompt is not None
        assert "{context}" in prompt.template
        assert "{question}" in prompt.template

    def test_format_context(self):
        """Test context formatting."""
        docs = [
            Document(
                page_content="Test content 1",
                metadata={"source_file": "doc1.txt"}
            ),
            Document(
                page_content="Test content 2",
                metadata={"source_file": "doc2.txt"}
            ),
        ]
        context = format_context(docs, max_docs=2)
        assert "Test content 1" in context
        assert "doc1.txt" in context

    def test_format_sources(self):
        """Test source formatting."""
        docs = [
            Document(
                page_content="Test content",
                metadata={"source_file": "doc1.txt", "chunk_index": 0}
            ),
        ]
        sources = format_sources(docs)
        assert len(sources) == 1
        assert sources[0]["source"] == "doc1.txt"


class TestGenerator:
    """Tests for Generator class."""

    def test_generator_initialization(self):
        """Test generator initialization."""
        # Would need actual LLM and retriever
        pass
