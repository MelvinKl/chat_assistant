# test_chat_graph.py
"""Unittests for chat_graph.py"""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

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


########################################################################################
# Tests – top-level
########################################################################################
class TestGraphNodeNames:
    def test_enum_values(self):
        assert GraphNodeNames.REPHRASE_QUESTION == "rephrase_question"
        assert GraphNodeNames.DETERMINE_LANGUAGE == "determine_language"
        assert GraphNodeNames.DECIDE == "decide"
        assert GraphNodeNames.ERROR_NODE == "error_node"
        assert GraphNodeNames.REPHRASE_ANSWER == "rephrase_answer"


class TestChatGraph:
    # ------------------------------------------------------------------ #
    # async ainvoke() workflow                                             #
    # ------------------------------------------------------------------ #
    @pytest.mark.asyncio
    async def test_ainvoke_returns_empty_string_for_empty_input(self, chat_graph):
        result = await chat_graph.ainvoke([])
        assert result == "No question has been found."

    @pytest.mark.asyncio
    async def test_ainvoke_happy_path(self, chat_graph, fake_answer_rephraser):
        chat_graph._graph.ainvoke.return_value = {"processed_answer": "42"}
        messages = [("user", "hello"), ("bot", "hi"), ("user", "meaning of life?")]
        result = await chat_graph.ainvoke(messages)

        assert result == "42"
        chat_graph._graph.ainvoke.assert_awaited_once()
        assert chat_graph._graph.ainvoke.call_args.kwargs["config"] is None  # no config supplied

    @pytest.mark.asyncio
    async def test_ainvoke_produces_correct_state(
        self,
        chat_graph,
    ):
        """Verify GraphState.create is called with the expected parts."""
        with patch("assistant.impl.graph.chat_graph.GraphState", create=True) as fake_gs:
            fake_gs.create = MagicMock()
            chat_graph._graph.ainvoke.return_value = {"processed_answer": "ok"}
            await chat_graph.ainvoke([("user", "q")])
            fake_gs.create.assert_called_once_with(
                history=[], question="q", additional_info="extra context"
            )
            
    # ------------------------------------------------------------------ #
    # Node level unit tests                                              #
    # ------------------------------------------------------------------ #
    @pytest.mark.asyncio
    async def test_determine_language_node(self, chat_graph):
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
        result = await chat_graph._answer_rephraser_node(
            {"question": "q", "raw_answer": "answer"}
        )
        assert result == {"processed_answer": "Refined answer"}

    @pytest.mark.asyncio
    async def test_decide_node(self, chat_graph, fake_mcp_agent):
        fake_mcp_agent.ainvoke.return_value = {"messages": [MagicMock(content="42")]}
        result = await chat_graph._decide_node(
            {"question": "meaning of life"}
        )
        assert result == {"raw_answer": "42"}
        fake_mcp_agent.ainvoke.assert_awaited_once_with(
            {"messages": "meaning of life"}, None
        )

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

