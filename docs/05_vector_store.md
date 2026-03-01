# Vector Store

## What It Does

Stores embeddings and metadata in Qdrant, a high-performance vector database. Provides similarity search returning top-k results with scores.

## Why It Exists

Flat-file embedding storage is too slow at scale. Qdrant enables millisecond-speed similarity search across millions of vectors with filtering, pagination, and distance metrics.

## How It Fits In

```
Embeddings + Metadata → [QdrantStore.upsert_documents()] → Collection
                                                                    ↓
Query + Embedding → [QdrantStore.similarity_search()] → Relevant Docs
```

## Key Design Decisions

- **Cosine distance**: Matches L2-normalized embeddings; aligns with bge model
- **LangChain wrapper**: Simplifies integration; same interface as other vector stores
- **Collection per use-case**: Default "rag_documents" separates concerns

## Configuration

| Variable | Default | Effect |
|----------|---------|--------|
| `QDRANT_HOST` | localhost | Server address |
| `QDRANT_PORT` | 6333 | REST API port |
| `QDRANT_COLLECTION_NAME` | rag_documents | Collection name |
| `QDRANT_API_KEY` | None | Auth (optional) |

## Code Walkthrough

`src/vectorstore/qdrant_store.py` - `QdrantStore.upsert_documents()`:
```python
def upsert_documents(self, documents: list[Document], batch_size: int = 100):
    texts = [doc.page_content for doc in documents]
    metadatas = [doc.metadata for doc in documents]
    self._vectorstore = Qdrant.from_texts(
        texts=texts,
        embedding=self.embedder,
        metadatas=metadatas,
        collection_name=self.collection_name,
        host=self.host,
        port=self.port,
    )
```

`similarity_search()` at line 87:
```python
def similarity_search(self, query: str, k: int = 4, filter: dict = None):
    return self.vectorstore.similarity_search(query=query, k=k, filter=filter)
```

## Common Errors & Fixes

- **Error**: Collection not found
  - Fix: Run `create_collection()` or set `force_recreate=True`

- **Error**: Vector size mismatch
  - Fix: Ensure embedding dimension matches collection (1024)

- **Error**: Connection refused
  - Fix: Start Qdrant: `docker run -d -p 6333:6333 qdrant/qdrant`

## Related Files

- `src/vectorstore/qdrant_store.py` - QdrantStore class
- `src/retrieval/retriever.py` - Uses for dense retrieval
- `src/utils/config.py` - QdrantSettings
