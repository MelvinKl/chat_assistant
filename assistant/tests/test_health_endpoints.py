"""Tests for health check endpoints"""

import os
import threading
from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest
from fastapi.testclient import TestClient

from assistant.endpoints import health_endpoints
from assistant.endpoints.health_endpoints import Status, health_check
from assistant.impl.settings.mcp_server_settings import MCPServer, MCPSettings


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


@pytest.fixture
def isolated_health_check():
    """Isolate the health check module state around one test.

    The health check keeps its status and its background thread in module
    globals; the fixture snapshots them, resets the status to healthy and
    the thread to None before the test, and restores the snapshot in
    teardown, joining a still-running thread first. ``time.sleep`` is
    patched in the health endpoints module so that a check round ends
    through the patched call instead of sleeping for five minutes: the
    patched call raises SystemExit, which ends a probe thread; the
    thread excepthook is silenced for the test so the killed threads
    raise no unhandled thread exception. The test receives the sleep
    mock and picks the round behaviour it needs.
    """
    snapshot = (health_endpoints.status, health_endpoints.health_thread)

    def silent_excepthook(*args):
        """Swallow thread exceptions: the killed probe threads are expected."""

    old_excepthook = threading.excepthook
    threading.excepthook = silent_excepthook
    health_endpoints.status = Status.HEALTHY
    health_endpoints.health_thread = None
    sleep_mock = MagicMock(name="time.sleep")
    sleep_mock.side_effect = SystemExit()
    with patch("assistant.endpoints.health_endpoints.time.sleep", sleep_mock):
        yield sleep_mock
    thread = health_endpoints.health_thread
    if thread is not None and thread.is_alive():
        thread.join(timeout=5)
    health_endpoints.status, health_endpoints.health_thread = snapshot
    threading.excepthook = old_excepthook


def test_health_endpoint(client):
    """Implements "the health endpoint reports the application status and version"
    (requirements/health-api.feature)
    Implements "without configured MCP servers the health status stays healthy"
    (requirements/health-api.feature)

    The fixture points MCP_SETTINGS_PATH at a non-existent file, so the
    application runs without configured MCP servers and the health check
    keeps the status healthy.
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_readiness_endpoint(client):
    """Implements "the readiness endpoint reports the application as ready"
    (requirements/health-api.feature)

    The readiness endpoint answers 200 with the application ready.
    """
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


class TestHealthCheck:
    """The background MCP probe thread of the health endpoints."""

    def test_thread_starts_on_first_health_request(self, client, isolated_health_check):
        """Implements "the health check thread starts on the first health request"
        (requirements/health-api.feature)

        When the health endpoint is called for the first time, a background
        health check thread is started.
        """
        assert health_endpoints.health_thread is None

        response = client.get("/health")

        assert response.status_code == 200
        thread = health_endpoints.health_thread
        assert isinstance(thread, threading.Thread)
        assert thread.ident is not None

    def test_probes_every_configured_mcp_server(self, isolated_health_check):
        """Implements "the health check probes every configured MCP server"
        (requirements/health-api.feature)

        When the background health check runs, every configured MCP server
        is probed for tool loading: a stdio server is probed with its
        command and args, a remote server is probed with its url, its
        transport and its headers, and the loaded tools land in the tool
        group under the server's agent key. The connections' sampling
        session kwargs (carried for the mcp-sampling scenario)
        are out of scope for this scenario and are dropped before the
        probe dicts are compared.
        """
        stdio_tool = MagicMock()
        remote_tool = MagicMock()

        def client_side_effect(server_dict):
            mock_client = MagicMock()
            if "probe-stdio" in server_dict:
                mock_client.get_tools = AsyncMock(return_value=[stdio_tool])
            else:
                mock_client.get_tools = AsyncMock(return_value=[remote_tool])
            return mock_client

        settings = MCPSettings(
            servers=[
                MCPServer(name="probe-stdio", command="probe-command", args=["probe"], transport="stdio"),
                MCPServer(
                    name="probe-remote",
                    url="http://localhost:9999/sse",
                    transport="sse",
                    headers={"Authorization": "Bearer token"},
                ),
            ]
        )

        tools = {}
        with (
            patch(
                "assistant.endpoints.health_endpoints.MultiServerMCPClient",
                side_effect=client_side_effect,
            ) as mock_client_cls,
            pytest.raises(SystemExit),
        ):
            health_check(mcp_settings=settings, tools=tools)

        assert mock_client_cls.call_count == 2
        stdio_dict, remote_dict = [call.args[0] for call in mock_client_cls.call_args_list]
        for connection in list(stdio_dict.values()) + list(remote_dict.values()):
            connection.pop("session_kwargs", None)
        assert stdio_dict == {
            "probe-stdio": {"command": "probe-command", "args": ["probe"], "transport": "stdio"},
        }
        assert remote_dict == {
            "probe-remote": {
                "url": "http://localhost:9999/sse",
                "transport": "sse",
                "headers": {"Authorization": "Bearer token"},
            },
        }
        assert tools == {None: [stdio_tool, remote_tool]}

    def test_check_repeats_on_five_minute_interval(self, isolated_health_check):
        """Implements "the health check repeats on a five minute interval"
        (requirements/health-api.feature)

        When one round of checks finishes, the check waits 300 seconds
        before the next round; only the second wait is patched to stop the
        loop, so the recorded waits show the repeated 300 s interval.
        """
        isolated_health_check.side_effect = [None, SystemExit()]

        def client_side_effect(server_dict):
            mock_client = MagicMock()
            mock_client.get_tools = AsyncMock(return_value=[])
            return mock_client

        settings = MCPSettings(servers=[MCPServer(name="probe-stdio", command="probe-command", transport="stdio")])

        with (
            patch(
                "assistant.endpoints.health_endpoints.MultiServerMCPClient",
                side_effect=client_side_effect,
            ) as mock_client_cls,
            pytest.raises(SystemExit),
        ):
            health_check(mcp_settings=settings, tools={})

        assert mock_client_cls.call_count >= 2
        assert len(isolated_health_check.call_args_list) >= 2
        for recorded_call in isolated_health_check.call_args_list:
            assert recorded_call == call(300)

    def test_failing_server_turns_health_unhealthy(self, client, isolated_health_check):
        """Implements "a failing MCP server turns the health status unhealthy"
        (requirements/health-api.feature)

        When the background health check runs and one configured MCP server
        fails to load its tools, the health status is "unhealthy".
        """

        def client_side_effect(server_dict):
            mock_client = MagicMock()
            mock_client.get_tools = AsyncMock(side_effect=ConnectionError("connection refused"))
            return mock_client

        settings = MCPSettings(servers=[MCPServer(name="failing-server", command="fail", transport="stdio")])

        with (
            patch("assistant.endpoints.health_endpoints.MultiServerMCPClient", side_effect=client_side_effect),
            pytest.raises(SystemExit),
        ):
            health_check(mcp_settings=settings, tools={})

        assert health_endpoints.status == Status.UNHEALTHY
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "unhealthy"

    def test_reachable_servers_keep_health_healthy(self, client, isolated_health_check):
        """Implements "all reachable MCP servers keep the health status healthy"
        (requirements/health-api.feature)

        When the background health check runs and every configured MCP
        server loads its tools, the health status is "healthy".
        """
        first_tool = MagicMock()
        second_tool = MagicMock()

        def client_side_effect(server_dict):
            mock_client = MagicMock()
            if "reachable-stdio" in server_dict:
                mock_client.get_tools = AsyncMock(return_value=[first_tool])
            else:
                mock_client.get_tools = AsyncMock(return_value=[second_tool])
            return mock_client

        settings = MCPSettings(
            servers=[
                MCPServer(name="reachable-stdio", command="probe-command", transport="stdio"),
                MCPServer(name="reachable-remote", url="http://localhost:9999/sse", transport="sse"),
            ]
        )

        with (
            patch("assistant.endpoints.health_endpoints.MultiServerMCPClient", side_effect=client_side_effect),
            pytest.raises(SystemExit),
        ):
            health_check(mcp_settings=settings, tools={})

        assert health_endpoints.status == Status.HEALTHY
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
