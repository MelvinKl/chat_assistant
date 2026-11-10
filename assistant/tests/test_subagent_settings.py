"""Unit tests for the subagent settings module"""

import json
import os
import tempfile

import pytest

from assistant.impl.settings.subagent_settings import (
    Subagent,
    load_subagent_settings_from_json,
)


def test_load_subagent_settings_from_valid_json():
    """Implements "the subagent settings are loaded from the subagents config file"
    (requirements/subagents.feature)

    Given a json file with subagent definitions at the subagents config path,
    loading the subagent settings yields the settings with one subagent per
    definition.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(
            {
                "subagents": [
                    {"name": "weather", "description": "the weather subagent", "system_prompt": "the weather prompt"},
                    {"name": "coder", "description": "the coder subagent", "system_prompt": "the coder prompt"},
                ]
            },
            f,
        )
        temp_path = f.name

    try:
        settings = load_subagent_settings_from_json(temp_path)
        assert [subagent.name for subagent in settings.subagents] == ["weather", "coder"]
        assert settings.subagents[0].description == "the weather subagent"
        assert settings.subagents[0].system_prompt == "the weather prompt"
        assert settings.subagents[1].description == "the coder subagent"
        assert settings.subagents[1].system_prompt == "the coder prompt"
    finally:
        os.unlink(temp_path)


def test_load_subagent_settings_respects_env_variable():
    """Implements "the subagents config path can be overridden by an environment variable"
    (requirements/subagents.feature)

    When the SUBAGENT_SETTINGS_PATH environment variable points at an
    alternate file, the subagent settings are read from the file named by
    the environment variable, not from the path that would be the default.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(
            {
                "subagents": [
                    {"name": "test", "description": "the alternate subagent", "system_prompt": "the alt prompt"}
                ]
            },
            f,
        )
        temp_path = f.name

    try:
        os.environ["SUBAGENT_SETTINGS_PATH"] = temp_path
        settings = load_subagent_settings_from_json("/default/path")  # default path ignored
        assert [subagent.name for subagent in settings.subagents] == ["test"]
    finally:
        del os.environ["SUBAGENT_SETTINGS_PATH"]
        os.unlink(temp_path)


def test_subagent_model_validation():
    """Implements "a subagent definition consists of name, description and system prompt"
    (requirements/subagents.feature)

    A subagent definition consists of a name, a description and a system
    prompt: the subagent model carries exactly those fields, and a validated
    subagent carries the name, the description and the system prompt of its
    definition.
    """
    subagent = Subagent(
        name="weather",
        description="the weather subagent description",
        system_prompt="the weather subagent system prompt",
    )
    assert subagent.name == "weather"
    assert subagent.description == "the weather subagent description"
    assert subagent.system_prompt == "the weather subagent system prompt"
    assert set(Subagent.model_fields) == {"name", "description", "system_prompt"}


def test_load_subagent_settings_missing_file():
    """Implements "a missing config file yields no subagents"
    (requirements/subagents.feature)

    Loading the subagent settings from a subagents config path that does
    not exist yields the settings with no subagents.
    """
    settings = load_subagent_settings_from_json("/nonexistent/path/subagents.json")
    assert len(settings.subagents) == 0


def test_load_subagent_settings_invalid_json():
    """Implements "an invalid json config file raises a value error"
    (requirements/subagents.feature)

    Loading the subagent settings from a config file containing invalid
    json raises a value error.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("{invalid json")
        temp_path = f.name

    try:
        with pytest.raises(ValueError, match="invalid JSON"):
            load_subagent_settings_from_json(temp_path)
    finally:
        os.unlink(temp_path)
