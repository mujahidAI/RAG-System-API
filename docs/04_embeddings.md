# Embeddings

## What This Component Does

Converts text into dense vector representations using HuggingFace transformers.

## Why It's Needed

Vectors enable semantic similarity search - finding documents with similar meaning, not just keyword matches.

## Key Design Decisions

1. **Model**: BAAI/bge-large-en-v1.5 (1024 dimensions)
2. **Normalization**: L2 normalized for cosine similarity
3. **Batching**: Configurable batch size for efficiency

## Code Walkthrough

See `src/embeddings/embedder.py`:

```python
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-large-en-v1.5",
    model_kwargs={"device": "cpu"},
)
```

## Connection to Other Components

- Input: Text chunks
- Output: Embedding vectors to Qdrant
