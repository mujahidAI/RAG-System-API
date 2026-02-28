"""Tests for API module."""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


class TestAPI:
    """Tests for FastAPI endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_ingest_endpoint_schema(self, client):
        """Test ingest endpoint request schema."""
        # Should require either directory_path or file_paths
        response = client.post("/ingest", json={})
        assert response.status_code != 200

    def test_query_endpoint_schema(self, client):
        """Test query endpoint requires question."""
        response = client.post("/query", json={})
        assert response.status_code != 200

    def test_evaluate_endpoint_schema(self, client):
        """Test evaluate endpoint requires questions."""
        response = client.post("/evaluate", json={})
        assert response.status_code != 200
