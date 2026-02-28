# RAG System

Production-grade Retrieval-Augmented Generation system with FastAPI, Qdrant, and LangChain.

## Features

- Multi-format document ingestion (TXT, PDF, DOCX, HTML)
- Hybrid retrieval (dense + sparse)
- Cross-encoder re-ranking
- Query transformation (HyDE, multi-query)
- RAGAS evaluation
- FastAPI REST API
- Docker deployment

## Quick Start

```bash
# Install dependencies
uv pip install -e .

# Generate dummy data
python data/generate_dummy_data.py

# Start services
docker-compose up -d

# Ingest documents
curl -X POST http://localhost:8000/ingest \
  -d '{"directory_path": "data/raw"}'

# Query
curl -X POST http://localhost:8000/query \
  -d '{"question": "What is quantum mechanics?"}'

# Evaluate
curl -X POST http://localhost:8000/evaluate \
  -d '{"questions": ["What is quantum mechanics?"]}'
```

## API Documentation

Visit http://localhost:8000/docs for Swagger UI.

## Configuration

Copy `.env.example` to `.env` and configure:

- Qdrant connection settings
- Embedding model
- LLM (Groq)
- Retrieval weights

## Testing

```bash
pytest tests/
```
