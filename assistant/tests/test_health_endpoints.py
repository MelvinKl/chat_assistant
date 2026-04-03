"""Tests for health check endpoints"""

import os

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
