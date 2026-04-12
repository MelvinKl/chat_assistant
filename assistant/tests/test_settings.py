"""Unit tests for settings modules"""

import json
import os
import tempfile

import pytest

from assistant.impl.settings.mcp_server_settings import (
    MCPServer,
    MCPSettings,
    load_mcp_settings_from_json,
)


def test_load_mcp_settings_from_valid_json():
    """Test loading MCP settings from valid JSON file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(
            {
                "servers": [
                    {
                        "name": "weather",
                        "url": "http://weather:8080/sse",
                        "transport": "sse",
                    }
                ]
            },
            f,
        )
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
    """Test loading MCP settings from missing file returns empty list."""
    settings = load_mcp_settings_from_json("/nonexistent/path/settings.json")
    assert len(settings.servers) == 0


def test_load_mcp_settings_invalid_json():
    """Test loading invalid JSON raises ValueError."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("{invalid json")
        temp_path = f.name

    try:
        with pytest.raises(ValueError, match="MCP settings file contains invalid JSON"):
            load_mcp_settings_from_json(temp_path)
    finally:
        os.unlink(temp_path)


def test_load_mcp_settings_respects_env_variable():
    """Test that environment variable overrides default path."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(
            {"servers": [{"name": "test", "url": "http://test", "transport": "sse"}]},
            f,
        )
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
    """Test MCPServer model validation."""
    server = MCPServer(name="test", transport="sse", url="http://test:8080")
    assert server.name == "test"
    assert server.transport == "sse"
    assert server.command is None  # Default is None, not empty string
    assert server.args == []


def test_mcp_settings_model_validation():
    """Test MCPSettings model validation."""
    settings = MCPSettings(
        servers=[MCPServer(name="test", transport="sse", url="http://test")],
    )
    assert len(settings.servers) == 1
    assert settings.strict is False  # Default value


def test_mcp_settings_model_validation_with_strict():
    """Test MCPSettings model validation with strict field."""
    settings = MCPSettings(
        servers=[MCPServer(name="test", transport="sse", url="http://test")],
        strict=True,
    )
    assert len(settings.servers) == 1
    assert settings.strict is True


def test_load_mcp_settings_with_strict_field():
    """Test loading MCP settings with strict field from JSON."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(
            {
                "servers": [
                    {
                        "name": "weather",
                        "url": "http://weather:8080/sse",
                        "transport": "sse",
                    }
                ],
                "strict": True,
            },
            f,
        )
        temp_path = f.name

    try:
        settings = load_mcp_settings_from_json(temp_path)
        assert len(settings.servers) == 1
        assert settings.servers[0].name == "weather"
        assert settings.strict is True
    finally:
        os.unlink(temp_path)


def test_load_mcp_settings_strict_field_default_false():
    """Test that strict field defaults to False when not provided."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(
            {
                "servers": [
                    {
                        "name": "weather",
                        "url": "http://weather:8080/sse",
                        "transport": "sse",
                    }
                ]
            },
            f,
        )
        temp_path = f.name

    try:
        settings = load_mcp_settings_from_json(temp_path)
        assert len(settings.servers) == 1
        assert settings.servers[0].name == "weather"
        assert settings.strict is False  # Default value
    finally:
        os.unlink(temp_path)
