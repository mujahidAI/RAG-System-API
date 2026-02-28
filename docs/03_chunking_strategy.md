# Chunking Strategy

## What This Component Does

Splits documents into smaller, semantically coherent chunks using recursive character splitting with configurable size and overlap.

## Why It's Needed

- Embedding models have token limits (typically 512)
- Smaller chunks improve retrieval precision
- Overlap maintains context between chunks

## Key Design Decisions

1. **Chunk Size**: 512 characters (configurable)
2. **Overlap**: 50 characters (configurable)
3. **Recursive Splitting**: Tries multiple separators in priority order

## Code Walkthrough

See `src/ingestion/chunker.py`:

```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=50,
    separators=["\n\n", "\n", " ", ".", ""],
)
```

## Connection to Other Components

- Input: Cleaned documents from `cleaner.py`
- Output: Chunked documents to `embedder.py`
