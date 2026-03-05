import os
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

os.environ["SETTINGS_OPENAI_API_KEY"] = "test_key"
os.environ["SETTINGS_OPENAI_EMBEDDER"] = "text-embedding-ada-002"
os.environ["SETTINGS_OPENAI_MODEL"] = "gpt-3.5-turbo"
os.environ["SETTINGS_OPENAI_BASE_URL"] = "http://test"
os.environ["SETTINGS_PROMPTS_REPHRASE_QUESTION_SYSTEM_PROMPT"] = "test"
os.environ["SETTINGS_PROMPTS_REPHRASE_QUESTION_USER_PROMPT"] = "test"
os.environ["SETTINGS_PROMPTS_REPHRASE_ANSWER_SYSTEM_PROMPT"] = "test"
os.environ["SETTINGS_PROMPTS_REPHRASE_ANSWER_USER_PROMPT"] = "test"
os.environ["SETTINGS_ADDITIONAL_INFORMATION"] = "test"
os.environ["SETTINGS_COMPONENTS_APIS"] = '["http://test"]'
os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_ENABLED"] = "false"
os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_COLLECTION_NAME"] = "test_col"
os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_DB_HOST"] = "test_host"
os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_SYSTEM_PROMPT"] = "test"
os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_USER_PROMPT"] = "test"

from assistant.main import app as application


@pytest.fixture
def app() -> FastAPI:
    application.dependency_overrides = {}

    return application


@pytest.fixture
def client(app) -> TestClient:
    return TestClient(app)
