# Vector Store

## What This Component Does

Stores and searches document embeddings using Qdrant vector database.

## Why It's Needed

- Efficient similarity search at scale
- Persistent storage of embeddings
- Fast retrieval of top-k results

## Key Design Decisions

1. **Distance Metric**: Cosine similarity
2. **Collection**: rag_documents
3. **Client**: qdrant-client with LangChain wrapper

## Code Walkthrough

See `src/vectorstore/qdrant_store.py`:

```python
qdrant = Qdrant.from_texts(
    texts=texts,
    embedding=embedder,
    collection_name="rag_documents",
    host="localhost",
    port=6333,
)
```

## Connection to Other Components

- Input: Embeddings from embedder
- Output: Search results to retriever
