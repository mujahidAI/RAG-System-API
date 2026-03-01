"""Document loader for multiple file formats.

This module provides a unified interface for loading documents from various
file formats (TXT, PDF, DOCX, HTML) using LangChain loaders with proper
metadata extraction and error handling.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator, Optional

from langchain_community.document_loaders import (
    CSVLoader,
    Docx2txtLoader,
    PyMuPDFLoader,
    TextLoader,
    UnstructuredHTMLLoader,
)
from langchain_core.documents import Document

from src.utils.logger import get_logger
from src.utils.config import get_settings

logger = get_logger(__name__)


class DocumentLoader:
    """Multi-format document loader with automatic format detection.

    Supports TXT, PDF, DOCX, and HTML files with automatic format detection.
    Each document is enriched with metadata including source, file type,
    and ingestion timestamp.
    """

    SUPPORTED_EXTENSIONS = {
        ".txt": "text",
        ".pdf": "pdf",
        ".docx": "docx",
        ".html": "html",
        ".htm": "html",
    }

    LOADER_MAP = {
        ".txt": TextLoader,
        ".pdf": PyMuPDFLoader,
        ".docx": Docx2txtLoader,
        ".html": UnstructuredHTMLLoader,
        ".htm": UnstructuredHTMLLoader,
    }

    def __init__(self, encoding: str = "utf-8"):
        """Initialize the document loader.

        Args:
            encoding: Text encoding for text files (default: utf-8)
        """
        # The encoding parameter specifies how text files should be decoded
        # when reading from disk. Many text files use UTF-8, but some may use
        # different encodings (e.g., latin-1, utf-16). Setting the encoding ensures
        # that files are read correctly regardless of the system default.
        # If the wrong encoding is used, file reading can fail or produce garbled text.
        self.encoding = encoding
        self.settings = get_settings()
        logger.info("DocumentLoader initialized", extra={"encoding": encoding})

    def detect_file_type(self, file_path: Path) -> str:
        """Detect file type from extension.

        Args:
            file_path: Path to the file

        Returns:
            File type string (text, pdf, docx, html)

        Raises:
            ValueError: If file type is not supported
        """
        ext = file_path.suffix.lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {ext}")
        return self.SUPPORTED_EXTENSIONS[ext]

    def load_file(self, file_path: Path) -> list[Document]:
        """Load a single file and return documents with metadata.

        Args:
            file_path: Path to the file to load

        Returns:
            List of Document objects with enriched metadata

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file type is not supported
        """
        if not file_path.exists():
            logger.error("File not found", extra={"file_path": str(file_path)})
            raise FileNotFoundError(f"File not found: {file_path}")

        file_type = self.detect_file_type(file_path)
        loader_class = self.LOADER_MAP.get(file_path.suffix.lower())

        logger.info("Loading file", extra={"file_path": str(file_path), "file_type": file_type})

        try:
            if file_path.suffix.lower() == ".txt":
                loader = loader_class(str(file_path), encoding=self.encoding)
            else:
                loader = loader_class(str(file_path))

            documents = loader.load()

            enriched_documents = self._enrich_metadata(documents, file_path, file_type)

            logger.info(
                "File loaded successfully",
                extra={"file_path": str(file_path), "document_count": len(enriched_documents)},
            )

            return enriched_documents

        except Exception as e:
            logger.error(
                "Failed to load file", extra={"file_path": str(file_path), "error": str(e)}
            )
            raise

    def load_directory(self, directory_path: Path, recursive: bool = False) -> list[Document]:
        """Load all supported files from a directory.

        Args:
            directory_path: Path to the directory
            recursive: Whether to search recursively in subdirectories

        Returns:
            List of all loaded documents
        """
        if not directory_path.exists() or not directory_path.is_dir():
            raise ValueError(f"Invalid directory: {directory_path}")

        pattern = "**/*" if recursive else "*"
        files = list(directory_path.glob(pattern))

        supported_files = [
            f for f in files if f.is_file() and f.suffix.lower() in self.SUPPORTED_EXTENSIONS
        ]

        logger.info(
            "Loading directory",
            extra={
                "directory": str(directory_path),
                "file_count": len(supported_files),
                "recursive": recursive,
            },
        )

        all_documents = []
        for file_path in supported_files:
            try:
                documents = self.load_file(file_path)
                all_documents.extend(documents)
            except Exception as e:
                logger.warning(
                    "Skipping file due to error",
                    extra={"file_path": str(file_path), "error": str(e)},
                )

        logger.info("Directory loaded", extra={"total_documents": len(all_documents)})

        return all_documents

    def _enrich_metadata(
        self, documents: list[Document], file_path: Path, file_type: str
    ) -> list[Document]:
        """Enrich documents with metadata.

        Args:
            documents: List of loaded documents
            file_path: Path to the source file
            file_type: Type of the file

        Returns:
            Documents with enriched metadata
        """
        timestamp = datetime.utcnow().isoformat() + "Z"

        for idx, doc in enumerate(documents):
            if doc.metadata is None:
                doc.metadata = {}

            doc.metadata.update(
                {
                    "source_file": file_path.name,
                    "file_type": file_type,
                    "ingestion_timestamp": timestamp,
                    "chunk_index": idx,
                    "file_path": str(file_path.absolute()),
                }
            )

        return documents

    def load_file_iterator(self, file_path: Path) -> Iterator[Document]:
        """Load a file as an iterator (memory-efficient for large files).

        Args:
            file_path: Path to the file

        Yields:
            Document objects one at a time
        """
        file_type = self.detect_file_type(file_path)

        logger.info("Loading file as iterator", extra={"file_path": str(file_path)})

        for idx, doc in enumerate(self.load_file(file_path)):
            doc.metadata["chunk_index"] = idx
            yield doc
