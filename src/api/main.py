"""FastAPI application entry point.

This is the main FastAPI application that provides REST API endpoints
for the RAG system including ingestion, querying, and evaluation.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.middleware import setup_middleware
from src.api.routes import ingest, query, evaluate
from src.api.schemas import HealthResponse
from src.utils.logger import get_logger
from src.utils.config import get_settings

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    settings = get_settings()
    
    app = FastAPI(
        title="RAG System API",
        description="Production-grade RAG system with FastAPI, Qdrant, and LangChain",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    setup_middleware(app)
    
    app.include_router(ingest.router)
    app.include_router(query.router)
    app.include_router(evaluate.router)
    
    @app.get("/", response_model=dict, tags=["Root"])
    async def root():
        """Root endpoint."""
        return {
            "message": "RAG System API",
            "version": "1.0.0",
            "docs": "/docs",
        }
    
    @app.get("/health", response_model=HealthResponse, tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            services={
                "api": "running",
                "qdrant": "checking",
            },
        )
    
    logger.info("FastAPI application created")
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    
    uvicorn.run(
        "src.api.main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.api.reload,
    )
