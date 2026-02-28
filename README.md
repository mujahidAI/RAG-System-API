# RAG System

Production-grade Retrieval-Augmented Generation system with FastAPI, Qdrant, and LangChain.

## Features

- Multi-format document ingestion (TXT, PDF, DOCX, HTML)
- Hybrid retrieval (dense + sparse)
- Cross-encoder re-ranking
- Query transformation (HyDE, multi-query)
- RAGAS evaluation
- FastAPI REST API
- React Frontend
- Docker deployment

## Quick Start (Backend)

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Ollama (for LLM) - optional

### Backend Setup

```bash
# Install dependencies
uv pip install -e .

# Generate dummy data
python data/generate_dummy_data.py

# Start Qdrant (vector database)
docker run -d -p 6333:6333 --name qdrant qdrant/qdrant:latest

# Run API locally
uvicorn src.api.main:app --reload --port 8000
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will be available at **http://localhost:5173**

---

## API Usage (via cURL)

### Ingest Documents
```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"directory_path": "data/raw"}'
```

### Query
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is quantum mechanics?"}'
```

### Evaluate
```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## Docker Deployment

```bash
# Start all services (Backend + Qdrant)
docker-compose up -d

# Frontend runs separately
cd frontend && npm run dev
```

---

## API Documentation

Visit http://localhost:8000/docs for Swagger UI.

---

## Configuration

Copy `.env.example` to `.env` and configure:

- Qdrant connection settings
- Embedding model
- LLM (Ollama)
- Retrieval weights

---

## Testing

```bash
pytest tests/
```
