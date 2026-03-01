# src/ingestion/cleaner.py
"""
Text cleaning and normalization utilities.

This file implements utilities for cleaning and normalizing text, primarily for use
in data ingestion pipelines within a Retrieval-Augmented Generation (RAG) system.
It helps to remove noise, standardize line breaks, handle special characters, and
prepare text for reliable downstream chunking and embedding.
"""

# --- Imports & Logger Setup ---

import re
from typing import Optional
from langchain_core.documents import Document
from src.utils.logger import get_logger

logger = get_logger(__name__)

# --- TextCleaner Class Definition ---

class TextCleaner:
    """
    Text cleaning and normalization for documents.

    This class provides comprehensive, configurable text cleaning for documents loaded
    from various file formats (PDF, TXT, DOCX, HTML). Its cleaning steps include:
      - Whitespace normalization
      - Special character and artifact removal
      - Line break & page break standardization
      - Unicode normalization
      - Pattern-based cleanup (e.g., URLs, emails)
    """

    # --- Initialization ---

    def __init__(
        self,
        remove_urls: bool = True,
        remove_emails: bool = True,
        remove_extra_whitespace: bool = True,
        lowercase: bool = False,
    ):
        """
        Create a new TextCleaner with configurable cleaning options.

        Args:
            remove_urls: Remove web URLs from text (default: True)
            remove_emails: Remove email addresses (default: True)
            remove_extra_whitespace: Collapse excessive whitespace (default: True)
            lowercase: Convert to all lowercase (default: False)
        """
        self.remove_urls = remove_urls
        self.remove_emails = remove_emails
        self.remove_extra_whitespace = remove_extra_whitespace
        self.lowercase = lowercase

        # Compile cleaning regex patterns
        self.url_pattern = re.compile(
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        )
        self.email_pattern = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
        self.whitespace_pattern = re.compile(r"\s+")
        self.page_break_pattern = re.compile(r"(?:\f|\n\n+)")

        logger.info(
            "TextCleaner initialized",
            extra={
                "remove_urls": remove_urls,
                "remove_emails": remove_emails,
                "remove_extra_whitespace": remove_extra_whitespace,
                "lowercase": lowercase,
            },
        )

    # --- Core Text Cleaning Functionality ---

    def clean_text(self, text: str) -> str:
        """
        Clean a string of text using configured cleaning steps.

        Args:
            text: The input string to clean.

        Returns:
            Cleaned string.
        """
        if not text:
            return text

        cleaned = text

        # The following steps apply the configured text cleaning operations in sequence:

        # Remove URLs by substituting any substring that matches the URL pattern with a space.
        if self.remove_urls:
            cleaned = self.url_pattern.sub(" ", cleaned)

        # Remove email addresses by substituting them with a space.
        if self.remove_emails:
            cleaned = self.email_pattern.sub(" ", cleaned)

        # Replace page break characters (\f) with a newline to normalize formatting across document types.
        cleaned = cleaned.replace("\f", "\n")

        # Collapse sets of whitespace (spaces, tabs, newlines) into a single space and strip leading/trailing spaces.
        if self.remove_extra_whitespace:
            cleaned = self.whitespace_pattern.sub(" ", cleaned)
            cleaned = cleaned.strip()

        # Optionally convert the entire cleaned text to lowercase.
        if self.lowercase:
            cleaned = cleaned.lower()

        logger.debug(
            "Text cleaned", extra={"original_length": len(text), "cleaned_length": len(cleaned)}
        )

        return cleaned

    # --- Cleaning Whole Document Objects ---

    def clean_document(self, document: Document) -> Document:
        """
        Clean a LangChain Document object.

        Args:
            document: The Document to clean.

        Returns:
            New Document with cleaned content, original metadata.
        """
        cleaned_content = self.clean_text(document.page_content)
        return Document(page_content=cleaned_content, metadata=document.metadata.copy())

    def clean_documents(self, documents: list[Document]) -> list[Document]:
        """
        Clean a list of Document objects.

        Args:
            documents: List[Document]

        Returns:
            List[Document] with cleaned text in each document.
        """
        logger.info("Cleaning documents", extra={"count": len(documents)})
        cleaned_docs = []
        for doc in documents:
            cleaned_docs.append(self.clean_document(doc))
        return cleaned_docs

    # --- Utility: Page Break and Paragraph Normalization ---

    def clean_page_breaks(self, text: str) -> str:
        """
        Replace excessive page breaks with normalized paragraph breaks and trim lines.

        Args:
            text: Input string possibly containing excessive breaks.

        Returns:
            Nicely formatted string with paragraph breaks.
        """
        text = self.page_break_pattern.sub("\n\n", text)
        lines = text.split("\n")
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line:
                cleaned_lines.append(line)
        return "\n\n".join(cleaned_lines)

    # --- Utility: Special Character Removal ---

    def remove_special_characters(self, text: str, keep_chars: Optional[str] = None) -> str:
        """
        Remove all special characters from text except those explicitly allowed.

        Args:
            text: Input text string.
            keep_chars: String of additional characters to keep (e.g. '.,!?')

        Returns:
            Text string with only letters, numbers, spaces and allowed characters.
        """
        if keep_chars:
            pattern = f"[^a-zA-Z0-9\s{re.escape(keep_chars)}]"
        else:
            pattern = r"[^a-zA-Z0-9\s\.,!?;:\'\"-]"
        return re.sub(pattern, "", text)

    # --- Utility: Unicode Normalization ---

    def normalize_unicode(self, text: str) -> str:
        """
        Apply NFC unicode normalization to text.

        Args:
            text: Input string.

        Returns:
            Unicode-normalized string.
        """
        import unicodedata
        return unicodedata.normalize("NFC", text)
