# RAG System Documentation

## Learning Path

Read in order from foundations to production deployment.

---

## Phase 1 — Foundations

| Doc | What You'll Learn | Read Time |
|-----|-------------------|-----------|
| [01_project_overview.md](01_project_overview.md) | System architecture, data flow, and configuration | 4 min |
| [02_data_ingestion.md](02_data_ingestion.md) | Loading multi-format documents, cleaning, chunking | 5 min |
| [03_chunking_strategy.md](03_chunking_strategy.md) | Recursive splitting with overlap for context | 3 min |
| [04_embeddings.md](04_embeddings.md) | Text-to-vector conversion with BAAI model | 3 min |

---

## Phase 2 — Core Pipeline

| Doc | What You'll Learn | Read Time |
|-----|-------------------|-----------|
| [05_vector_store.md](05_vector_store.md) | Qdrant for similarity search at scale | 3 min |
| [06_retrieval.md](06_retrieval.md) | Hybrid dense + sparse retrieval | 4 min |
| [07_reranking.md](07_reranking.md) | Cross-encoder for precision | 3 min |
| [08_query_transformation.md](08_query_transformation.md) | HyDE and multi-query expansion | 3 min |
| [09_generation.md](09_generation.md) | LLM chain with context and citations | 4 min |

---

## Phase 3 — Production

| Doc | What You'll Learn | Read Time |
|-----|-------------------|-----------|
| [10_evaluation.md](10_evaluation.md) | RAGAS metrics for pipeline quality | 3 min |
| [11_api_design.md](11_api_design.md) | FastAPI endpoints and middleware | 4 min |
| [12_deployment.md](12_deployment.md) | Docker Compose setup and运维 | 4 min |

---

## Quick Reference

| Need | Doc |
|------|-----|
| Add new document format | 02_data_ingestion.md |
| Change chunk size | 03_chunking_strategy.md |
| Switch embedding model | 04_embeddings.md |
| Adjust retrieval weights | 06_retrieval.md |
| Enable query expansion | 08_query_transformation.md |
| Run evaluation | 10_evaluation.md |
| Deploy to production | 12_deployment.md |
