# test_mcp_client_setup.py
"""Tests that _get_mcp_tools registers the sampling callback with all MCP server connections."""

from unittest.mock import AsyncMock, MagicMock, patch

from assistant.assistant_container import _get_mcp_tools
from assistant.impl.settings.mcp_server_settings import MCPServer, MCPSettings
from tests.fake_chat_model import FakeChatModel


@patch("assistant.assistant_container.MultiServerMCPClient")
@patch("assistant.assistant_container.create_sampling_callback")
def test_stdio_server_gets_sampling_callback(mock_create_cb, mock_mcp_client_cls):
    mock_callback = AsyncMock()
    mock_create_cb.return_value = mock_callback

    mock_client = MagicMock()
    mock_client.get_tools = AsyncMock(return_value=[])
    mock_mcp_client_cls.return_value = mock_client

    settings = MCPSettings(
        servers=[
            MCPServer(name="test-stdio", command="echo", args=["hello"], transport="stdio"),
        ]
    )
    llm = FakeChatModel(answer="test")

    _get_mcp_tools(settings, llm)

    mock_create_cb.assert_called_once_with(llm)
    server_dict = mock_mcp_client_cls.call_args[0][0]
    assert "test-stdio" in server_dict
    assert server_dict["test-stdio"]["transport"] == "stdio"
    session_kwargs = mock_mcp_client_cls.call_args.kwargs["session_kwargs"]
    assert session_kwargs["sampling_callback"] is mock_callback


@patch("assistant.assistant_container.MultiServerMCPClient")
@patch("assistant.assistant_container.create_sampling_callback")
def test_http_server_gets_sampling_callback(mock_create_cb, mock_mcp_client_cls):
    mock_callback = AsyncMock()
    mock_create_cb.return_value = mock_callback

    mock_client = MagicMock()
    mock_client.get_tools = AsyncMock(return_value=[])
    mock_mcp_client_cls.return_value = mock_client

    settings = MCPSettings(
        servers=[
            MCPServer(name="test-sse", url="http://localhost:8080/sse", transport="sse"),
        ]
    )
    llm = FakeChatModel(answer="test")

    _get_mcp_tools(settings, llm)

    server_dict = mock_mcp_client_cls.call_args[0][0]
    assert "test-sse" in server_dict
    assert server_dict["test-sse"]["transport"] == "sse"
    assert server_dict["test-sse"]["url"] == "http://localhost:8080/sse"
    session_kwargs = mock_mcp_client_cls.call_args.kwargs["session_kwargs"]
    assert session_kwargs["sampling_callback"] is mock_callback


@patch("assistant.assistant_container.MultiServerMCPClient")
@patch("assistant.assistant_container.create_sampling_callback")
def test_http_server_preserves_headers(mock_create_cb, mock_mcp_client_cls):
    mock_create_cb.return_value = AsyncMock()

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

    _get_mcp_tools(settings, llm)

    server_dict = mock_mcp_client_cls.call_args[0][0]
    assert server_dict["test-sse"]["headers"] == {"Authorization": "Bearer token"}


@patch("assistant.assistant_container.MultiServerMCPClient")
@patch("assistant.assistant_container.create_sampling_callback")
def test_multiple_servers_share_same_callback(mock_create_cb, mock_mcp_client_cls):
    mock_callback = AsyncMock()
    mock_create_cb.return_value = mock_callback

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

    _get_mcp_tools(settings, llm)

    # Callback is created once and reused
    mock_create_cb.assert_called_once_with(llm)

    # Each server call gets the same callback
    assert mock_mcp_client_cls.call_count == 2
    for call in mock_mcp_client_cls.call_args_list:
        session_kwargs = call.kwargs["session_kwargs"]
        assert session_kwargs["sampling_callback"] is mock_callback


@patch("assistant.assistant_container.MultiServerMCPClient")
@patch("assistant.assistant_container.create_sampling_callback")
def test_empty_servers_returns_no_tools(mock_create_cb, mock_mcp_client_cls):
    settings = MCPSettings(servers=[])
    llm = FakeChatModel(answer="test")

    tools = _get_mcp_tools(settings, llm)

    assert tools == []
    mock_mcp_client_cls.assert_not_called()


@patch("assistant.assistant_container.MultiServerMCPClient")
@patch("assistant.assistant_container.create_sampling_callback")
def test_failing_server_does_not_break_others(mock_create_cb, mock_mcp_client_cls):
    """When one server fails to load tools, the others still contribute their tools."""
    mock_create_cb.return_value = AsyncMock()

    good_tool = MagicMock()

    def client_side_effect(server_dict, session_kwargs=None):
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

    tools = _get_mcp_tools(settings, llm)

    assert tools == [good_tool]
