# Chunking Strategy

## What It Does

Splits text into overlapping chunks of ~512 characters using recursive character splitting. Preserves metadata through chunking so sources can be cited.

## Why It Needed

Embedding models have token limits. Without chunking, large documents exceed limits and fail. Poor chunking causes either loss of context (too small) or noisy retrieval (too large). Overlap ensures context spans chunk boundaries.

## How It Fits In

```
Cleaned Document → [TextChunker] → List of Chunks
                              ↓
                        Each chunk keeps:
                        - source_file
                        - chunk_index
                        - ingestion_timestamp
```

## Key Design Decisions

- **512 chars, 50 overlap**: Balances context preservation with precision
- **Recursive separators**: Tries `\n\n`, then `\n`, then space—breaks on natural boundaries
- **Metadata passthrough**: All original metadata flows through to each chunk

## Configuration

| Variable | Default | Effect |
|----------|---------|--------|
| `CHUNK_SIZE` | 512 | Max characters per chunk |
| `CHUNK_OVERLAP` | 50 | Characters shared between chunks |

## Code Walkthrough

`src/ingestion/chunker.py` - `TextChunker.__init__()`:
```python
self.splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=50,
    separators=["\n\n\n", "\n\n", "\n", " ", ".", ",", "?", "!", ""],
)
```

`chunk_document()` at line 47 splits one document:
```python
def chunk_document(self, document: Document) -> list[Document]:
    chunks = self.splitter.split_text(document.page_content)
    chunked_documents = []
    for idx, chunk in enumerate(chunks):
        chunk_metadata = document.metadata.copy()
        chunk_metadata.update({"chunk_index": idx, "total_chunks": len(chunks)})
        chunked_documents.append(Document(page_content=chunk, metadata=chunk_metadata))
    return chunked_documents
```

## Common Errors & Fixes

- **Error**: All chunks empty
  - Fix: Document shorter than chunk_size—returned as single chunk

- **Error**: Too many tiny chunks
  - Fix: Increase chunk_size or check separator order

## Related Files

- `src/ingestion/chunker.py` - TextChunker class
- `src/ingestion/__init__.py` - Exports
- `src/utils/config.py` - ChunkingSettings
