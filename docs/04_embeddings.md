# Embeddings

## What It Does

Converts text chunks into dense vector representations (1024 dimensions) using the BAAI/bge-large-en-v1.5 model. Enables semantic similarity search.

## Why It Exists

Vectors enable "find documents like this" queries—matching meaning, not just keywords. Without embeddings, retrieval relies solely on keyword overlap, missing synonyms and related concepts.

## How It Fits In

```
Text Chunks → [Embedder.embed_documents()] → Embedding vectors
                                                  ↓
                                            [QdrantStore]
```

## Key Design Decisions

- **BAAI/bge-large-en-v1.5**: State-of-the-art open-source, 1024 dimensions
- **L2 normalization**: Enables cosine similarity via dot product
- **Batch processing**: Configurable batch size reduces API overhead

## Configuration

| Variable | Default | Effect |
|----------|---------|--------|
| `EMBEDDING_MODEL_NAME` | BAAI/bge-large-en-v1.5 | HuggingFace model |
| `EMBEDDING_DEVICE` | cpu | cpu or cuda |
| `EMBEDDING_BATCH_SIZE` | 32 | Documents per batch |
| `EMBEDDING_VECTOR_SIZE` | 1024 | Vector dimensions |

## Code Walkthrough

`src/embeddings/embedder.py` - `Embedder.__init__()`:
```python
self._embeddings_model = HuggingFaceEmbeddings(
    model_name=self.model_name,
    model_kwargs={"device": self.device},
    encode_kwargs={"normalize_embeddings": True},
)
```

`embed_documents()` at line 54 processes batches:
```python
def embed_documents(self, texts: list[str]) -> list[list[float]]:
    return self._embeddings_model.embed_documents(texts)
```

## Common Errors & Fixes

- **Error**: Model download fails
  - Fix: Check HuggingFace access; set HF_HOME for custom cache

- **Error**: Out of memory with large batches
  - Fix: Reduce `EMBEDDING_BATCH_SIZE` in config

- **Error**: Dimension mismatch with Qdrant
  - Fix: Ensure `EMBEDDING_VECTOR_SIZE` matches model (1024 for bge-large)

## Related Files

- `src/embeddings/embedder.py` - Embedder class
- `src/vectorstore/qdrant_store.py` - Stores embeddings
- `src/utils/config.py` - EmbeddingSettings
