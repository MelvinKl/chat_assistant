# test_mcp_client_setup.py
"""Tests that _get_mcp_tools registers the sampling callback with all MCP server connections."""

from unittest.mock import AsyncMock, MagicMock, patch

from assistant.assistant_container import _get_mcp_tools
from assistant.impl.settings.mcp_server_settings import MCPServer, MCPSettings
from tests.fake_chat_model import FakeChatModel


@patch("assistant.assistant_container.MultiServerMCPClient")
def test_stdio_server_gets_tools(mock_mcp_client_cls):
    """Implements "a stdio server is connected with its command"
    (requirements/mcp-integration.feature)

    When the tools of a stdio server are loaded, the mcp client is created
    with the server's command, its args and the stdio transport.
    """
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

    server_dict = mock_mcp_client_cls.call_args[0][0]
    assert "test-stdio" in server_dict
    assert server_dict["test-stdio"]["command"] == "echo"
    assert server_dict["test-stdio"]["args"] == ["hello"]
    assert server_dict["test-stdio"]["transport"] == "stdio"


@patch("assistant.assistant_container.MultiServerMCPClient")
def test_http_server_gets_tools(mock_mcp_client_cls):
    """Implements "a remote server is connected with its url"
    (requirements/mcp-integration.feature)

    When the tools of a remote server are loaded, the mcp client is created
    with the server's url and its transport.
    """
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


@patch("assistant.assistant_container.MultiServerMCPClient")
def test_http_server_preserves_headers(mock_mcp_client_cls):
    """Implements "server headers are preserved on the connection"
    (requirements/mcp-integration.feature)

    When the tools of a remote server with configured headers are loaded,
    the mcp client receives the configured headers.
    """
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
def test_multiple_servers(mock_mcp_client_cls):
    """Implements "every server is connected with its own client"
    (requirements/mcp-integration.feature)

    When the tools of two configured mcp servers are loaded, each server is
    connected through a separate mcp client.
    """
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

    assert mock_mcp_client_cls.call_count == 2


@patch("assistant.assistant_container.MultiServerMCPClient")
def test_empty_servers_returns_no_tools(mock_mcp_client_cls):
    settings = MCPSettings(servers=[])
    llm = FakeChatModel(answer="test")

    tools = _get_mcp_tools(settings, llm)

    assert tools == {}
    mock_mcp_client_cls.assert_not_called()


@patch("assistant.assistant_container.MultiServerMCPClient")
def test_failing_server_does_not_break_others(mock_mcp_client_cls):
    """Implements "a failing server does not prevent the other servers from loading tools"
    (requirements/mcp-integration.feature)

    When one server fails to load tools, the tools of the succeeding server
    are registered and the failure is logged without aborting the load.
    """
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

    tools = _get_mcp_tools(settings, llm)

    assert tools == {None: [good_tool]}


@patch("assistant.assistant_container.MultiServerMCPClient")
def test_server_tools_grouped_by_agent_assignment(mock_mcp_client_cls):
    """Implements "server tools are grouped by their agent assignment"
    (requirements/mcp-integration.feature)

    When the tools of the servers are loaded, the tools of the server without
    an ``agent`` are registered under the main agent and the tools of the
    server with an ``agent`` name under that subagent.
    """
    main_tool = MagicMock()
    subagent_tool = MagicMock()

    def client_side_effect(server_dict):
        client = MagicMock()
        name = list(server_dict.keys())[0]
        tools = [main_tool] if name == "main-server" else [subagent_tool]
        client.get_tools = AsyncMock(return_value=tools)
        return client

    mock_mcp_client_cls.side_effect = client_side_effect

    settings = MCPSettings(
        servers=[
            MCPServer(name="main-server", command="cmd", transport="stdio"),
            MCPServer(name="weather-server", command="cmd", transport="stdio", agent="weather"),
        ]
    )
    llm = FakeChatModel(answer="test")

    tools = _get_mcp_tools(settings, llm)

    assert tools == {None: [main_tool], "weather": [subagent_tool]}


@patch("assistant.assistant_container.MultiServerMCPClient")
def test_server_assigned_to_preprocessing_stage(mock_mcp_client_cls):
    """Implements "a server assigned to the preprocessing stage registers its tools for that stage"
    (requirements/mcp-integration.feature)

    When the tools of a server whose ``agent`` field is ``preprocessing``
    are loaded, the tools of the server are registered under the
    preprocessing stage.
    """
    stage_tool = MagicMock()

    mock_client = MagicMock()
    mock_client.get_tools = AsyncMock(return_value=[stage_tool])
    mock_mcp_client_cls.return_value = mock_client

    settings = MCPSettings(
        servers=[
            MCPServer(name="prep-server", command="cmd", transport="stdio", agent="preprocessing"),
        ]
    )
    llm = FakeChatModel(answer="test")

    tools = _get_mcp_tools(settings, llm)

    assert tools == {"preprocessing": [stage_tool]}


@patch("assistant.assistant_container.MultiServerMCPClient")
def test_server_assigned_to_postprocessing_stage(mock_mcp_client_cls):
    """Implements "a server assigned to the postprocessing stage registers its tools for that stage"
    (requirements/mcp-integration.feature)

    When the tools of a server whose ``agent`` field is ``postprocessing``
    are loaded, the tools of the server are registered under the
    postprocessing stage.
    """
    stage_tool = MagicMock()

    mock_client = MagicMock()
    mock_client.get_tools = AsyncMock(return_value=[stage_tool])
    mock_mcp_client_cls.return_value = mock_client

    settings = MCPSettings(
        servers=[
            MCPServer(name="post-server", command="cmd", transport="stdio", agent="postprocessing"),
        ]
    )
    llm = FakeChatModel(answer="test")

    tools = _get_mcp_tools(settings, llm)

    assert tools == {"postprocessing": [stage_tool]}


@patch("assistant.assistant_container.MultiServerMCPClient")
def test_sampling_callback_registered_on_every_connection(mock_mcp_client_cls):
    """Implements "the sampling callback is registered with every connected mcp server"
    (requirements/mcp-sampling.feature)

    When the tools of the configured mcp servers are loaded, every mcp client
    connection carries the sampling callback of the LLM. The installed
    langchain-mcp-adapters takes no callback at the client level, so the
    registration rides the connection dicts: each ``MultiServerMCPClient``
    call receives a server dict whose connection carries the LLM's sampling
    callback under ``session_kwargs``, the session kwargs the adapter's
    session creators forward to the ``mcp`` SDK's ``ClientSession``.
    """
    mock_client = MagicMock()
    mock_client.get_tools = AsyncMock(return_value=[])
    mock_mcp_client_cls.return_value = mock_client

    settings = MCPSettings(
        servers=[
            MCPServer(name="test-stdio", command="echo", args=["hello"], transport="stdio"),
            MCPServer(name="test-sse", url="http://localhost:8080/sse", transport="sse"),
        ]
    )
    llm = FakeChatModel(answer="test")

    _get_mcp_tools(settings, llm)

    assert mock_mcp_client_cls.call_count == len(settings.servers)
    for call in mock_mcp_client_cls.call_args_list:
        for connection in call.args[0].values():
            assert connection["session_kwargs"]["sampling_callback"] is not None
