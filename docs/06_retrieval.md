# Retrieval

## What It Does

Finds relevant documents using hybrid search: 60% dense (semantic, Qdrant) + 40% sparse (keyword, BM25). Returns top-k candidates for re-ranking.

## Why It Exists

Dense alone misses exact keyword matches. Sparse alone misses semantic matches. Hybrid combines both—catching synonyms (dense) and exact terms (sparse)—for higher recall.

## How It Fits In

```
Query → [HybridRetriever] → Combined top-10 results
                  ↓
            [Dense: Qdrant] → Semantic similarity
            [Sparse: BM25] → Keyword matching
```

## Key Design Decisions

- **60/40 weight split**: Favor semantic but keep keyword contribution
- **Top-10 before re-ranking**: Enough candidates for reranker to filter
- **EnsembleRetriever**: LangChain's standard hybrid implementation

## Configuration

| Variable | Default | Effect |
|----------|---------|--------|
| `RETRIEVAL_TOP_K` | 10 | Documents retrieved before re-ranking |
| `RETRIEVAL_DENSE_WEIGHT` | 0.6 | Weight for semantic search |
| `RETRIEVAL_SPARSE_WEIGHT` | 0.4 | Weight for BM25 |

## Code Walkthrough

`src/retrieval/retriever.py` - `HybridRetriever.__init__()`:
```python
self._ensemble_retriever = EnsembleRetriever(
    retrievers=[self.dense_retriever, self.sparse_retriever],
    weights=[self.dense_weight, self.sparse_weight],  # [0.6, 0.4]
)
```

`retrieve()` at line 83:
```python
def retrieve(self, query: str) -> list[Document]:
    results = self.ensemble_retriever.invoke(query)
    return results
```

## Common Errors & Fixes

- **Error**: BM25 returns no results
  - Fix: Ensure documents were set via `set_documents()` before retrieval

- **Error**: Empty dense results
  - Fix: Check Qdrant has data: `store.get_collection_info()`

- **Error**: Weights don't sum to 1
  - Fix: Adjust in config; currently accepts any but warns if skewed

## Related Files

- `src/retrieval/retriever.py` - HybridRetriever class
- `src/retrieval/reranker.py` - Re-ranks retrieved results
- `src/utils/config.py` - RetrievalSettings
