"""Tests for ingestion module."""

import pytest
from pathlib import Path

from langchain_core.documents import Document

from src.ingestion.loader import DocumentLoader
from src.ingestion.cleaner import TextCleaner
from src.ingestion.chunker import TextChunker


class TestDocumentLoader:
    """Tests for DocumentLoader."""

    def test_detect_file_type_txt(self):
        """Test file type detection for TXT."""
        loader = DocumentLoader()
        assert loader.detect_file_type(Path("test.txt")) == "text"

    def test_detect_file_type_pdf(self):
        """Test file type detection for PDF."""
        loader = DocumentLoader()
        assert loader.detect_file_type(Path("test.pdf")) == "pdf"

    def test_detect_file_type_unsupported(self):
        """Test file type detection for unsupported type."""
        loader = DocumentLoader()
        with pytest.raises(ValueError):
            loader.detect_file_type(Path("test.xyz"))


class TestTextCleaner:
    """Tests for TextCleaner."""

    def test_clean_text(self):
        """Test basic text cleaning."""
        cleaner = TextCleaner()
        text = "  Hello   World  "
        result = cleaner.clean_text(text)
        assert result == "Hello World"

    def test_clean_text_with_urls(self):
        """Test URL removal."""
        cleaner = TextCleaner(remove_urls=True)
        text = "Visit http://example.com for more"
        result = cleaner.clean_text(text)
        assert "http://example.com" not in result


class TestTextChunker:
    """Tests for TextChunker."""

    def test_chunk_document(self):
        """Test document chunking."""
        chunker = TextChunker(chunk_size=100, chunk_overlap=20)
        doc = Document(page_content="This is a long text " * 50, metadata={"source": "test.txt"})
        chunks = chunker.chunk_document(doc)
        assert len(chunks) > 1

    def test_metadata_preservation(self):
        """Test that metadata is preserved."""
        chunker = TextChunker()
        doc = Document(
            page_content="Test content", metadata={"source": "test.txt", "custom": "value"}
        )
        chunks = chunker.chunk_document(doc)
        assert chunks[0].metadata["source"] == "test.txt"
        assert chunks[0].metadata["custom"] == "value"
