"""Text chunking with semantic and recursive strategies.

This module provides text chunking using LangChain's RecursiveCharacterTextSplitter
with metadata preservation. Chunks are sized for optimal embedding and retrieval.
"""

from typing import Any

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.utils.logger import get_logger
from src.utils.config import get_settings

logger = get_logger(__name__)


class TextChunker:
    """Text chunker using RecursiveCharacterTextSplitter.

    Splits documents into chunks of specified size with overlap for
    maintaining context. Preserves and passes through all metadata
    from source documents to each chunk.
    """

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        separators: list[str] | None = None,
        length_function: Any = None,
    ):
        """Initialize the text chunker.

        Args:
            chunk_size: Size of each chunk in characters
            chunk_overlap: Overlap between chunks in characters
            separators: List of separators to use (in priority order)
            length_function: Function to calculate text length
        """
        settings = get_settings()

        self.chunk_size = chunk_size or settings.chunking.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunking.chunk_overlap

        if separators is None:
            separators = [
                "\n\n\n",
                "\n\n",
                "\n",
                " ",
                ".",
                ",",
                "?",
                "!",
                ";",
                ":",
                "",
            ]

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=separators,
            length_function=length_function or len,
            keep_separator=False,
        )

        logger.info(
            "TextChunker initialized",
            extra={
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap,
                "separators_count": len(separators),
            },
        )

    def chunk_document(self, document: Document) -> list[Document]:
        """Split a single document into chunks.

        Args:
            document: Document to chunk

        Returns:
            List of chunk documents with metadata
        """
        source_file = document.metadata.get("source_file", "unknown")

        logger.debug(
            "Chunking document",
            extra={"source_file": source_file, "content_length": len(document.page_content)},
        )

        chunks = self.splitter.split_text(document.page_content)

        chunked_documents = []
        for idx, chunk in enumerate(chunks):
            chunk_metadata = document.metadata.copy()
            chunk_metadata.update(
                {
                    "chunk_index": idx,
                    "total_chunks": len(chunks),
                    "chunk_size": len(chunk),
                }
            )

            chunked_documents.append(Document(page_content=chunk, metadata=chunk_metadata))

        logger.info(
            "Document chunked", extra={"source_file": source_file, "total_chunks": len(chunks)}
        )

        return chunked_documents

    def chunk_documents(self, documents: list[Document]) -> list[Document]:
        """Split multiple documents into chunks.

        Args:
            documents: List of documents to chunk

        Returns:
            List of all chunk documents
        """
        logger.info("Chunking documents", extra={"document_count": len(documents)})

        all_chunks = []
        for doc in documents:
            chunks = self.chunk_document(doc)
            all_chunks.extend(chunks)

        logger.info("All documents chunked", extra={"total_chunks": len(all_chunks)})

        return all_chunks

    def chunk_with_metadata(self, text: str, metadata: dict[str, Any]) -> list[Document]:
        """Chunk text with provided metadata.

        Args:
            text: Text to chunk
            metadata: Metadata to attach to each chunk

        Returns:
            List of chunk documents
        """
        document = Document(page_content=text, metadata=metadata)
        return self.chunk_document(document)

    def get_chunk_count_estimate(self, text: str) -> int:
        """Estimate the number of chunks for given text.

        Args:
            text: Input text

        Returns:
            Estimated number of chunks
        """
        chunks = self.splitter.split_text(text)
        return len(chunks)


class SemanticChunker(TextChunker):
    """Enhanced chunker with semantic awareness.

    Extends TextChunker with additional semantic chunking capabilities
    for better context preservation.
    """

    def __init__(self, *args, **kwargs):
        """Initialize semantic chunker with enhanced settings."""
        super().__init__(*args, **kwargs)

        self.sentence_separators = [". ", "! ", "? ", "\n"]

    def chunk_by_sentences(self, text: str) -> list[str]:
        """Split text into sentence-aware chunks.

        Args:
            text: Input text

        Returns:
            List of text chunks by sentences
        """
        chunks = []
        current_chunk = ""

        for char in text:
            current_chunk += char

            for sep in self.sentence_separators:
                if current_chunk.endswith(sep):
                    if len(current_chunk) >= self.chunk_size // 2:
                        chunks.append(current_chunk.strip())
                        current_chunk = ""
                    break

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks
