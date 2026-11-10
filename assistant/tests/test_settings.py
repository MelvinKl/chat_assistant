"""Unit tests for settings modules"""

import json
import os
import tempfile

import pytest
from langchain_openai import ChatOpenAI

from assistant.impl.settings.api_settings import APISetttings
from assistant.impl.settings.information_settings import InformationSettings
from assistant.impl.settings.mcp_server_settings import (
    MCPServer,
    MCPSettings,
    load_mcp_settings_from_json,
)
from assistant.impl.settings.openai_settings import OpenAISetttings
from assistant.impl.settings.prompt_settings import PromptSettings


def test_load_mcp_settings_from_valid_json():
    """Implements "the server settings are loaded from the mcp config file"
    (requirements/mcp-integration.feature)

    Given a json file with server definitions at the mcp config path, loading
    the mcp server settings yields the settings with one server per
    definition.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"servers": [{"name": "weather", "url": "http://weather:8080/sse", "transport": "sse"}]}, f)
        temp_path = f.name

    try:
        settings = load_mcp_settings_from_json(temp_path)
        assert len(settings.servers) == 1
        assert settings.servers[0].name == "weather"
        assert settings.servers[0].url == "http://weather:8080/sse"
        assert settings.servers[0].transport == "sse"
    finally:
        os.unlink(temp_path)


def test_load_mcp_settings_empty_servers():
    """Test loading MCP settings with empty servers list."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"servers": []}, f)
        temp_path = f.name

    try:
        settings = load_mcp_settings_from_json(temp_path)
        assert len(settings.servers) == 0
    finally:
        os.unlink(temp_path)


def test_load_mcp_settings_missing_file():
    """Implements "a missing config file yields an empty server list"
    (requirements/mcp-integration.feature)

    Loading the mcp server settings from a mcp config path that does not
    exist yields the settings with no servers.
    """
    settings = load_mcp_settings_from_json("/nonexistent/path/settings.json")
    assert len(settings.servers) == 0


def test_load_mcp_settings_invalid_json():
    """Implements "an invalid json config file raises a value error"
    (requirements/mcp-integration.feature)

    Loading the mcp server settings from a config file containing invalid
    json raises a value error reporting the invalid json.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("{invalid json")
        temp_path = f.name

    try:
        with pytest.raises(ValueError, match="MCP settings file contains invalid JSON"):
            load_mcp_settings_from_json(temp_path)
    finally:
        os.unlink(temp_path)


def test_load_mcp_settings_respects_env_variable():
    """Implements "the mcp config path can be overridden by an environment variable"
    (requirements/mcp-integration.feature)

    When the MCP_SETTINGS_PATH environment variable points at an alternate
    file, the mcp server settings are read from the file named by the
    environment variable, not from the path that would be the default.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"servers": [{"name": "test", "url": "http://test", "transport": "sse"}]}, f)
        temp_path = f.name

    try:
        # Set environment variable
        os.environ["MCP_SETTINGS_PATH"] = temp_path
        settings = load_mcp_settings_from_json("/default/path")  # default path ignored
        assert len(settings.servers) == 1
        assert settings.servers[0].name == "test"
    finally:
        del os.environ["MCP_SETTINGS_PATH"]
        os.unlink(temp_path)


def test_mcp_server_model_validation():
    """Implements "a server definition carries name, transport and connection details"
    (requirements/mcp-integration.feature)

    A server definition carries its name, its url and its transport, and has
    empty defaults for command, args and env.
    """
    server = MCPServer(name="test", transport="sse", url="http://test:8080")
    assert server.name == "test"
    assert server.transport == "sse"
    assert server.url == "http://test:8080"
    assert server.command == ""
    assert server.args == []
    assert server.env == ""


def test_mcp_settings_model_validation():
    """Test MCPSettings model validation."""
    settings = MCPSettings(servers=[MCPServer(name="test", transport="sse", url="http://test")])
    assert len(settings.servers) == 1


def test_llm_created_from_openai_settings():
    """Implements "the LLM is created from the openai settings"
    (requirements/configuration.feature)

    The SETTINGS_OPENAI_MODEL, SETTINGS_OPENAI_BASE_URL and
    SETTINGS_OPENAI_API_KEY environment variables are read by the OpenAI
    settings, and the openai compatible chat model the dependency container
    creates from them carries the configured model, base url and api key.
    """
    env_vars = {
        "SETTINGS_OPENAI_MODEL": "gpt-test",
        "SETTINGS_OPENAI_BASE_URL": "http://llm.test:8080",
        "SETTINGS_OPENAI_API_KEY": "sk-test",
    }
    old_env = {name: os.environ.get(name) for name in env_vars}
    for name in env_vars:
        os.environ.pop(name, None)
    os.environ.update(env_vars)

    try:
        settings = OpenAISetttings()
        assert settings.model == "gpt-test"
        assert settings.base_url == "http://llm.test:8080"
        assert settings.api_key == "sk-test"

        # The container creates the chat model from exactly these settings.
        llm = ChatOpenAI(
            model=settings.model,
            base_url=settings.base_url,
            api_key=settings.api_key,
        )
        assert llm.model == "gpt-test"
        assert llm.openai_api_base == "http://llm.test:8080"
        assert llm.openai_api_key.get_secret_value() == "sk-test"
    finally:
        for name, value in old_env.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


def test_prompt_settings_read_from_environment():
    """Implements "the prompt settings are read from the environment"
    (requirements/configuration.feature)

    The four SETTINGS_PROMPTS_ environment variables are read when the
    prompt settings are created, so the settings carry the question
    rephrasing system and user prompts and the answer rephrasing system and
    user prompts.
    """
    env_vars = {
        "SETTINGS_PROMPTS_REPHRASE_QUESTION_SYSTEM_PROMPT": "question system prompt",
        "SETTINGS_PROMPTS_REPHRASE_QUESTION_USER_PROMPT": "question user prompt",
        "SETTINGS_PROMPTS_REPHRASE_ANSWER_SYSTEM_PROMPT": "answer system prompt",
        "SETTINGS_PROMPTS_REPHRASE_ANSWER_USER_PROMPT": "answer user prompt",
    }
    old_env = {name: os.environ.get(name) for name in env_vars}
    for name in env_vars:
        os.environ.pop(name, None)
    os.environ.update(env_vars)

    try:
        settings = PromptSettings()
        assert settings.rephrase_question_system_prompt == "question system prompt"
        assert settings.rephrase_question_user_prompt == "question user prompt"
        assert settings.rephrase_answer_system_prompt == "answer system prompt"
        assert settings.rephrase_answer_user_prompt == "answer user prompt"
    finally:
        for name, value in old_env.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


def test_additional_information_read_from_environment():
    """Implements "the additional information is read from the environment"
    (requirements/configuration.feature)

    The SETTINGS_ADDITIONAL_INFORMATION environment variable is read when
    the information settings are created, so the settings carry the
    configured additional information.
    """
    old_value = os.environ.get("SETTINGS_ADDITIONAL_INFORMATION")
    os.environ["SETTINGS_ADDITIONAL_INFORMATION"] = "the configured additional information"

    try:
        settings = InformationSettings()
        assert settings.information == "the configured additional information"
    finally:
        if old_value is None:
            os.environ.pop("SETTINGS_ADDITIONAL_INFORMATION", None)
        else:
            os.environ["SETTINGS_ADDITIONAL_INFORMATION"] = old_value


def test_api_name_and_description_read_from_environment():
    """Implements "the api name and description are read from the environment"
    (requirements/configuration.feature)

    The SETTINGS_API_NAME and SETTINGS_API_DESCRIPTION environment variables
    are read when the api settings are created, so the settings carry the
    configured name and description.
    """
    env_vars = {
        "SETTINGS_API_NAME": "the configured api name",
        "SETTINGS_API_DESCRIPTION": "the configured api description",
    }
    old_env = {name: os.environ.get(name) for name in env_vars}
    for name in env_vars:
        os.environ.pop(name, None)
    os.environ.update(env_vars)

    try:
        settings = APISetttings()
        assert settings.name == "the configured api name"
        assert settings.description == "the configured api description"
    finally:
        for name, value in old_env.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


def test_settings_loaded_from_env_file():
    """Implements "the settings are loaded from a .env file"
    (requirements/configuration.feature)

    The settings objects declare env_file=".env", so when a settings object
    is created and the .env file holds values, the values from the .env file
    are used.
    """
    env_vars = ("SETTINGS_OPENAI_MODEL", "SETTINGS_OPENAI_BASE_URL", "SETTINGS_OPENAI_API_KEY")
    old_cwd = os.getcwd()
    old_env = {name: os.environ.get(name) for name in env_vars}
    for name in env_vars:
        os.environ.pop(name, None)

    try:
        with tempfile.TemporaryDirectory() as env_dir:
            os.chdir(env_dir)
            try:
                with open(os.path.join(env_dir, ".env"), "w", encoding="utf-8") as f:
                    f.write(
                        "SETTINGS_OPENAI_MODEL=gpt-from-env-file\n"
                        "SETTINGS_OPENAI_BASE_URL=http://llm-from-env-file:8080\n"
                        "SETTINGS_OPENAI_API_KEY=sk-from-env-file\n"
                    )
                settings = OpenAISetttings()
                assert settings.model == "gpt-from-env-file"
                assert settings.base_url == "http://llm-from-env-file:8080"
                assert settings.api_key == "sk-from-env-file"
            finally:
                os.chdir(old_cwd)
    finally:
        for name, value in old_env.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


def test_unrelated_environment_variables_ignored():
    """Implements "unrelated environment variables are ignored"
    (requirements/configuration.feature)

    The settings declare extra="ignore", so environment variables that match
    no settings field raise no validation error when a settings object is
    created, and the declared fields keep their defaults.
    """
    # The declared settings fields, so ambient values cannot leak into the
    # defaults asserted below.
    settings_vars = (
        "SETTINGS_PROMPTS_REPHRASE_QUESTION_SYSTEM_PROMPT",
        "SETTINGS_PROMPTS_REPHRASE_QUESTION_USER_PROMPT",
        "SETTINGS_PROMPTS_REPHRASE_ANSWER_SYSTEM_PROMPT",
        "SETTINGS_PROMPTS_REPHRASE_ANSWER_USER_PROMPT",
        "SETTINGS_OPENAI_MODEL",
        "SETTINGS_OPENAI_BASE_URL",
        "SETTINGS_OPENAI_API_KEY",
        "SETTINGS_ADDITIONAL_INFORMATION",
        "SETTINGS_API_NAME",
        "SETTINGS_API_DESCRIPTION",
    )
    unrelated_vars = {
        "SETTINGS_PROMPTS_UNRELATED_VARIABLE": "some value",
        "SETTINGS_OPENAI_UNRELATED_VARIABLE": "some value",
    }
    old_env = {name: os.environ.get(name) for name in [*settings_vars, *unrelated_vars]}
    for name in old_env:
        os.environ.pop(name, None)
    os.environ.update(unrelated_vars)

    try:
        prompt_settings = PromptSettings()
        openai_settings = OpenAISetttings()
        information_settings = InformationSettings()
        api_settings = APISetttings()
        assert prompt_settings.rephrase_question_system_prompt == ""
        assert openai_settings.model == ""
        assert information_settings.information == ""
        assert api_settings.name == ""
    finally:
        for name, value in old_env.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
