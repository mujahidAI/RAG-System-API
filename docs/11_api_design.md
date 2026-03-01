# API Design

## What It Does

Provides REST endpoints for ingestion, querying, evaluation, and health checks. Handles HTTP requests, validates input, and returns structured JSON responses.

## Why It Exists

Without an API, users must interact with the pipeline programmatically. The API provides a clean HTTP interface usable from any language or client—including the React frontend.

## How It Fits In

```
HTTP Request → [FastAPI] → Route Handler → Component
                    ↓
            Middleware (logging, timing, errors)
```

## Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/ingest` | Load documents from directory |
| POST | `/query` | Ask a question |
| POST | `/evaluate` | Run RAGAS metrics |
| GET | `/health` | Check backend status |
| GET | `/docs` | Swagger UI |

## Middleware

- **Logging**: JSON structured logs with request/response info
- **Timing**: Adds `X-Process-Time` header (milliseconds)
- **Error handling**: Catches exceptions, returns JSON error response

## Configuration

| Variable | Default | Effect |
|----------|---------|--------|
| `API_HOST` | 0.0.0.0 | Bind address |
| `API_PORT` | 8000 | HTTP port |
| `API_RELOAD` | false | Auto-reload in dev |

## Code Walkthrough

`src/api/main.py` - Router setup:
```python
def create_app() -> FastAPI:
    app = FastAPI(title="RAG System API")
    setup_middleware(app)
    app.include_router(ingest.router)
    app.include_router(query.router)
    app.include_router(evaluate.router)
    return app
```

`src/api/routes/query.py` - Query endpoint:
```python
@router.post("", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    generator = get_generator()
    result = generator.generate(request.question)
    return QueryResponse(answer=result["answer"], sources=result["sources"])
```

## Common Errors & Fixes

- **Error**: CORS blocked
  - Fix: Middleware allows all origins by default

- **Error**: Request validation fails
  - Fix: Check request body matches schema in `/docs`

- **Error**: 500 on endpoint
  - Fix: Check Qdrant running; check logs for details

## Related Files

- `src/api/main.py` - App factory
- `src/api/routes/ingest.py`, `query.py`, `evaluate.py` - Route handlers
- `src/api/schemas.py` - Pydantic models
- `src/api/middleware.py` - Request/response middleware
