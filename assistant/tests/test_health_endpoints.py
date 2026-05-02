"""Tests for health check endpoints"""

import json
import os
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


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


def test_health_endpoint(client):
    """Test health check endpoint returns 200."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_readiness_endpoint(client):
    """Test readiness check endpoint returns 200."""
    response = client.get("/readiness")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert "version" in data


def test_health_response_format(client):
    """Test health response has correct format."""
    response = client.get("/health")
    assert response.status_code == 200

    # Verify response schema
    data = response.json()
    assert isinstance(data["status"], str)
    assert isinstance(data["version"], str)
    assert len(data["status"]) > 0
    assert len(data["version"]) > 0


@patch("assistant.endpoints.health_endpoints.MultiServerMCPClient")
def test_health_endpoint_unhealthy_when_mcp_server_fails(mock_mcp_client_cls):
    """Test health endpoint returns unhealthy when MCP servers fail."""
    mock_client = MagicMock()
    mock_client.get_tools = AsyncMock(side_effect=ConnectionError("refused"))
    mock_mcp_client_cls.return_value = mock_client

    # Create a test client with MCP settings that have a failing server
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
        os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_COLLECTION_NAME"] = "test"
        os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_DB_HOST"] = "localhost"
        os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_SYSTEM_PROMPT"] = "System prompt"
        os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_USER_PROMPT"] = "User prompt"

        # Write a temporary MCP settings file with a failing server
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"servers": [{"name": "failing-server", "command": "fail", "transport": "stdio"}]}, f)
            temp_path = f.name
        os.environ["MCP_SETTINGS_PATH"] = temp_path

        from assistant.main import app

        test_client = TestClient(app)

        response = test_client.get("/health")
        data = response.json()
        assert data["status"] == "unhealthy"
        assert "failed_servers" in data

        os.unlink(temp_path)
    finally:
        os.environ.clear()
        os.environ.update(old_env)


@patch("assistant.endpoints.health_endpoints.MultiServerMCPClient")
def test_readiness_endpoint_not_ready_when_mcp_server_returns_no_tools(mock_mcp_client_cls):
    """Test readiness endpoint returns not ready when MCP server returns no tools."""
    mock_client = MagicMock()
    mock_client.get_tools = AsyncMock(return_value=[])
    mock_mcp_client_cls.return_value = mock_client

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
        os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_COLLECTION_NAME"] = "test"
        os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_DB_HOST"] = "localhost"
        os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_SYSTEM_PROMPT"] = "System prompt"
        os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_USER_PROMPT"] = "User prompt"

        # Write a temporary MCP settings file with a server that returns no tools
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"servers": [{"name": "empty-server", "command": "echo", "transport": "stdio"}]}, f)
            temp_path = f.name
        os.environ["MCP_SETTINGS_PATH"] = temp_path

        from assistant.main import app

        test_client = TestClient(app)

        response = test_client.get("/readiness")
        data = response.json()
        assert data["status"] == "not ready"
        assert "failed_servers" in data

        os.unlink(temp_path)
    finally:
        os.environ.clear()
        os.environ.update(old_env)
