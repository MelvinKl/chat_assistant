# test_mcp_client_setup.py
"""Tests that _get_mcp_tools registers the sampling callback with all MCP server connections."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from assistant.assistant_container import _get_mcp_tools
from assistant.impl.settings.mcp_server_settings import MCPServer, MCPSettings
from tests.fake_chat_model import FakeChatModel


@patch("assistant.assistant_container.MultiServerMCPClient")
def test_stdio_server_gets_tools(mock_mcp_client_cls):
    mock_client = MagicMock()
    mock_client.get_tools = AsyncMock(return_value=[])
    mock_mcp_client_cls.return_value = mock_client

    settings = MCPSettings(
        servers=[
            MCPServer(name="test-stdio", command="echo", args=["hello"], transport="stdio"),
        ]
    )
    llm = FakeChatModel(answer="test")

    _get_mcp_tools(settings)

    server_dict = mock_mcp_client_cls.call_args[0][0]
    assert "test-stdio" in server_dict
    assert server_dict["test-stdio"]["transport"] == "stdio"


@patch("assistant.assistant_container.MultiServerMCPClient")
def test_http_server_gets_tools(mock_mcp_client_cls):
    mock_client = MagicMock()
    mock_client.get_tools = AsyncMock(return_value=[])
    mock_mcp_client_cls.return_value = mock_client

    settings = MCPSettings(
        servers=[
            MCPServer(name="test-sse", url="http://localhost:8080/sse", transport="sse"),
        ]
    )
    llm = FakeChatModel(answer="test")

    _get_mcp_tools(settings)

    server_dict = mock_mcp_client_cls.call_args[0][0]
    assert "test-sse" in server_dict
    assert server_dict["test-sse"]["transport"] == "sse"
    assert server_dict["test-sse"]["url"] == "http://localhost:8080/sse"


@patch("assistant.assistant_container.MultiServerMCPClient")
def test_http_server_preserves_headers(mock_mcp_client_cls):
    mock_client = MagicMock()
    mock_client.get_tools = AsyncMock(return_value=[])
    mock_mcp_client_cls.return_value = mock_client

    settings = MCPSettings(
        servers=[
            MCPServer(
                name="test-sse",
                url="http://localhost:8080/sse",
                transport="sse",
                headers={"Authorization": "Bearer token"},
            ),
        ]
    )
    llm = FakeChatModel(answer="test")

    _get_mcp_tools(settings)

    server_dict = mock_mcp_client_cls.call_args[0][0]
    assert server_dict["test-sse"]["headers"] == {"Authorization": "Bearer token"}


@patch("assistant.assistant_container.MultiServerMCPClient")
def test_multiple_servers(mock_mcp_client_cls):
    mock_client = MagicMock()
    mock_client.get_tools = AsyncMock(return_value=[])
    mock_mcp_client_cls.return_value = mock_client

    settings = MCPSettings(
        servers=[
            MCPServer(name="server-a", command="cmd", transport="stdio"),
            MCPServer(name="server-b", url="http://localhost/sse", transport="sse"),
        ]
    )
    llm = FakeChatModel(answer="test")

    _get_mcp_tools(settings)

    assert mock_mcp_client_cls.call_count == 2


@patch("assistant.assistant_container.MultiServerMCPClient")
def test_empty_servers_returns_no_tools(mock_mcp_client_cls):
    settings = MCPSettings(servers=[])
    llm = FakeChatModel(answer="test")

    tools, failed_servers = _get_mcp_tools(settings)

    assert tools == {}
    assert failed_servers == []
    mock_mcp_client_cls.assert_not_called()


@patch("assistant.assistant_container.MultiServerMCPClient")
def test_failing_server_does_not_break_others(mock_mcp_client_cls):
    """When one server fails to load tools, the others still contribute their tools."""
    good_tool = MagicMock()

    def client_side_effect(server_dict):
        client = MagicMock()
        name = list(server_dict.keys())[0]
        if name == "bad-server":
            client.get_tools = AsyncMock(side_effect=ConnectionError("refused"))
        else:
            client.get_tools = AsyncMock(return_value=[good_tool])
        return client

    mock_mcp_client_cls.side_effect = client_side_effect

    settings = MCPSettings(
        servers=[
            MCPServer(name="good-server", command="echo", transport="stdio"),
            MCPServer(name="bad-server", command="fail", transport="stdio"),
        ]
    )
    llm = FakeChatModel(answer="test")

    tools, failed_servers = _get_mcp_tools(settings)

    assert tools == {None: [good_tool]}
    assert failed_servers == ["bad-server"]


@patch("assistant.assistant_container._get_mcp_tools")
@patch("assistant.assistant_container.load_mcp_settings_from_json")
def test_strict_tool_check_exits_on_failed_servers(mock_load_settings, mock_get_tools):
    """Test that strict_tool_check=True causes SystemExit when servers fail."""
    from assistant.assistant_container import _di_config
    from inject import Binder

    mock_load_settings.return_value = MCPSettings(
        servers=[MCPServer(name="bad", command="fail", transport="stdio")],
        strict_tool_check=True,
    )
    mock_get_tools.return_value = ({}, ["bad"])

    binder = MagicMock(spec=Binder)
    with pytest.raises(SystemExit) as exc_info:
        _di_config(binder)
    assert exc_info.value.code == 1


@patch("assistant.assistant_container.create_deep_agent")
@patch("assistant.assistant_container.ChatOpenAI")
@patch("assistant.assistant_container._get_mcp_tools")
@patch("assistant.assistant_container.load_mcp_settings_from_json")
def test_strict_tool_check_no_exit_when_all_servers_ok(
    mock_load_settings, mock_get_tools, mock_chat_openai, mock_create_deep_agent
):
    """Test that strict_tool_check=True does not exit when all servers provide tools."""
    from assistant.assistant_container import _di_config
    from inject import Binder

    mock_load_settings.return_value = MCPSettings(
        servers=[MCPServer(name="good", command="echo", transport="stdio")],
        strict_tool_check=True,
    )
    mock_get_tools.return_value = ({None: []}, [])
    mock_chat_openai.return_value = MagicMock()
    mock_create_deep_agent.return_value = MagicMock()

    binder = MagicMock(spec=Binder)
    _di_config(binder)  # Should not raise
