"""
Text chunking with semantic and recursive strategies.

This module provides classes (`TextChunker` and `SemanticChunker`) for splitting text documents into chunks suitable for embedding and retrieval, while preserving all relevant metadata. It leverages LangChain's `RecursiveCharacterTextSplitter` and includes additional semantic splitting utilities.
"""

# --- Imports and Logger Setup ---

from typing import Any

from langchain_core.documents import Document           # Document type from LangChain
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.utils.logger import get_logger                 # Custom logger
from src.utils.config import get_settings               # App settings for configuration

logger = get_logger(__name__)


# --- TextChunker Class ---

class TextChunker:
    """
    Text chunker using RecursiveCharacterTextSplitter.

    Splits documents into chunks of specified size with overlap to maintain context.
    Passes through all metadata from the source document to each resulting chunk,
    and adds per-chunk metadata (such as `chunk_index` and `total_chunks`).
    """

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        separators: list[str] | None = None,
        length_function: Any = None,
    ):
        """
        Configure chunking strategy.

        - chunk_size: Maximum size of each chunk (in characters).
        - chunk_overlap: Overlap between consecutive chunks (characters).
        - separators: Priority-ordered list of strings to use as natural break points.
        - length_function: Function to measure string length (defaults to `len`).
        Loads defaults from app settings if arguments are omitted.
        """
        settings = get_settings()
        self.chunk_size = chunk_size or settings.chunking.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunking.chunk_overlap

        # Choose fallback separators if none given
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
        # Configure the recursive text splitter from LangChain
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
        """
        Split a single document into chunks.

        - For the given LangChain Document, splits its content into multiple sub-documents.
        - Preserves and extends original metadata (adds `chunk_index`, `total_chunks`, etc).

        Returns:
            List of Document objects, where each is a chunk with appropriate metadata.
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
        """
        Split a list of documents into chunks.

        Calls `chunk_document` on each Document and combines all results into a single list.

        Returns:
            List of Document chunks from all input documents.
        """
        logger.info("Chunking documents", extra={"document_count": len(documents)})

        all_chunks = []
        for doc in documents:
            chunks = self.chunk_document(doc)
            all_chunks.extend(chunks)

        logger.info("All documents chunked", extra={"total_chunks": len(all_chunks)})
        return all_chunks

    def chunk_with_metadata(self, text: str, metadata: dict[str, Any]) -> list[Document]:
        """
        Split a raw text string into chunks and associate provided metadata with each.

        Args:
            text: Input content
            metadata: Metadata dictionary attached to each resulting chunk

        Returns:
            List of chunked Document objects.
        """
        document = Document(page_content=text, metadata=metadata)
        return self.chunk_document(document)

    def get_chunk_count_estimate(self, text: str) -> int:
        """
        Estimate the number of chunks generated by current settings for a given text.

        Returns:
            Approximate chunk count as an integer.
        """
        chunks = self.splitter.split_text(text)
        return len(chunks)


# --- SemanticChunker Class ---

class SemanticChunker(TextChunker):
    """
    Enhanced chunker with semantic awareness.

    Inherits from TextChunker but provides sentence-level splitting, allowing
    for more contextually meaningful chunk boundaries.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize SemanticChunker and set up sentence separators
        (e.g., ". ", "! ", "? ", line breaks) for use in sentence chunking.
        """
        super().__init__(*args, **kwargs)
        self.sentence_separators = [". ", "! ", "? ", "\n"]

    def chunk_by_sentences(self, text: str) -> list[str]:
        """
        Split text into chunks based on sentence boundaries.

        Walks through each character, accumulating text until a sentence separator
        is encountered and the chunk length exceeds half the configured chunk_size.
        Produces a list of sentence-based text chunks.

        Returns:
            List[str]: List of chunked strings split at likely sentence boundaries.
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
