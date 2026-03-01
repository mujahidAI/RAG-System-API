# Data Ingestion

## What It Does

Loads documents from disk (TXT, PDF, DOCX, HTML), cleans extracted text, and splits into chunks ready for embedding. Each chunk preserves metadata linking back to the source file.

## Why It Exists

Without ingestion, the system has no documents to search. Different formats require different loaders, and raw extracted text contains noise (URLs, extra whitespace) that degrades retrieval quality.

## How It Fits In

```
Files → [DocumentLoader] → [TextCleaner] → [TextChunker] → Chunks with metadata
                                                                  ↓
                                                           [QdrantStore]
```

## Key Design Decisions

- **Format detection by extension**: Simple and reliable for supported types
- **Metadata preservation**: Every chunk carries source filename, chunk index, timestamp
- **Configurable cleaning**: Default removes URLs/emails; can be customized

## Configuration

| Variable | Default | Effect |
|----------|---------|--------|
| `CHUNK_SIZE` | 512 | Characters per chunk |
| `CHUNK_OVERLAP` | 50 | Overlap between chunks |

## Code Walkthrough

`src/ingestion/loader.py` - `DocumentLoader.load_file()`:
```python
def load_file(self, file_path: Path) -> list[Document]:
    file_type = self.detect_file_type(file_path)  # .txt, .pdf, etc.
    loader_class = self.LOADER_MAP[file_type]
    loader = loader_class(str(file_path))
    documents = loader.load()
    return self._enrich_metadata(documents, file_path, file_type)
```

`src/ingestion/chunker.py` - `TextChunker.chunk_document()`:
```python
def chunk_document(self, document: Document) -> list[Document]:
    chunks = self.splitter.split_text(document.page_content)
    return [
        Document(page_content=chunk, metadata={**document.metadata, "chunk_index": i})
        for i, chunk in enumerate(chunks)
    ]
```

## Common Errors & Fixes

- **Error**: `Unsupported file type: .xyz`
  - Fix: Add extension to `SUPPORTED_EXTENSIONS` in `loader.py`

- **Error**: Empty chunks after processing
  - Fix: Check source file is not empty; verify encoding

- **Error**: Unicode decode errors
  - Fix: Specify encoding in `TextLoader` (default utf-8)

## Related Files

- `src/ingestion/loader.py` - Multi-format loading
- `src/ingestion/cleaner.py` - Text normalization
- `src/ingestion/chunker.py` - Recursive splitting
- `src/api/routes/ingest.py` - API endpoint
