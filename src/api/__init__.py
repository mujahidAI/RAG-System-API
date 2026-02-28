"""API module for FastAPI endpoints.

This module provides REST API endpoints for:
- Document ingestion
- Query answering
- RAG evaluation
"""

from src.api.main import app, create_app

__all__ = ["app", "create_app"]
