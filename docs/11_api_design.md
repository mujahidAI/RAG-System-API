# API Design

## What This Component Does

FastAPI REST endpoints for ingestion, querying, and evaluation.

## Why It's Needed

- Easy integration with applications
- Standard HTTP interface
- Automatic documentation

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ingest` | POST | Load and index documents |
| `/query` | POST | Ask questions |
| `/evaluate` | POST | Run RAGAS evaluation |
| `/health` | GET | Health check |

## Middleware

- Logging: JSON structured logs
- Timing: Response time headers
- Error handling: JSON error responses

## Code Walkthrough

See `src/api/main.py`:

```python
app.include_router(ingest.router)
app.include_router(query.router)
app.include_router(evaluate.router)
```

## Connection to Other Components

- All components integrated through API
- `/docs` for Swagger documentation
