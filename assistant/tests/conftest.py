import os

os.environ["SETTINGS_API_NAME"] = "dummy"
os.environ["SETTINGS_API_DESCRIPTION"] = "dummy"
os.environ["SETTINGS_COMPONENTS_APIS"] = '[]'
os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_ENABLED"] = "false"
os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_COLLECTION_NAME"] = "dummy"
os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_DB_HOST"] = "dummy"
os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_SYSTEM_PROMPT"] = "dummy"
os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_USER_PROMPT"] = "dummy"
os.environ["SETTINGS_ADDITIONAL_INFORMATION"] = "dummy"
os.environ["SETTINGS_OPENAI_API_KEY"] = "dummy"
os.environ["SETTINGS_OPENAI_EMBEDDER"] = "dummy"
os.environ["SETTINGS_OPENAI_MODEL"] = "dummy"
os.environ["SETTINGS_OPENAI_BASE_URL"] = "http://dummy"
os.environ["SETTINGS_PROMPTS_REPHRASE_QUESTION_SYSTEM_PROMPT"] = "dummy"
os.environ["SETTINGS_PROMPTS_REPHRASE_QUESTION_USER_PROMPT"] = "dummy"
os.environ["SETTINGS_PROMPTS_REPHRASE_ANSWER_SYSTEM_PROMPT"] = "dummy"
os.environ["SETTINGS_PROMPTS_REPHRASE_ANSWER_USER_PROMPT"] = "dummy"

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from assistant.main import app as application


@pytest.fixture
def app() -> FastAPI:
    application.dependency_overrides = {}

    return application


@pytest.fixture
def client(app) -> TestClient:
    return TestClient(app)
