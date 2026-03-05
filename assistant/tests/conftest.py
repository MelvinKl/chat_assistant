import os
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest import mock

os.environ["SETTINGS_OPENAI_API_KEY"] = "test"
os.environ["SETTINGS_OPENAI_EMBEDDER"] = "test"
os.environ["SETTINGS_OPENAI_MODEL"] = "test"
os.environ["SETTINGS_OPENAI_BASE_URL"] = "http://test"
os.environ["SETTINGS_PROMPTS_REPHRASE_QUESTION_SYSTEM_PROMPT"] = "test"
os.environ["SETTINGS_PROMPTS_REPHRASE_QUESTION_USER_PROMPT"] = "test"
os.environ["SETTINGS_PROMPTS_REPHRASE_ANSWER_SYSTEM_PROMPT"] = "test"
os.environ["SETTINGS_PROMPTS_REPHRASE_ANSWER_USER_PROMPT"] = "test"
os.environ["SETTINGS_ADDITIONAL_INFORMATION"] = "test"
os.environ["SETTINGS_COMPONENTS_APIS"] = "[]"
os.environ["SETTINGS_MCP_SERVERS"] = "[]"
os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_ENABLED"] = "false"
os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_COLLECTION_NAME"] = "test"
os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_DB_HOST"] = "test"
os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_SYSTEM_PROMPT"] = "test"
os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_USER_PROMPT"] = "test"
os.environ["SETTINGS_API_NAME"] = "test"
os.environ["SETTINGS_API_DESCRIPTION"] = "test"

# Mock mcp settings loading before importing application
from assistant.impl.settings.mcp_server_settings import MCPSettings
mcp_mock = mock.patch(
    "assistant.assistant_container.load_mcp_settings_from_json", 
    return_value=MCPSettings(servers=[])
)
mcp_mock.start()

from assistant.main import app as application


@pytest.fixture
def app() -> FastAPI:
    application.dependency_overrides = {}

    return application


@pytest.fixture
def client(app) -> TestClient:
    return TestClient(app)
