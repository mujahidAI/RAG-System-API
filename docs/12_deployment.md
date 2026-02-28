# Deployment

## What This Component Does

Docker containerization for the entire RAG system.

## Why It's Needed

- Reproducible deployments
- Isolated environments
- Easy scaling

## Docker Compose Services

1. **app**: FastAPI on port 8000
2. **qdrant**: Vector DB on port 6333

## Key Design Decisions

1. **Multi-stage build**: Minimal image size
2. **Non-root user**: Security best practice
3. **Health checks**: Service availability
4. **Volume**: Persistent Qdrant storage

## Deployment Steps

```bash
# Start services
docker-compose up -d

# Check health
curl http://localhost:8000/health

# Ingest documents
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"directory_path": "/app/data/raw"}'

# Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is quantum mechanics?"}'
```

## Connection to Other Components

- All services containerized
- Environment variables from .env
