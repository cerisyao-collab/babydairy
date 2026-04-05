"""API tests for Baby Diary endpoints"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from datetime import datetime

from src.api.main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_auth():
    """Mock authentication for testing"""
    with patch("src.api.auth.AuthService") as mock:
        yield mock


class TestHealthEndpoints:
    """Tests for health check endpoints"""

    def test_root_endpoint(self, client):
        """Test root endpoint returns API info"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["message"] == "Baby Diary API is running"

    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestAuthEndpoints:
    """Tests for authentication endpoints"""

    def test_login_endpoint_exists(self, client):
        """Test login endpoint exists"""
        # Should return 401 without valid WeChat code
        response = client.post("/api/auth/login", json={"code": "test_code"})
        # Will fail due to missing WeChat credentials, but endpoint exists
        assert response.status_code in [401, 500]

    def test_profile_requires_auth(self, client):
        """Test profile endpoint requires authentication"""
        response = client.get("/api/auth/profile")
        assert response.status_code == 403  # Forbidden without token


class TestRecordsEndpoints:
    """Tests for record management endpoints"""

    def test_list_records_requires_auth(self, client):
        """Test records list requires authentication"""
        response = client.get("/api/records/")
        assert response.status_code == 403

    def test_create_record_requires_auth(self, client):
        """Test record creation requires authentication"""
        response = client.post(
            "/api/records/",
            json={
                "type": "feeding",
                "details": {"amount_ml": 100},
            }
        )
        assert response.status_code == 403

    def test_get_record_requires_auth(self, client):
        """Test getting single record requires authentication"""
        response = client.get("/api/records/test-id")
        assert response.status_code == 403


class TestSummaryEndpoints:
    """Tests for summary endpoints"""

    def test_daily_summary_requires_auth(self, client):
        """Test daily summary requires authentication"""
        response = client.get("/api/summary/daily")
        assert response.status_code == 403


class TestConfigEndpoints:
    """Tests for configuration endpoints"""

    def test_get_config_requires_auth(self, client):
        """Test config get requires authentication"""
        response = client.get("/api/config/baby")
        assert response.status_code == 403

    def test_update_config_requires_auth(self, client):
        """Test config update requires authentication"""
        response = client.put("/api/config/baby", json={"baby_name": "Test"})
        assert response.status_code == 403


class TestAIEndpoints:
    """Tests for AI analysis endpoints"""

    def test_analyze_requires_auth(self, client):
        """Test AI analyze requires authentication"""
        response = client.post("/api/ai/analyze", json={})
        assert response.status_code == 403

    def test_chat_requires_auth(self, client):
        """Test AI chat requires authentication"""
        response = client.post("/api/ai/chat", json={"question": "test"})
        assert response.status_code == 403

    def test_ai_summary_requires_auth(self, client):
        """Test AI daily summary requires authentication"""
        response = client.get("/api/summary/daily/ai")
        assert response.status_code == 403


class TestOpenAPI:
    """Tests for OpenAPI documentation"""

    def test_openapi_json_available(self, client):
        """Test OpenAPI JSON specification is available"""
        response = client.get("/api/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data

    def test_docs_available(self, client):
        """Test Swagger docs are available"""
        response = client.get("/api/docs")
        assert response.status_code == 200

    def test_redoc_available(self, client):
        """Test ReDoc documentation is available"""
        response = client.get("/api/redoc")
        assert response.status_code == 200