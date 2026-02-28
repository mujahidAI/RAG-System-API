# Project Overview

## What This Component Does

The RAG (Retrieval-Augmented Generation) system is a production-grade pipeline that combines document retrieval with LLM generation. It provides a complete solution for building question-answering systems over custom document collections.

## Why It's Needed

Traditional LLMs are limited by their training data. RAG allows you to:
- Ground answers in your own documents
- Provide citations and sources
- Handle domain-specific questions
- Reduce hallucination

## Key Components

1. **Data Ingestion**: Load documents from various formats
2. **Embeddings**: Convert text to vector representations
3. **Vector Store**: Store and search embeddings efficiently
4. **Retrieval**: Find relevant documents for queries
5. **Generation**: Generate answers using retrieved context

## Tech Stack

- **LLM**: Ollama (mistral/llama3)
- **Embeddings**: HuggingFace BAAI/bge-large-en-v1.5
- **Vector DB**: Qdrant
- **Framework**: LangChain
- **API**: FastAPI
- **Evaluation**: RAGAS

## Architecture Flow

```
User Query → Query Transform → Retrieval → Re-ranking → Generation → Answer
                                  ↓
                            Document Store
                                  ↑
Documents → Ingestion → Chunking → Embedding → Storage
```
