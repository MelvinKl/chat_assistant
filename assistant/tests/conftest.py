import os

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

os.environ["SETTINGS_OPENAI_API_KEY"] = "fake-key"
os.environ["SETTINGS_OPENAI_EMBEDDER"] = "fake-embedder"
os.environ["SETTINGS_OPENAI_MODEL"] = "fake-model"
os.environ["SETTINGS_OPENAI_BASE_URL"] = "http://fake-url"

os.environ["SETTINGS_PROMPTS_REPHRASE_QUESTION_SYSTEM_PROMPT"] = "fake-rephrase-question-system-prompt"
os.environ["SETTINGS_PROMPTS_REPHRASE_QUESTION_USER_PROMPT"] = "fake-rephrase-question-user-prompt"
os.environ["SETTINGS_PROMPTS_REPHRASE_ANSWER_SYSTEM_PROMPT"] = "fake-rephrase-answer-system-prompt"
os.environ["SETTINGS_PROMPTS_REPHRASE_ANSWER_USER_PROMPT"] = "fake-rephrase-answer-user-prompt"
os.environ["SETTINGS_ADDITIONAL_INFORMATION"] = "fake-information"
os.environ["SETTINGS_COMPONENTS_APIS"] = '["http://fake-api"]'
os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_ENABLED"] = "false"
os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_COLLECTION_NAME"] = "fake-collection"
os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_DB_HOST"] = "fake-host"
os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_SYSTEM_PROMPT"] = "fake-dynamic-system-prompt"
os.environ["SETTINGS_DYNAMIC_KNOWLEDGE_USER_PROMPT"] = "fake-dynamic-user-prompt"

from assistant.main import app as application


@pytest.fixture
def app() -> FastAPI:
    application.dependency_overrides = {}

    return application


@pytest.fixture
def client(app) -> TestClient:
    return TestClient(app)
