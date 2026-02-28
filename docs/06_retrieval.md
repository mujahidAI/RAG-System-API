# Retrieval

## What This Component Does

Combines dense (semantic) and sparse (BM25) retrieval methods using weighted ensemble.

## Why It's Needed

- Dense: Finds semantically similar documents
- Sparse: Finds keyword-matched documents
- Hybrid: Best of both worlds

## Key Design Decisions

1. **Dense Weight**: 0.6 (60% semantic)
2. **Sparse Weight**: 0.4 (40% keyword)
3. **Top-K**: 10 documents retrieved

## Code Walkthrough

See `src/retrieval/retriever.py`:

```python
ensemble = EnsembleRetriever(
    retrievers=[dense_retriever, sparse_retriever],
    weights=[0.6, 0.4],
)
```

## Connection to Other Components

- Input: Query from API/generator
- Output: Documents to reranker
