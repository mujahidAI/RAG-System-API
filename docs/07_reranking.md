# Re-ranking

## What It Does

Re-scales top-10 retrieved documents using a cross-encoder, returning top-3 for generation. Provides more precise relevance ordering than initial retrieval.

## Why It Exists

Initial retrieval optimizes for speed (dense uses approximations; sparse ignores context). Cross-encoder scores exact query-document pairs, improving precision at the cost of speed—worthwhile for final context.

## How It Fits In

```
[HybridRetriever] → 10 documents → [Reranker] → Top-3 → [Generator]
```

## Key Design Decisions

- **MiniLM cross-encoder**: Fast (6 layers) but accurate enough for reranking
- **Top-3 output**: Balances context breadth with LLM token limits
- **Score logging**: Enables debugging/observability

## Configuration

| Variable | Default | Effect |
|----------|---------|--------|
| `RERANKER_MODEL_NAME` | cross-encoder/ms-marco-MiniLM-L-6-v2 | HuggingFace model |
| `RERANKER_TOP_K` | 3 | Results after re-ranking |

## Code Walkthrough

`src/retrieval/reranker.py` - `Reranker.rerank()`:
```python
def rerank(self, query: str, documents: list[Document], top_k: int = 3):
    doc_texts = [doc.page_content for doc in documents]
    query_doc_pairs = [[query, doc] for doc in doc_texts]
    scores = self._cross_encoder.score(query_doc_pairs)
    doc_scores = list(zip(documents, scores))
    doc_scores.sort(key=lambda x: x[1], reverse=True)
    return doc_scores[:top_k]
```

## Common Errors & Fixes

- **Error**: Model not loading
  - Fix: Check HuggingFace cache; first use downloads ~100MB

- **Error**: All scores are zero
  - Fix: Usually normal—MiniLM outputs raw scores, not probabilities

- **Error**: Too few results returned
  - Fix: Ensure at least top_k documents were retrieved

## Related Files

- `src/retrieval/reranker.py` - Reranker class
- `src/generation/generator.py` - Uses reranked results
- `src/utils/config.py` - RerankerSettings
