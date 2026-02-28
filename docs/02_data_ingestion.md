# Data Ingestion

## What This Component Does

Loads documents from multiple file formats (TXT, PDF, DOCX, HTML) and enriches them with metadata including source filename, file type, and ingestion timestamp.

## Why It's Needed

Real-world documents come in various formats. A robust RAG system must handle all common document types while preserving source information for citation.

## Key Design Decisions

1. **Format Detection**: Automatic detection via file extension
2. **LangChain Loaders**: Uses PyMuPDFLoader, Docx2txtLoader, etc.
3. **Metadata Enrichment**: Adds source, timestamp, chunk index

## Code Walkthrough

See `src/ingestion/loader.py`:

```python
def load_file(self, file_path: Path) -> list[Document]:
    # Auto-detect format
    file_type = self.detect_file_type(file_path)
    # Load using appropriate loader
    loader = self.LOADER_MAP[file_type](str(file_path))
    # Enrich with metadata
    return self._enrich_metadata(documents, file_path, file_type)
```

## Connection to Other Components

- Input to: Chunking (`src/ingestion/chunker.py`)
- Output: Document objects with metadata
