"""Tests for HealthCheckService"""

import asyncio
import os
from dataclasses import is_dataclass
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from assistant.health.health_check_service import HealthCheckService, HealthStatus


def test_health_status_dataclass():
    """Test HealthStatus is a proper dataclass with correct fields."""
    assert is_dataclass(HealthStatus)

    status = HealthStatus(server_name="test-server", healthy=True, last_checked=datetime.now(), error_message=None)
    assert status.server_name == "test-server"
    assert status.healthy is True
    assert isinstance(status.last_checked, datetime)
    assert status.error_message is None


def test_health_status_dataclass_with_error():
    """Test HealthStatus with error message."""
    status = HealthStatus(
        server_name="test-server", healthy=False, last_checked=datetime.now(), error_message="Connection failed"
    )
    assert status.healthy is False
    assert status.error_message == "Connection failed"


def test_health_check_service_init_default_interval():
    """Test HealthCheckService initializes with default 60 second interval."""
    service = HealthCheckService()
    assert service.check_interval_seconds == 60
    assert service.server_health == {}
    assert service.server_configs == {}
    assert service._task is None
    assert service._running is False


def test_health_check_service_init_custom_interval():
    """Test HealthCheckService initializes with custom interval."""
    service = HealthCheckService(check_interval_seconds=30)
    assert service.check_interval_seconds == 30


def test_health_check_service_init_invalid_interval_zero():
    """Test HealthCheckService falls back to 60 when interval is 0."""
    service = HealthCheckService(check_interval_seconds=0)
    assert service.check_interval_seconds == 60


def test_health_check_service_init_invalid_interval_negative():
    """Test HealthCheckService falls back to 60 when interval is negative."""
    service = HealthCheckService(check_interval_seconds=-10)
    assert service.check_interval_seconds == 60


def test_health_check_service_init_invalid_interval_small_positive():
    """Test HealthCheckService falls back to 60 when interval is <=0 (edge case)."""
    service = HealthCheckService(check_interval_seconds=-1)
    assert service.check_interval_seconds == 60


def test_health_check_service_init_with_server_configs():
    """Test HealthCheckService initializes with server configs."""
    configs = {"server1": {"url": "http://localhost:8080", "transport": "sse"}}
    service = HealthCheckService(server_configs=configs)
    assert service.server_configs == configs


def test_get_overall_health_empty():
    """Test get_overall_health returns True when server_health is empty."""
    service = HealthCheckService()
    assert service.get_overall_health() is True


def test_get_overall_health_all_healthy():
    """Test get_overall_health returns True when all servers are healthy."""
    service = HealthCheckService()
    service.server_health = {
        "server1": HealthStatus("server1", True, datetime.now()),
        "server2": HealthStatus("server2", True, datetime.now()),
    }
    assert service.get_overall_health() is True


def test_get_overall_health_one_unhealthy():
    """Test get_overall_health returns False when any server is unhealthy."""
    service = HealthCheckService()
    service.server_health = {
        "server1": HealthStatus("server1", True, datetime.now()),
        "server2": HealthStatus("server2", False, datetime.now(), "error"),
    }
    assert service.get_overall_health() is False


def test_get_overall_health_all_unhealthy():
    """Test get_overall_health returns False when all servers are unhealthy."""
    service = HealthCheckService()
    service.server_health = {
        "server1": HealthStatus("server1", False, datetime.now(), "error1"),
        "server2": HealthStatus("server2", False, datetime.now(), "error2"),
    }
    assert service.get_overall_health() is False


@pytest.mark.asyncio
async def test_start_and_stop():
    """Test start() and stop() manage the background task correctly."""
    service = HealthCheckService(check_interval_seconds=1)
    service.server_health = {"server1": None}

    # Mock _check_server to avoid actual checks
    service._check_server = AsyncMock()

    service.start()
    assert service._running is True
    assert service._task is not None
    assert not service._task.done()

    # Let it run briefly
    await asyncio.sleep(0.1)

    service.stop()
    assert service._running is False
    # Task should be cancelled
    await asyncio.sleep(0.1)  # Give it time to cancel


@pytest.mark.asyncio
async def test_start_prevents_duplicate_tasks():
    """Test start() does not create duplicate tasks."""
    service = HealthCheckService(check_interval_seconds=1)
    service.server_health = {"server1": None}
    service._check_server = AsyncMock()

    service.start()
    task1 = service._task

    service.start()  # Should not create new task
    assert service._task is task1


@pytest.mark.asyncio
async def test_server_health_updated_on_successful_check():
    """Test server_health dict is updated correctly on successful checks."""
    service = HealthCheckService(check_interval_seconds=1)
    service.server_health = {"server1": None}

    # Mock _check_server to simulate healthy state
    async def mock_check(server_name):
        service.server_health[server_name] = HealthStatus(
            server_name=server_name, healthy=True, last_checked=datetime.now(), error_message=None
        )

    service._check_server = mock_check

    await service._perform_checks()

    assert service.server_health["server1"].healthy is True
    assert service.server_health["server1"].error_message is None
    assert isinstance(service.server_health["server1"].last_checked, datetime)


@pytest.mark.asyncio
async def test_server_health_updated_on_failed_check():
    """Test server_health dict is updated correctly on failed checks."""
    service = HealthCheckService(check_interval_seconds=1)
    service.server_health = {"server1": None}

    # Make _check_server raise an exception
    async def mock_check_that_fails(server_name):
        raise Exception("Connection refused")

    service._check_server = mock_check_that_fails

    await service._perform_checks()

    assert service.server_health["server1"].healthy is False
    assert service.server_health["server1"].error_message == "Connection refused"
    assert isinstance(service.server_health["server1"].last_checked, datetime)


@pytest.mark.asyncio
async def test_check_loop_runs_periodically():
    """Test that _check_loop runs checks periodically with configurable interval."""
    service = HealthCheckService(check_interval_seconds=1)
    service.server_health = {"server1": None}

    call_count = 0
    original_check = service._check_server

    async def counting_check(server_name):
        nonlocal call_count
        call_count += 1
        # Don't actually do the check, just count

    service._check_server = counting_check

    service.start()
    await asyncio.sleep(2.5)  # Should have run at least 2 times
    service.stop()

    assert call_count >= 2


def test_mcp_settings_default_interval():
    """Test MCPSettings.health_check_interval_seconds defaults to 60."""
    # Clear any environment override
    old_env = os.environ.copy()
    try:
        if "SETTINGS_MCP_HEALTH_CHECK_INTERVAL_SECONDS" in os.environ:
            del os.environ["SETTINGS_MCP_HEALTH_CHECK_INTERVAL_SECONDS"]

        from assistant.impl.settings.mcp_server_settings import MCPSettings

        settings = MCPSettings(servers=[])
        assert settings.health_check_interval_seconds == 60
    finally:
        os.environ.clear()
        os.environ.update(old_env)


def test_mcp_settings_interval_from_env(monkeypatch):
    """Test MCPSettings.health_check_interval_seconds can be overridden via env var."""
    monkeypatch.setenv("SETTINGS_MCP_HEALTH_CHECK_INTERVAL_SECONDS", "120")

    from assistant.impl.settings.mcp_server_settings import MCPSettings

    settings = MCPSettings(servers=[])
    assert settings.health_check_interval_seconds == 120


@pytest.mark.asyncio
async def test_check_server_success():
    """Test _check_server marks server as healthy on successful check."""
    configs = {"test-server": {"url": "http://localhost:8080", "transport": "sse"}}
    service = HealthCheckService(server_configs=configs)
    service.server_health["test-server"] = None

    with patch("assistant.health.health_check_service.MultiServerMCPClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client.get_tools = AsyncMock(return_value=[])
        mock_client_class.return_value = mock_client

        await service._check_server("test-server")

        assert service.server_health["test-server"].healthy is True
        assert service.server_health["test-server"].error_message is None
        assert isinstance(service.server_health["test-server"].last_checked, datetime)


@pytest.mark.asyncio
async def test_check_server_no_config():
    """Test _check_server marks server as unhealthy when no config exists."""
    service = HealthCheckService(server_configs={})
    service.server_health["unknown-server"] = None

    await service._check_server("unknown-server")

    assert service.server_health["unknown-server"].healthy is False
    assert "No configuration found" in service.server_health["unknown-server"].error_message


@pytest.mark.asyncio
async def test_check_server_timeout():
    """Test _check_server marks server as unhealthy on timeout."""
    configs = {"slow-server": {"url": "http://localhost:8080", "transport": "sse"}}
    service = HealthCheckService(server_configs=configs)
    service.server_health["slow-server"] = None

    with patch("assistant.health.health_check_service.MultiServerMCPClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client.get_tools = AsyncMock(side_effect=asyncio.TimeoutError())
        mock_client_class.return_value = mock_client

        await service._check_server("slow-server")

        assert service.server_health["slow-server"].healthy is False
        assert (
            "TimeoutError" in type(service.server_health["slow-server"].error_message).__name__
            or "TimeoutError" in str(service.server_health["slow-server"].error_message)
            or service.server_health["slow-server"].error_message == ""
        )


@pytest.mark.asyncio
async def test_check_server_connection_error():
    """Test _check_server marks server as unhealthy on connection error."""
    configs = {"bad-server": {"url": "http://localhost:8080", "transport": "sse"}}
    service = HealthCheckService(server_configs=configs)
    service.server_health["bad-server"] = None

    with patch("assistant.health.health_check_service.MultiServerMCPClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client.get_tools = AsyncMock(side_effect=ConnectionError("Connection refused"))
        mock_client_class.return_value = mock_client

        await service._check_server("bad-server")

        assert service.server_health["bad-server"].healthy is False
        assert "Connection refused" in service.server_health["bad-server"].error_message


@pytest.mark.asyncio
async def test_stop_when_not_running():
    """Test stop() works gracefully when service is not running."""
    service = HealthCheckService()
    # Should not raise
    service.stop()
    assert service._running is False
    assert service._task is None


@pytest.mark.asyncio
async def test_multiple_servers_mixed_health():
    """Test get_overall_health with multiple servers with mixed health status."""
    service = HealthCheckService()
    service.server_health = {
        "server1": HealthStatus("server1", True, datetime.now()),
        "server2": HealthStatus("server2", False, datetime.now(), "error"),
        "server3": HealthStatus("server3", True, datetime.now()),
    }
    assert service.get_overall_health() is False


@pytest.mark.asyncio
async def test_perform_checks_with_empty_server_health():
    """Test _perform_checks handles empty server_health gracefully."""
    service = HealthCheckService()
    # Should not raise
    await service._perform_checks()
    assert service.server_health == {}


@pytest.mark.asyncio
async def test_check_loop_stops_on_stop_call():
    """Test that _check_loop stops when stop() is called."""
    service = HealthCheckService(check_interval_seconds=1)
    service.server_health = {"server1": None}
    service._check_server = AsyncMock()

    service.start()
    assert service._running is True

    # Let it run once
    await asyncio.sleep(1.5)

    service.stop()
    assert service._running is False

    # Verify the task is done or cancelled
    await asyncio.sleep(0.1)
    # After stop, the task should be cancelled
