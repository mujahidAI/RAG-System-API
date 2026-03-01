# Project Overview

## What It Does

The RAG system answers questions by retrieving relevant documents from a vector store and generating natural language responses using an LLM. It processes raw documents through ingestion, embedding, and storage, then uses hybrid retrieval (semantic + keyword search) with optional re-ranking to find the best context for generation.

## Why It Exists

Traditional LLMs are limited to knowledge in their training data. Without RAG, the system cannot answer domain-specific questions or cite sources. If removed, the system would rely solely on LLM knowledge—leading to hallucinations and no source attribution.

## How It Fits In

```
User Query
    ↓
[API Route] → Query Transform (HyDE/Multi-Query)
    ↓
[Retriever] → Hybrid: Dense (Qdrant) + Sparse (BM25)
    ↓
[Reranker] → Cross-encoder, top-3
    ↓
[Generator] → LLM + Context → Answer + Sources
```

## Key Design Decisions

- **Hybrid retrieval**: Combines semantic (dense) and keyword (sparse) to catch both meaning and exact matches
- **Optional re-ranking**: Uses cross-encoder for precision after initial broad retrieval
- **Source citations**: Every answer includes metadata for verification
- **Modular pipeline**: Each stage is independent and configurable

## Configuration

| Variable | Default | Effect |
|----------|---------|--------|
| `QDRANT_HOST` | localhost | Qdrant server address |
| `QDRANT_PORT` | 6333 | REST API port |
| `QDRANT_COLLECTION_NAME` | rag_documents | Vector store collection |
| `LLM_PROVIDER` | ollama | LLM backend (ollama/huggingface) |
| `OLLAMA_MODEL` | mistral | Model name for generation |
| `LOG_LEVEL` | INFO | Logging verbosity |

## Code Walkthrough

The main pipeline in `src/api/routes/query.py`:
```python
# 1. Get generator with configured components
generator = get_generator()

# 2. Generate answer with retrieval + generation
result = generator.generate(question)

# 3. Return answer + sources
return QueryResponse(answer=result["answer"], sources=result["sources"])
```

The generator chain in `src/generation/generator.py`:
```python
# LCEL chain: prompt | llm
self._chain = self.prompt | self.llm

# Generate with context
answer = self.chain.invoke({"context": context, "question": query})
```

## Common Errors & Fixes

- **Error**: `ConnectionRefusedError` to Qdrant
  - Fix: Ensure Qdrant is running: `docker run -d -p 6333:6333 qdrant/qdrant`

- **Error**: `Model not found` for embeddings
  - Fix: HuggingFace model downloads on first use; check network access

- **Error**: Ollama not responding
  - Fix: Start Ollama: `ollama serve` and pull model: `ollama pull mistral`

## Related Files

- `src/api/main.py` - FastAPI app entry point
- `src/generation/generator.py` - Pipeline orchestration
- `src/retrieval/retriever.py` - Hybrid retrieval logic
- `.env.example` - All configuration variables
