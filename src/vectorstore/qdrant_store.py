"""Qdrant vector database integration for the RAG system.

This module provides Qdrant vector store integration with LangChain,
supporting document upserting, similarity search, and collection management.
"""

from pathlib import Path
from typing import Any, Optional

from langchain_core.documents import Document
from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from src.embeddings.embedder import Embedder
from src.utils.logger import get_logger
from src.utils.config import get_settings

logger = get_logger(__name__)


class QdrantStore:
    """Qdrant vector store wrapper with LangChain integration.
    
    Provides methods for:
    - Creating and managing collections
    - Upserting documents with embeddings
    - Similarity search with filtering
    - Collection deletion
    """
    
    def __init__(
        self,
        embedder: Embedder,
        collection_name: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        api_key: Optional[str] = None,
    ):
        """Initialize the Qdrant store.
        
        Args:
            embedder: Embedder instance for generating vectors
            collection_name: Name of the collection
            host: Qdrant host
            port: Qdrant port
            api_key: Optional API key for authentication
        """
        settings = get_settings()
        
        self.collection_name = collection_name or settings.qdrant.collection_name
        self.host = host or settings.qdrant.host
        self.port = port or settings.qdrant.port
        self.api_key = api_key or settings.qdrant.api_key
        
        self.embedder = embedder
        
        self._client: Optional[QdrantClient] = None
        self._vectorstore: Optional[Qdrant] = None
        
        logger.info("QdrantStore initialized", extra={
            "collection_name": self.collection_name,
            "host": self.host,
            "port": self.port,
        })
    
    @property
    def client(self) -> QdrantClient:
        """Get or create Qdrant client."""
        if self._client is None:
            self._client = QdrantClient(
                host=self.host,
                port=self.port,
                api_key=self.api_key,
            )
        return self._client
    
    @property
    def vectorstore(self) -> Qdrant:
        """Get or create LangChain Qdrant vectorstore."""
        if self._vectorstore is None:
            self._vectorstore = Qdrant.from_documents(
                documents=[],
                embedding=self.embedder,
                collection_name=self.collection_name,
                host=self.host,
                port=self.port,
                api_key=self.api_key,
            )
        return self._vectorstore
    
    def create_collection(
        self,
        vector_size: Optional[int] = None,
        distance: Distance = Distance.COSINE,
        force_recreate: bool = False,
    ) -> bool:
        """Create a Qdrant collection."""
        if vector_size is None:
            vector_size = self.embedder.embedding_dimension
        
        if force_recreate:
            self.delete_collection()
        
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if self.collection_name in collection_names:
            return False
        
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=distance,
            ),
        )
        return True
    
    def upsert_documents(
        self,
        documents: list[Document],
        batch_size: int = 100,
    ) -> dict[str, Any]:
        """Upsert documents with their embeddings into Qdrant."""
        if not documents:
            return {"upserted_count": 0, "batch_count": 0}
        
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        
        self._vectorstore = Qdrant.from_texts(
            texts=texts,
            embedding=self.embedder,
            metadatas=metadatas,
            collection_name=self.collection_name,
            host=self.host,
            port=self.port,
            api_key=self.api_key,
            batch_size=batch_size,
        )
        
        return {
            "upserted_count": len(documents),
            "batch_count": (len(documents) + batch_size - 1) // batch_size,
            "collection_name": self.collection_name,
        }
    
    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[dict[str, Any]] = None,
        score_threshold: Optional[float] = None,
    ) -> list[Document]:
        """Perform similarity search."""
        return self.vectorstore.similarity_search(
            query=query,
            k=k,
            filter=filter,
            score_threshold=score_threshold,
        )
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        filter: Optional[dict[str, Any]] = None,
    ) -> list[tuple[Document, float]]:
        """Perform similarity search with scores."""
        return self.vectorstore.similarity_search_with_score(
            query=query,
            k=k,
            filter=filter,
        )
    
    def delete_collection(self) -> bool:
        """Delete the collection."""
        try:
            self.client.delete_collection(collection_name=self.collection_name)
            self._vectorstore = None
            return True
        except Exception:
            return False
    
    def get_collection_info(self) -> dict[str, Any]:
        """Get collection information."""
        try:
            info = self.client.get_collection(collection_name=self.collection_name)
            return {
                "name": info.name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status.name,
            }
        except Exception as e:
            return {"error": str(e)}
    
    def exists(self) -> bool:
        """Check if collection exists."""
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            return self.collection_name in collection_names
        except Exception:
            return False


def get_qdrant_store(embedder: Optional[Embedder] = None) -> QdrantStore:
    """Get a configured QdrantStore instance."""
    from src.embeddings.embedder import get_embedder
    if embedder is None:
        embedder = get_embedder()
    return QdrantStore(embedder=embedder)
