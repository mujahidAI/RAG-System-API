# Deployment

## What It Does

Containers the entire RAG system using Docker. Runs FastAPI and Qdrant as separate services with health checks, persistent storage, and networking.

## Why It Exists

Deployment ensures reproducibility. Docker guarantees the same environment across machines. Separate services allow independent scaling—Qdrant can grow without restarting the API.

## Architecture

```
┌─────────────────────────────────────┐
│  docker-compose.yml                 │
│                                     │
│  ┌─────────────┐   ┌─────────────┐ │
│  │ app (8000)  │   │ qdrant     │ │
│  │ FastAPI     │──▶│ (6333/6334)│ │
│  └─────────────┘   └─────────────┘ │
│         ↓                          │
│   /api/* (proxied)                 │
└─────────────────────────────────────┘
```

## Key Design Decisions

- **Multi-stage Dockerfile**: Reduces final image size
- **Non-root user**: Security—container cannot modify system files
- **Health checks**: Ensures Qdrant is ready before API starts
- **Persistent volume**: Qdrant data survives restarts

## Configuration

| Variable | Default | Effect |
|----------|---------|--------|
| Ports | 8000, 6333, 6334 | API, Qdrant REST, Qdrant gRPC |

## Running

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f app

# Stop
docker-compose down
```

For local development without Docker:
```bash
docker run -d -p 6333:6333 qdrant/qdrant
uvicorn src.api.main:app --reload
```

## Common Errors & Fixes

- **Error**: App container exits immediately
  - Fix: Check Qdrant running; check `OLLAMA_BASE_URL` if using Ollama

- **Error**: Cannot connect to Qdrant from app
  - Fix: Use service name "qdrant" as host in Docker network

- **Error**: Data lost on restart
  - Fix: Volume `qdrant_data` persists—don't use `--volumes` flag with down

## Related Files

- `docker-compose.yml` - Service orchestration
- `docker/Dockerfile` - App container image
- `.env` - Environment variables passed to containers
