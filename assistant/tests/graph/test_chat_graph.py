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
def fake_info_settings() -> MagicMock:
    """Mock `InformationSettings`."""
    ms = MagicMock(spec=["information"])
    ms.information = "extra context"
    return ms


@pytest.fixture
def chat_graph(
    fake_llm,
    fake_question_rephraser,
    fake_answer_rephraser,
    fake_mcp_agent,
    fake_info_settings,
) -> ChatGraph:
    """Instance assembled with mocked dependencies."""
    with patch("assistant.impl.graph.chat_graph.StateGraph", autospec=True):
        cg = ChatGraph(
            llm=fake_llm,
            question_rephraser=fake_question_rephraser,
            answer_rephraser=fake_answer_rephraser,
            mcp_agent=fake_mcp_agent,
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
    fake_info_settings,
) -> ChatGraph:
    """Instance with the real StateGraph, so the compiled graph's edges and
    image export are read without mocks in the way."""
    return ChatGraph(
        llm=fake_llm,
        question_rephraser=fake_question_rephraser,
        answer_rephraser=fake_answer_rephraser,
        mcp_agent=fake_mcp_agent,
        information_settings=fake_info_settings,
    )


########################################################################################
# Tests – top-level
########################################################################################
class TestGraphNodeNames:
    def test_enum_values(self):
        """Implements "the graph contains the four processing nodes"
        (requirements/chat-graph.feature)
        """
        assert GraphNodeNames.REPHRASE_QUESTION == "rephrase_question"
        assert GraphNodeNames.DETERMINE_LANGUAGE == "determine_language"
        assert GraphNodeNames.DECIDE == "decide"
        assert GraphNodeNames.REPHRASE_ANSWER == "rephrase_answer"


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

            sg_mock.add_node.assert_any_call(GraphNodeNames.REPHRASE_QUESTION, chat_graph._rephrase_question_node)
            sg_mock.add_node.assert_any_call(GraphNodeNames.DETERMINE_LANGUAGE, chat_graph._determine_language_node)
            sg_mock.add_node.assert_any_call(GraphNodeNames.DECIDE, chat_graph._decide_node)
            sg_mock.add_node.assert_any_call(GraphNodeNames.REPHRASE_ANSWER, chat_graph._answer_rephraser_node)
            assert sg_mock.add_node.call_count == 4


########################################################################################
# Tests – real graph wiring and image export
########################################################################################
class TestGraphWiring:
    def test_wired_graph_edges(self, wired_chat_graph):
        """Implements "the graph starts both language detection and question rephrasing"
        (requirements/chat-graph.feature)
        Implements "the question rephrasing feeds the decision"
        (requirements/chat-graph.feature)
        Implements "language detection and decision converge into the answer rephrasing"
        (requirements/chat-graph.feature)
        """
        edges = {(str(edge.source), str(edge.target)) for edge in wired_chat_graph._graph.get_graph().edges}
        assert (START, "determine_language") in edges
        assert (START, "rephrase_question") in edges
        assert ("rephrase_question", "decide") in edges
        assert ("determine_language", "rephrase_answer") in edges
        assert ("decide", "rephrase_answer") in edges
        assert ("rephrase_answer", END) in edges


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
