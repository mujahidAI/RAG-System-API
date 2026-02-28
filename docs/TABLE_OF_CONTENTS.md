# RAG System Documentation

## Learning Path

This table of contents provides an ordered learning path through the RAG system codebase. Read each document in order to fully understand the entire system.

| # | Document | Description |
|---|----------|-------------|
| 1 | [01_project_overview.md](01_project_overview.md) | High-level overview of the RAG system architecture, components, and tech stack |
| 2 | [02_data_ingestion.md](02_data_ingestion.md) | Document loading from multiple formats (TXT, PDF, DOCX, HTML) |
| 3 | [03_chunking_strategy.md](03_chunking_strategy.md) | Text chunking using RecursiveCharacterTextSplitter for optimal retrieval |
| 4 | [04_embeddings.md](04_embeddings.md) | HuggingFace embeddings with BAAI/bge-large-en-v1.5 model |
| 5 | [05_vector_store.md](05_vector_store.md) | Qdrant vector database integration for document storage |
| 6 | [06_retrieval.md](06_retrieval.md) | Hybrid retrieval combining dense (semantic) and sparse (BM25) methods |
| 7 | [07_reranking.md](07_reranking.md) | Cross-encoder re-ranking to improve retrieval quality |
| 8 | [08_query_transformation.md](08_query_transformation.md) | HyDE and multi-query expansion for better retrieval |
| 9 | [09_generation.md](09_generation.md) | LLM chain for answer generation with context |
| 10 | [10_evaluation.md](10_evaluatibon.md) | RAGAS metrics for pipeline evaluation |
| 11 | [11_api_design.md](11_api_design.md) | FastAPI endpoints and middleware |
| 12 | [12_deployment.md](12_deployment.md) | Docker and Docker Compose deployment |

## Quick Reference

- **API Endpoints**: `/docs` for Swagger UI
- **Health Check**: `GET /health`
- **Ingest**: `POST /ingest`
- **Query**: `POST /query`
- **Evaluate**: `POST /evaluate`

## Prerequisites

Before reading the documentation:
1. Python 3.11+
2. Docker and Docker Compose
3. Ollama (for LLM)
4. Basic understanding of RAG architecture
