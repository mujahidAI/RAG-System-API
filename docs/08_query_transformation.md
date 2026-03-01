# Query Transformation

## What It Does

Expands user queries using HyDE (Hypothetical Document Embedding) and/or multi-query expansion. Generates query variants to improve recall.

## Why It Exists

Users phrase questions differently than documents are written. "How does photosynthesis work?" may not match a document titled "Plant Energy Conversion." Transformation bridges this vocabulary gap.

## How It Fits In

```
User Query → [QueryTransformer] → Expanded queries
                     ↓
              [HyDE] → Generate hypothetical answer
              [Multi-Query] → Generate 3 variants
                     ↓
              [Retriever] → Search each variant
```

## Key Design Decisions

- **Disabled by default**: Adds latency; enable when recall is more important than speed
- **HyDE**: Generates answer-like text, uses for embedding search
- **Multi-query**: Creates paraphrases, retrieves for each, deduplicates

## Configuration

| Variable | Default | Effect |
|----------|---------|--------|
| `ENABLE_HYDE` | false | Enable hypothetical document embedding |
| `ENABLE_MULTI_QUERY` | false | Enable query variant generation |
| `MULTI_QUERY_COUNT` | 3 | Number of variants to generate |

## Code Walkthrough

`src/retrieval/query_transformer.py` - `QueryTransformer.transform()`:
```python
def transform(self, query: str) -> list[str]:
    queries = [query]
    if self.enable_hyde:
        hyde_query = self.transform_hyde(query)
        if hyde_query != query:
            queries.append(hyde_query)
    if self.enable_multi_query:
        multi_queries = self.transform_multi_query(query)
        queries.extend(multi_queries)
    return list(dict.fromkeys(queries))  # Deduplicate
```

`transform_hyde()` at line 55 generates hypothetical answer:
```python
hyde_chain = hyde_prompt | self.llm_chain | StrOutputParser()
hypothetical_answer = hyde_chain.invoke({"question": query})
```

## Common Errors & Fixes

- **Error**: LLM chain required
  - Fix: Pass `llm_chain` to QueryTransformer; both techniques need LLM

- **Error**: Slow query processing
  - Fix: Disable transformations; only use for low-volume, high-recall use cases

- **Error**: Duplicate results
  - Fix: Normalization happens in `dict.fromkeys()` call

## Related Files

- `src/retrieval/query_transformer.py` - QueryTransformer class
- `src/generation/generator.py` - Instantiates transformer
- `src/utils/config.py` - QueryTransformSettings
