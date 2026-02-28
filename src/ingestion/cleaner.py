"""Text cleaning and normalization utilities.

This module provides text cleaning functions to normalize and clean
extracted document text before chunking. Removes artifacts from various
file formats and standardizes text for better retrieval.
"""

import re
from typing import Optional

from langchain_core.documents import Document

from src.utils.logger import get_logger

logger = get_logger(__name__)


class TextCleaner:
    """Text cleaning and normalization for documents.
    
    Provides comprehensive text cleaning including:
    - Whitespace normalization
    - Special character handling
    - Line break standardization
    - Unicode normalization
    - Pattern-based cleanup
    """
    
    def __init__(
        self,
        remove_urls: bool = True,
        remove_emails: bool = True,
        remove_extra_whitespace: bool = True,
        lowercase: bool = False,
    ):
        """Initialize the text cleaner.
        
        Args:
            remove_urls: Whether to remove URLs
            remove_emails: Whether to remove email addresses
            remove_extra_whitespace: Whether to normalize whitespace
            lowercase: Whether to convert text to lowercase
        """
        self.remove_urls = remove_urls
        self.remove_emails = remove_emails
        self.remove_extra_whitespace = remove_extra_whitespace
        self.lowercase = lowercase
        
        self.url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        )
        self.whitespace_pattern = re.compile(r'\s+')
        self.page_break_pattern = re.compile(r'(?:\f|\n\n+)')
        
        logger.info("TextCleaner initialized", extra={
            "remove_urls": remove_urls,
            "remove_emails": remove_emails,
            "remove_extra_whitespace": remove_extra_whitespace,
            "lowercase": lowercase,
        })
    
    def clean_text(self, text: str) -> str:
        """Clean a text string.
        
        Args:
            text: Input text to clean
            
        Returns:
            Cleaned text string
        """
        if not text:
            return text
        
        cleaned = text
        
        if self.remove_urls:
            cleaned = self.url_pattern.sub(' ', cleaned)
        
        if self.remove_emails:
            cleaned = self.email_pattern.sub(' ', cleaned)
        
        cleaned = cleaned.replace('\f', '\n')
        
        if self.remove_extra_whitespace:
            cleaned = self.whitespace_pattern.sub(' ', cleaned)
            cleaned = cleaned.strip()
        
        if self.lowercase:
            cleaned = cleaned.lower()
        
        logger.debug("Text cleaned", extra={"original_length": len(text), "cleaned_length": len(cleaned)})
        
        return cleaned
    
    def clean_document(self, document: Document) -> Document:
        """Clean a Document object.
        
        Args:
            document: Document to clean
            
        Returns:
            Cleaned Document
        """
        cleaned_content = self.clean_text(document.page_content)
        
        return Document(
            page_content=cleaned_content,
            metadata=document.metadata.copy()
        )
    
    def clean_documents(self, documents: list[Document]) -> list[Document]:
        """Clean a list of documents.
        
        Args:
            documents: List of documents to clean
            
        Returns:
            List of cleaned documents
        """
        logger.info("Cleaning documents", extra={"count": len(documents)})
        
        cleaned_docs = []
        for doc in documents:
            cleaned_docs.append(self.clean_document(doc))
        
        return cleaned_docs
    
    def clean_page_breaks(self, text: str) -> str:
        """Remove excessive page breaks and format nicely.
        
        Args:
            text: Input text
            
        Returns:
            Cleaned text with normalized paragraphs
        """
        text = self.page_break_pattern.sub('\n\n', text)
        
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                cleaned_lines.append(line)
        
        return '\n\n'.join(cleaned_lines)
    
    def remove_special_characters(
        self, 
        text: str, 
        keep_chars: Optional[str] = None
    ) -> str:
        """Remove special characters while keeping specified characters.
        
        Args:
            text: Input text
            keep_chars: Characters to keep (e.g., '.,!?')
            
        Returns:
            Text with special characters removed
        """
        if keep_chars:
            pattern = f'[^a-zA-Z0-9\s{re.escape(keep_chars)}]'
        else:
            pattern = r'[^a-zA-Z0-9\s\.,!?;:\'\"-]'
        
        return re.sub(pattern, '', text)
    
    def normalize_unicode(self, text: str) -> str:
        """Normalize Unicode text (NFC normalization).
        
        Args:
            text: Input text
            
        Returns:
            Normalized text
        """
        import unicodedata
        return unicodedata.normalize('NFC', text)
