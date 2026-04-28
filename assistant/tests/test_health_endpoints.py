"""Tests for health check endpoints"""

import os
from datetime import datetime
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from assistant.health.health_check_service import HealthStatus


@pytest.fixture
def client():
    """Create FastAPI TestClient for testing endpoints."""
    # Save current environment
    old_env = os.environ.copy()

    try:
        # Set dummy environment variables to avoid initialization errors
        # OpenAI settings
        os.environ["SETTINGS_OPENAI_API_KEY"] = "test-api-key"
        os.environ["SETTINGS_OPENAI_EMBEDDER"] = "test-embedder"
        os.environ["SETTINGS_OPENAI_MODEL"] = "test-model"
        os.environ["SETTINGS_OPENAI_BASE_URL"] = "http://test-url"

        # Prompt settings
        os.environ["SETTINGS_PROMPTS_REPHRASE_QUESTION_SYSTEM_PROMPT"] = "System prompt"
        os.environ["SETTINGS_PROMPTS_REPHRASE_QUESTION_USER_PROMPT"] = "User prompt"
        os.environ["SETTINGS_PROMPTS_REPHRASE_ANSWER_SYSTEM_PROMPT"] = "System prompt"
        os.environ["SETTINGS_PROMPTS_REPHRASE_ANSWER_USER_PROMPT"] = "User prompt"

        # Additional information settings
        os.environ["SETTINGS_ADDITIONAL_INFORMATION"] = "Additional context"

        # Dynamic knowledge settings
        os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_ENABLED"] = "false"
        os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_COLLECTION_NAME"] = "test"
        os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_DB_HOST"] = "localhost"
        os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_SYSTEM_PROMPT"] = "System prompt"
        os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_USER_PROMPT"] = "User prompt"

        # MCP settings - set path to non-existent file so it uses empty list
        os.environ["MCP_SETTINGS_PATH"] = "/tmp/non_existent_mcp_config.json"  # noqa: S108

        # Import app after setting environment variables
        from assistant.main import app

        yield TestClient(app)
    finally:
        # Restore environment
        os.environ.clear()
        os.environ.update(old_env)


def test_health_endpoint(mock_health_service):
    """Test health check endpoint returns 200."""
    # Set up environment
    old_env = os.environ.copy()
    try:
        os.environ["SETTINGS_OPENAI_API_KEY"] = "test-api-key"
        os.environ["SETTINGS_OPENAI_EMBEDDER"] = "test-embedder"
        os.environ["SETTINGS_OPENAI_MODEL"] = "test-model"
        os.environ["SETTINGS_OPENAI_BASE_URL"] = "http://test-url"
        os.environ["SETTINGS_PROMPTS_REPHRASE_QUESTION_SYSTEM_PROMPT"] = "System prompt"
        os.environ["SETTINGS_PROMPTS_REPHRASE_QUESTION_USER_PROMPT"] = "User prompt"
        os.environ["SETTINGS_PROMPTS_REPHRASE_ANSWER_SYSTEM_PROMPT"] = "System prompt"
        os.environ["SETTINGS_PROMPTS_REPHRASE_ANSWER_USER_PROMPT"] = "User prompt"
        os.environ["SETTINGS_ADDITIONAL_INFORMATION"] = "Additional context"
        os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_ENABLED"] = "false"
        os.environ["MCP_SETTINGS_PATH"] = "/tmp/non_existent_mcp_config.json"  # noqa: S108

        from assistant.main import app

        app.state.health_check_service = mock_health_service

        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    finally:
        os.environ.clear()
        os.environ.update(old_env)


def test_readiness_endpoint(mock_health_service):
    """Test readiness check endpoint returns 200."""
    # Set up environment
    old_env = os.environ.copy()
    try:
        os.environ["SETTINGS_OPENAI_API_KEY"] = "test-api-key"
        os.environ["SETTINGS_OPENAI_EMBEDDER"] = "test-embedder"
        os.environ["SETTINGS_OPENAI_MODEL"] = "test-model"
        os.environ["SETTINGS_OPENAI_BASE_URL"] = "http://test-url"
        os.environ["SETTINGS_PROMPTS_REPHRASE_QUESTION_SYSTEM_PROMPT"] = "System prompt"
        os.environ["SETTINGS_PROMPTS_REPHRASE_QUESTION_USER_PROMPT"] = "User prompt"
        os.environ["SETTINGS_PROMPTS_REPHRASE_ANSWER_SYSTEM_PROMPT"] = "System prompt"
        os.environ["SETTINGS_PROMPTS_REPHRASE_ANSWER_USER_PROMPT"] = "User prompt"
        os.environ["SETTINGS_ADDITIONAL_INFORMATION"] = "Additional context"
        os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_ENABLED"] = "false"
        os.environ["MCP_SETTINGS_PATH"] = "/tmp/non_existent_mcp_config.json"  # noqa: S108

        from assistant.main import app

        app.state.health_check_service = mock_health_service

        client = TestClient(app)
        response = client.get("/readiness")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert "version" in data
    finally:
        os.environ.clear()
        os.environ.update(old_env)


def test_health_response_format(mock_health_service):
    """Test health response has correct format."""
    # Set up environment
    old_env = os.environ.copy()
    try:
        os.environ["SETTINGS_OPENAI_API_KEY"] = "test-api-key"
        os.environ["SETTINGS_OPENAI_EMBEDDER"] = "test-embedder"
        os.environ["SETTINGS_OPENAI_MODEL"] = "test-model"
        os.environ["SETTINGS_OPENAI_BASE_URL"] = "http://test-url"
        os.environ["SETTINGS_PROMPTS_REPHRASE_QUESTION_SYSTEM_PROMPT"] = "System prompt"
        os.environ["SETTINGS_PROMPTS_REPHRASE_QUESTION_USER_PROMPT"] = "User prompt"
        os.environ["SETTINGS_PROMPTS_REPHRASE_ANSWER_SYSTEM_PROMPT"] = "System prompt"
        os.environ["SETTINGS_PROMPTS_REPHRASE_ANSWER_USER_PROMPT"] = "User prompt"
        os.environ["SETTINGS_ADDITIONAL_INFORMATION"] = "Additional context"
        os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_ENABLED"] = "false"
        os.environ["MCP_SETTINGS_PATH"] = "/tmp/non_existent_mcp_config.json"  # noqa: S108

        from assistant.main import app

        app.state.health_check_service = mock_health_service

        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200

        # Verify response schema
        data = response.json()
        assert isinstance(data["status"], str)
        assert isinstance(data["version"], str)
        assert len(data["status"]) > 0
        assert len(data["version"]) > 0
    finally:
        os.environ.clear()
        os.environ.update(old_env)


@pytest.fixture
def mock_health_service():
    """Create a mock HealthCheckService for testing endpoints."""
    service = MagicMock()
    service.get_overall_health.return_value = True
    service.server_health = {}
    return service


def test_health_endpoint_healthy(mock_health_service):
    """Test /health returns 200 with healthy status when all servers are healthy."""
    # Set up environment
    old_env = os.environ.copy()
    try:
        os.environ["SETTINGS_OPENAI_API_KEY"] = "test-api-key"
        os.environ["SETTINGS_OPENAI_EMBEDDER"] = "test-embedder"
        os.environ["SETTINGS_OPENAI_MODEL"] = "test-model"
        os.environ["SETTINGS_OPENAI_BASE_URL"] = "http://test-url"
        os.environ["SETTINGS_PROMPTS_REPHRASE_QUESTION_SYSTEM_PROMPT"] = "System prompt"
        os.environ["SETTINGS_PROMPTS_REPHRASE_QUESTION_USER_PROMPT"] = "User prompt"
        os.environ["SETTINGS_PROMPTS_REPHRASE_ANSWER_SYSTEM_PROMPT"] = "System prompt"
        os.environ["SETTINGS_PROMPTS_REPHRASE_ANSWER_USER_PROMPT"] = "User prompt"
        os.environ["SETTINGS_ADDITIONAL_INFORMATION"] = "Additional context"
        os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_ENABLED"] = "false"
        os.environ["MCP_SETTINGS_PATH"] = "/tmp/non_existent_mcp_config.json"  # noqa: S108

        from assistant.main import app

        app.state.health_check_service = mock_health_service

        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "2.3.0"
    finally:
        os.environ.clear()
        os.environ.update(old_env)


def test_health_endpoint_unhealthy(mock_health_service):
    """Test /health returns 503 with unhealthy status when any server is unhealthy."""
    # Create unhealthy server status
    mock_health_service.get_overall_health.return_value = False
    mock_health_service.server_health = {
        "server1": HealthStatus(
            server_name="server1", healthy=False, last_checked=datetime.now(), error_message="Connection refused"
        )
    }

    # Set up environment
    old_env = os.environ.copy()
    try:
        os.environ["SETTINGS_OPENAI_API_KEY"] = "test-api-key"
        os.environ["SETTINGS_OPENAI_EMBEDDER"] = "test-embedder"
        os.environ["SETTINGS_OPENAI_MODEL"] = "test-model"
        os.environ["SETTINGS_OPENAI_BASE_URL"] = "http://test-url"
        os.environ["SETTINGS_PROMPTS_REPHRASE_QUESTION_SYSTEM_PROMPT"] = "System prompt"
        os.environ["SETTINGS_PROMPTS_REPHRASE_QUESTION_USER_PROMPT"] = "User prompt"
        os.environ["SETTINGS_PROMPTS_REPHRASE_ANSWER_SYSTEM_PROMPT"] = "System prompt"
        os.environ["SETTINGS_PROMPTS_REPHRASE_ANSWER_USER_PROMPT"] = "User prompt"
        os.environ["SETTINGS_ADDITIONAL_INFORMATION"] = "Additional context"
        os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_ENABLED"] = "false"
        os.environ["MCP_SETTINGS_PATH"] = "/tmp/non_existent_mcp_config.json"  # noqa: S108

        from assistant.main import app

        app.state.health_check_service = mock_health_service

        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["version"] == "2.3.0"
        assert "servers" in data
        assert len(data["servers"]) == 1
        assert data["servers"][0]["name"] == "server1"
        assert data["servers"][0]["healthy"] is False
        assert "last_checked" in data["servers"][0]
        assert data["servers"][0]["error"] == "Connection refused"
    finally:
        os.environ.clear()
        os.environ.update(old_env)


def test_health_endpoint_unhealthy_multiple_servers(mock_health_service):
    """Test /health returns 503 with multiple server details when servers are unhealthy."""
    mock_health_service.get_overall_health.return_value = False
    mock_health_service.server_health = {
        "server1": HealthStatus(server_name="server1", healthy=True, last_checked=datetime.now(), error_message=None),
        "server2": HealthStatus(
            server_name="server2", healthy=False, last_checked=datetime.now(), error_message="Timeout"
        ),
    }

    # Set up environment
    old_env = os.environ.copy()
    try:
        os.environ["SETTINGS_OPENAI_API_KEY"] = "test-api-key"
        os.environ["SETTINGS_OPENAI_EMBEDDER"] = "test-embedder"
        os.environ["SETTINGS_OPENAI_MODEL"] = "test-model"
        os.environ["SETTINGS_OPENAI_BASE_URL"] = "http://test-url"
        os.environ["SETTINGS_PROMPTS_REPHRASE_QUESTION_SYSTEM_PROMPT"] = "System prompt"
        os.environ["SETTINGS_PROMPTS_REPHRASE_QUESTION_USER_PROMPT"] = "User prompt"
        os.environ["SETTINGS_PROMPTS_REPHRASE_ANSWER_SYSTEM_PROMPT"] = "System prompt"
        os.environ["SETTINGS_PROMPTS_REPHRASE_ANSWER_USER_PROMPT"] = "User prompt"
        os.environ["SETTINGS_ADDITIONAL_INFORMATION"] = "Additional context"
        os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_ENABLED"] = "false"
        os.environ["MCP_SETTINGS_PATH"] = "/tmp/non_existent_mcp_config.json"  # noqa: S108

        from assistant.main import app

        app.state.health_check_service = mock_health_service

        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert len(data["servers"]) == 2

        # Find server2 (unhealthy)
        server2 = next(s for s in data["servers"] if s["name"] == "server2")
        assert server2["healthy"] is False
        assert server2["error"] == "Timeout"

        # Find server1 (healthy - no error field)
        server1 = next(s for s in data["servers"] if s["name"] == "server1")
        assert server1["healthy"] is True
        assert "error" not in server1
    finally:
        os.environ.clear()
        os.environ.update(old_env)


def test_health_endpoint_healthy_no_servers(mock_health_service):
    """Test /health returns 200 when server_health is empty."""
    mock_health_service.get_overall_health.return_value = True
    mock_health_service.server_health = {}

    # Set up environment
    old_env = os.environ.copy()
    try:
        os.environ["SETTINGS_OPENAI_API_KEY"] = "test-api-key"
        os.environ["SETTINGS_OPENAI_EMBEDDER"] = "test-embedder"
        os.environ["SETTINGS_OPENAI_MODEL"] = "test-model"
        os.environ["SETTINGS_OPENAI_BASE_URL"] = "http://test-url"
        os.environ["SETTINGS_PROMPTS_REPHRASE_QUESTION_SYSTEM_PROMPT"] = "System prompt"
        os.environ["SETTINGS_PROMPTS_REPHRASE_QUESTION_USER_PROMPT"] = "User prompt"
        os.environ["SETTINGS_PROMPTS_REPHRASE_ANSWER_SYSTEM_PROMPT"] = "System prompt"
        os.environ["SETTINGS_PROMPTS_REPHRASE_ANSWER_USER_PROMPT"] = "User prompt"
        os.environ["SETTINGS_ADDITIONAL_INFORMATION"] = "Additional context"
        os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_ENABLED"] = "false"
        os.environ["MCP_SETTINGS_PATH"] = "/tmp/non_existent_mcp_config.json"  # noqa: S108

        from assistant.main import app

        app.state.health_check_service = mock_health_service

        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "servers" not in data
    finally:
        os.environ.clear()
        os.environ.update(old_env)
