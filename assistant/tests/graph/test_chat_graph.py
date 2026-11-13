# test_chat_graph.py
"""Unittests for chat_graph.py"""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langgraph.graph import END, START

from assistant.impl.graph.chat_graph import ChatGraph, GraphNodeNames


########################################################################################
# Shared test fixtures and Mocks
########################################################################################
@pytest.fixture
def fake_llm():
    return MagicMock(name="BaseChatModel")


@pytest.fixture
def fake_question_rephraser() -> AsyncMock:
    """Async version so `ainvoke` works in rephrase question node."""
    return AsyncMock(name="question_rephraser")


@pytest.fixture
def fake_answer_rephraser() -> AsyncMock:
    """Async version so `ainvoke` works in answer rephrase node."""
    return AsyncMock(name="answer_rephraser")


@pytest.fixture
def fake_mcp_agent() -> AsyncMock:
    """The decide node awaits this."""
    return AsyncMock(name="mcp_agent")


@pytest.fixture
def fake_preprocessing() -> AsyncMock:
    """Async version so `ainvoke` works in the preprocessing node."""
    return AsyncMock(name="preprocessing")


@pytest.fixture
def fake_postprocessing() -> AsyncMock:
    """Async version so `ainvoke` works in the postprocessing node."""
    return AsyncMock(name="postprocessing")


@pytest.fixture
def fake_info_settings() -> MagicMock:
    """Mock `InformationSettings`."""
    ms = MagicMock(spec=["information"])
    ms.information = "extra context"
    return ms


@pytest.fixture
def fake_system_one_settings() -> MagicMock:
    """Mock `SystemOneSettings` with a configured model."""
    settings = MagicMock(spec=["model", "base_url", "api_key"])
    settings.model = "the system one model"
    settings.base_url = "http://the system one url"
    settings.api_key = "the system one api key"
    return settings


@pytest.fixture
def fake_mcp_settings() -> MagicMock:
    """Mock `MCPSettings` with the available MCP servers."""
    first_server = MagicMock(spec=["name"])
    first_server.name = "the first mcp server"
    second_server = MagicMock(spec=["name"])
    second_server.name = "the second mcp server"
    settings = MagicMock(spec=["servers"])
    settings.servers = [first_server, second_server]
    return settings


@pytest.fixture
def chat_graph_with_system_one(
    fake_llm,
    fake_question_rephraser,
    fake_answer_rephraser,
    fake_mcp_agent,
    fake_preprocessing,
    fake_postprocessing,
    fake_info_settings,
    fake_system_one_settings,
    fake_mcp_settings,
) -> ChatGraph:
    """The `chat_graph` fixture with a configured SystemOne model and the
    available MCP servers, so the invocation runs the reachability
    determination."""
    with patch("assistant.impl.graph.chat_graph.StateGraph", autospec=True):
        cg = ChatGraph(
            llm=fake_llm,
            question_rephraser=fake_question_rephraser,
            answer_rephraser=fake_answer_rephraser,
            mcp_agent=fake_mcp_agent,
            preprocessing=fake_preprocessing,
            postprocessing=fake_postprocessing,
            information_settings=fake_info_settings,
            system_one=fake_system_one_settings,
            mcp_settings=fake_mcp_settings,
        )
        # Patch the compiled graph to async invoke safely.
        cg._graph = AsyncMock()
        return cg


@pytest.fixture
def reachable_system_one() -> MagicMock:
    """The SystemOne model answering that the user's goal is reachable."""
    model = MagicMock(name="system_one_model")
    model.ainvoke = AsyncMock(return_value=MagicMock(content="reachable"))
    with patch("assistant.impl.graph.chat_graph.ChatOpenAI", return_value=model):
        yield model


@pytest.fixture
def unreachable_system_one() -> MagicMock:
    """The SystemOne model answering that the user's goal is unreachable."""
    model = MagicMock(name="system_one_model")
    model.ainvoke = AsyncMock(return_value=MagicMock(content="unreachable"))
    with patch("assistant.impl.graph.chat_graph.ChatOpenAI", return_value=model):
        yield model


@pytest.fixture
def chat_graph(
    fake_llm,
    fake_question_rephraser,
    fake_answer_rephraser,
    fake_mcp_agent,
    fake_preprocessing,
    fake_postprocessing,
    fake_info_settings,
) -> ChatGraph:
    """Instance assembled with mocked dependencies."""
    with patch("assistant.impl.graph.chat_graph.StateGraph", autospec=True):
        cg = ChatGraph(
            llm=fake_llm,
            question_rephraser=fake_question_rephraser,
            answer_rephraser=fake_answer_rephraser,
            mcp_agent=fake_mcp_agent,
            preprocessing=fake_preprocessing,
            postprocessing=fake_postprocessing,
            information_settings=fake_info_settings,
        )
        # Patch the compiled graph to async invoke safely.
        cg._graph = AsyncMock()
        return cg


@pytest.fixture
def wired_chat_graph(
    fake_llm,
    fake_question_rephraser,
    fake_answer_rephraser,
    fake_mcp_agent,
    fake_preprocessing,
    fake_postprocessing,
    fake_info_settings,
) -> ChatGraph:
    """Instance with the real StateGraph, so the compiled graph's edges and
    image export are read without mocks in the way."""
    return ChatGraph(
        llm=fake_llm,
        question_rephraser=fake_question_rephraser,
        answer_rephraser=fake_answer_rephraser,
        mcp_agent=fake_mcp_agent,
        preprocessing=fake_preprocessing,
        postprocessing=fake_postprocessing,
        information_settings=fake_info_settings,
    )


########################################################################################
# Tests – top-level
########################################################################################
class TestGraphNodeNames:
    def test_enum_values(self):
        """Implements "the graph contains the six processing nodes"
        (requirements/chat-graph.feature)
        """
        assert GraphNodeNames.PREPROCESSING == "preprocessing"
        assert GraphNodeNames.REPHRASE_QUESTION == "rephrase_question"
        assert GraphNodeNames.DETERMINE_LANGUAGE == "determine_language"
        assert GraphNodeNames.DECIDE == "decide"
        assert GraphNodeNames.REPHRASE_ANSWER == "rephrase_answer"
        assert GraphNodeNames.POSTPROCESSING == "postprocessing"


class TestChatGraph:
    # ------------------------------------------------------------------ #
    # async ainvoke() workflow                                             #
    # ------------------------------------------------------------------ #
    @pytest.mark.asyncio
    async def test_ainvoke_returns_empty_string_for_empty_input(self, chat_graph):
        """Implements "an empty request yields the no question answer"
        (requirements/chat-graph.feature)
        """
        result = await chat_graph.ainvoke([])
        assert result == "No question has been found."

    @pytest.mark.asyncio
    async def test_ainvoke_happy_path(self, chat_graph, fake_answer_rephraser):
        """Implements "the invocation result is the processed answer"
        (requirements/chat-graph.feature)
        Implements "earlier messages become history entries"
        (requirements/chat-graph.feature)
        """
        chat_graph._graph.ainvoke.return_value = {"processed_answer": "42"}
        messages = [("user", "hello"), ("bot", "hi"), ("user", "meaning of life?")]
        with patch("assistant.impl.graph.chat_graph.GraphState", create=True) as fake_gs:
            fake_gs.create = MagicMock()
            result = await chat_graph.ainvoke(messages)
        fake_gs.create.assert_called_once_with(
            history=["user: hello", "bot: hi"],
            question="meaning of life?",
            additional_info="extra context",
        )

        assert result == "42"
        chat_graph._graph.ainvoke.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_ainvoke_produces_correct_state(
        self,
        chat_graph,
    ):
        """Verify GraphState.create is called with the expected parts.

        Implements "the last message is used as the question"
        (requirements/chat-graph.feature)
        Implements "the initial state carries the additional information"
        (requirements/chat-graph.feature)
        """
        with patch("assistant.impl.graph.chat_graph.GraphState", create=True) as fake_gs:
            fake_gs.create = MagicMock()
            chat_graph._graph.ainvoke.return_value = {"processed_answer": "ok"}
            await chat_graph.ainvoke([("user", "q")])
            fake_gs.create.assert_called_once_with(history=[], question="q", additional_info="extra context")

    @pytest.mark.asyncio
    async def test_the_system_one_model_determines_if_the_users_goal_can_be_reached(
        self,
        chat_graph_with_system_one,
        reachable_system_one,
    ):
        """Implements "the SystemOne model determines if the users goal can be reached"
        (requirements/chat-graph.feature)

        Given a chat graph with a configured SystemOne model, when the graph
        is invoked with a user question, the SystemOne model determines if
        the user's goal can be reached at all with the available MCP
        servers: the model is consulted with the question and the names of
        the available MCP servers before any node of the compiled graph
        runs, and a reachable determination lets the invocation run the
        graph.
        """
        chat_graph_with_system_one._graph.ainvoke.return_value = {"processed_answer": "the processed answer"}

        result = await chat_graph_with_system_one.ainvoke([("user", "how do I deploy the assistant?")])

        # The SystemOne model is consulted for the reachability determination.
        reachable_system_one.ainvoke.assert_awaited_once()
        prompt = reachable_system_one.ainvoke.await_args.args[0]
        assert "how do I deploy the assistant?" in prompt
        assert "the first mcp server" in prompt
        assert "the second mcp server" in prompt
        # The goal is reachable, so the invocation runs the compiled graph.
        chat_graph_with_system_one._graph.ainvoke.assert_awaited_once()
        assert result == "the processed answer"

    @pytest.mark.asyncio
    async def test_an_unreachable_goal_skips_the_stages_up_to_the_answer_generation(
        self,
        chat_graph_with_system_one,
        unreachable_system_one,
    ):
        """Implements "an unreachable goal skips the stages up to the answer generation"
        (requirements/chat-graph.feature)

        Given a chat graph with a configured SystemOne model and a user
        question whose goal cannot be reached with the available MCP
        servers, when the graph is invoked with the question, the stages up
        to the answer generation do not run (no stage LLM call on the
        question, the compiled graph is not run) and the returned answer
        informs the user that no MCP servers are currently available to
        help.
        """
        result = await chat_graph_with_system_one.ainvoke([("user", "how do I deploy the assistant?")])

        # The determination runs ...
        unreachable_system_one.ainvoke.assert_awaited_once()
        # ... and concludes the goal is unreachable: the stages up to the
        # answer generation do not run and neither does the compiled graph.
        chat_graph_with_system_one._preprocessing.ainvoke.assert_not_awaited()
        chat_graph_with_system_one._postprocessing.ainvoke.assert_not_awaited()
        chat_graph_with_system_one._graph.ainvoke.assert_not_awaited()
        # The returned answer informs the user that no MCP servers are
        # currently available to help.
        assert result == "No MCP servers are currently available to help."

    # ------------------------------------------------------------------ #
    # Node level unit tests                                              #
    # ------------------------------------------------------------------ #
    @pytest.mark.asyncio
    async def test_determine_language_node(self, chat_graph):
        """Implements "the language node detects the language of the question"
        (requirements/chat-graph.feature)
        """
        with patch("assistant.impl.graph.chat_graph.detect", return_value="de"):
            result = await chat_graph._determine_language_node({"question": "Wie geht's?"})
            assert result == {"question_language": "de"}

    @pytest.mark.asyncio
    async def test_rephrase_question_node(self, chat_graph, fake_question_rephraser):
        fake_question_rephraser.ainvoke.return_value = "Rephrased?"
        state_dict = {"question": "old", "history": ["user: hi", "assistant: hello"]}
        result = await chat_graph._rephrase_question_node(state_dict)
        assert result == {"question": "Rephrased?"}
        fake_question_rephraser.ainvoke.assert_awaited_once_with(state_dict, None)

    @pytest.mark.asyncio
    async def test_answer_rephraser_node(self, chat_graph, fake_answer_rephraser):
        fake_answer_rephraser.ainvoke.return_value = "Refined answer"
        result = await chat_graph._answer_rephraser_node({"question": "q", "raw_answer": "answer"})
        assert result == {"processed_answer": "Refined answer"}

    @pytest.mark.asyncio
    async def test_decide_node(self, chat_graph, fake_mcp_agent):
        """Implements "the decide node asks the MCP agent the rephrased question"
        (requirements/chat-graph.feature)
        """
        fake_mcp_agent.ainvoke.return_value = {"messages": [MagicMock(content="42")]}
        result = await chat_graph._decide_node({"question": "meaning of life"})
        assert result == {"raw_answer": "42"}
        fake_mcp_agent.ainvoke.assert_awaited_once_with({"messages": "meaning of life"}, None)

    # ------------------------------------------------------------------ #
    # Graph wiring                                                       #
    # ------------------------------------------------------------------ #
    def test_add_nodes_calls_state_graph_correctly(self, chat_graph):
        with (
            patch("assistant.impl.graph.chat_graph.StateGraph", autospec=True) as sg_mock,
            patch.object(chat_graph, "_wire_graph"),
        ):
            chat_graph._state_graph = sg_mock
            chat_graph._add_nodes()

            sg_mock.add_node.assert_any_call(GraphNodeNames.PREPROCESSING, chat_graph._preprocessing_node)
            sg_mock.add_node.assert_any_call(GraphNodeNames.REPHRASE_QUESTION, chat_graph._rephrase_question_node)
            sg_mock.add_node.assert_any_call(GraphNodeNames.DETERMINE_LANGUAGE, chat_graph._determine_language_node)
            sg_mock.add_node.assert_any_call(GraphNodeNames.DECIDE, chat_graph._decide_node)
            sg_mock.add_node.assert_any_call(GraphNodeNames.REPHRASE_ANSWER, chat_graph._answer_rephraser_node)
            sg_mock.add_node.assert_any_call(GraphNodeNames.POSTPROCESSING, chat_graph._postprocessing_node)
            assert sg_mock.add_node.call_count == 6


########################################################################################
# Tests – real graph wiring and image export
########################################################################################
class TestGraphWiring:
    def test_wired_graph_edges(self, wired_chat_graph):
        """Implements "the graph starts with the preprocessing step"
        (requirements/chat-graph.feature)
        Implements "the question rephrasing feeds the decision"
        (requirements/chat-graph.feature)
        Implements "language detection and decision converge into the answer rephrasing"
        (requirements/chat-graph.feature)
        """
        edges = {(str(edge.source), str(edge.target)) for edge in wired_chat_graph._graph.get_graph().edges}
        assert (START, "preprocessing") in edges
        assert ("preprocessing", "determine_language") in edges
        assert ("preprocessing", "rephrase_question") in edges
        assert ("rephrase_question", "decide") in edges
        assert ("determine_language", "rephrase_answer") in edges
        assert ("decide", "rephrase_answer") in edges
        assert ("rephrase_answer", "postprocessing") in edges
        assert ("postprocessing", END) in edges


class TestDrawGraph:
    def test_draw_graph_exports_png(self, wired_chat_graph, tmp_path):
        """Implements "the graph can be exported as an image"
        (requirements/chat-graph.feature)
        """

        def fake_draw(**kwargs):
            """Replace the mermaid render boundary so no network call is made."""
            Path(kwargs["output_file_path"]).write_bytes(b"\x89PNG")

        with patch("langchain_core.runnables.graph_mermaid.draw_mermaid_png", side_effect=fake_draw):
            wired_chat_graph.draw_graph(str(tmp_path))
        assert (tmp_path / "chat_graph.png").exists()
