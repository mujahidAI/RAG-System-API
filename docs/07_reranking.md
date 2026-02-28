# Re-ranking

## What This Component Does

Uses cross-encoder model to re-rank retrieved documents for better relevance.

## Why It's Needed

Initial retrieval may include less relevant documents. Re-ranking improves quality by scoring query-document pairs.

## Key Design Decisions

1. **Model**: cross-encoder/ms-marco-MiniLM-L-6-v2
2. **Top-K**: 3 final results after re-ranking

## Code Walkthrough

See `src/retrieval/reranker.py`:

```python
scores = cross_encoder.score(query_doc_pairs)
reranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
```

## Connection to Other Components

- Input: 10 documents from retrieval
- Output: Top 3 documents to generator
