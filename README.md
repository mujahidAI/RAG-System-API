# RAG System

Production-grade Retrieval-Augmented Generation system with FastAPI, Qdrant, and LangChain.

## What This Project Is

A complete RAG pipeline that ingests documents (TXT, PDF, DOCX, HTML), stores embeddings in Qdrant, and answers questions using hybrid retrieval with an LLM. Includes a React frontend and Docker deployment.

## Architecture

```
                         User Query
                              │
                              ▼
                    ┌─────────────────┐
                    │   FastAPI API   │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌───────────────┐   ┌──────────────┐   ┌────────────────┐
│  Ingestion    │   │   Query      │   │   Evaluate     │
│  Pipeline     │   │   Pipeline   │   │   Pipeline     │
└───────┬───────┘   └───────┬──────┘   └───────┬────────┘
        │                   │                  │
        ▼                   ▼                  ▼
   Documents           Generator            Metrics
   (files)            + Retriever          (RAGAS)
        │                   │                  │
        ▼                   ▼                  ▼
   ┌────────┐        ┌──────────┐        ┌─────────┐
   │ Chunker│──────▶ │ Qdrant  │◀───────│   LLM   │
   └────────┘        └──────────┘        └─────────┘
        │                   │
        ▼                   ▼
   ┌────────┐        ┌──────────┐
   │Embedder│──────▶ │ Vector   │
   └────────┘        │ Store    │
                     └──────────┘
```

## Quickstart

```bash
# 1. Clone and setup
cd RAG-system-api
cp .env.example .env

# 2. Start Qdrant
docker run -d -p 6333:6333 --name qdrant qdrant/qdrant:latest

# 3. Install and run API
uv pip install -e .
uvicorn src.api.main:app --reload --port 8000

# 4. Ingest documents
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"directory_path": "data/raw"}'

# 5. Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is quantum mechanics?"}'

# 6. Frontend (optional)
cd frontend && npm install && npm run dev
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `QDRANT_HOST` | localhost | Qdrant server |
| `QDRANT_PORT` | 6333 | REST API port |
| `QDRANT_COLLECTION_NAME` | rag_documents | Collection name |
| `EMBEDDING_MODEL_NAME` | BAAI/bge-large-en-v1.5 | Embedding model |
| `EMBEDDING_DEVICE` | cpu | cpu or cuda |
| `LLM_PROVIDER` | ollama | LLM backend |
| `OLLAMA_MODEL` | mistral | Model name |
| `RETRIEVAL_DENSE_WEIGHT` | 0.6 | Semantic weight |
| `RETRIEVAL_SPARSE_WEIGHT` | 0.4 | BM25 weight |

## API Reference

| Method | Endpoint | Purpose | Example |
|--------|---------|---------|---------|
| POST | `/ingest` | Load documents | `{"directory_path": "data/raw"}` |
| POST | `/query` | Ask question | `{"question": "..."}` |
| POST | `/evaluate` | Run metrics | `{}` |
| GET | `/health` | Status check | — |

Docs at http://localhost:8000/docs

## Running Evaluations

```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{}'
```

Returns: faithfulness, answer_relevancy, context_precision, context_recall.

## Project Structure

```
src/
├── api/           # FastAPI routes and middleware
├── embeddings/    # HuggingFace embedder
├── evaluation/    # RAGAS metrics
├── generation/    # LLM chain and prompts
├── ingestion/     # Loader, cleaner, chunker
├── retrieval/     # Hybrid retriever, reranker
├── utils/         # Config and logging
└── vectorstore/   # Qdrant integration
data/raw/          # Sample documents
frontend/          # React UI
docs/              # Full documentation
tests/             # Pytest tests
```

## Troubleshooting

1. **Qdrant refused**: `docker run -d -p 6333:6333 qdrant/qdrant`
2. **LLM not responding**: Ensure `ollama serve` and `ollama pull mistral`
3. **No query results**: Run `/ingest` first
4. **Frontend CORS**: API must be same domain or configure CORS
