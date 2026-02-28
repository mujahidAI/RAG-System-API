# Query Transformation

## What This Component Does

Improves retrieval through HyDE and multi-query expansion techniques.

## Why It's Needed

- Users may phrase questions differently than documents
- HyDE generates hypothetical answers for better matching
- Multi-query expands to capture different phrasings

## Key Design Decisions

1. **HyDE**: Generates hypothetical answer, uses for retrieval
2. **Multi-query**: Generates 3 variants, retrieves for each

## Code Walkthrough

See `src/retrieval/query_transformer.py`:

```python
hyde_prompt | llm | StrOutputParser()  # Generate hypothetical answer
multi_query_prompt | llm | StrOutputParser()  # Generate variants
```

## Connection to Other Components

- Input: Original user query
- Output: Transformed queries to retriever
