# test_chat_graph.py
"""Unittests for chat_graph.py"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.messages import HumanMessage
from langgraph.graph import END, START

from assistant.impl.graph.chat_graph import ChatGraph, GraphNodeNames
from assistant.impl.graph.graph_state import GraphState
from assistant.impl.stages.stage import Stage

from ..fake_chat_model import FakeChatModel


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
def fake_preprocess_stage() -> AsyncMock:
    """The preprocess node awaits this."""
    return AsyncMock(name="preprocess_stage")


@pytest.fixture
def fake_postprocess_stage() -> AsyncMock:
    """The postprocess node awaits this."""
    return AsyncMock(name="postprocess_stage")


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
    fake_preprocess_stage,
    fake_postprocess_stage,
    fake_info_settings,
) -> ChatGraph:
    """Instance assembled with mocked dependencies."""
    with patch("assistant.impl.graph.chat_graph.StateGraph", autospec=True):
        cg = ChatGraph(
            llm=fake_llm,
            question_rephraser=fake_question_rephraser,
            answer_rephraser=fake_answer_rephraser,
            mcp_agent=fake_mcp_agent,
            preprocess_stage=fake_preprocess_stage,
            postprocess_stage=fake_postprocess_stage,
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
        assert GraphNodeNames.REPHRASE_ANSWER == "rephrase_answer"
        assert GraphNodeNames.PREPROCESS == "preprocess"
        assert GraphNodeNames.POSTPROCESS == "postprocess"


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
            fake_gs.create.assert_called_once_with(history=[], question="q", additional_info="extra context")

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
        result = await chat_graph._answer_rephraser_node({"question": "q", "raw_answer": "answer"})
        assert result == {"processed_answer": "Refined answer"}

    @pytest.mark.asyncio
    async def test_preprocess_node(self, chat_graph, fake_preprocess_stage):
        fake_preprocess_stage.ainvoke.return_value = "Refined question"
        state_dict = {"question": "old", "history": [], "additional_info": "x"}
        result = await chat_graph._preprocess_node(state_dict)
        assert result == {"question": "Refined question", "preprocessed_question": "Refined question"}
        fake_preprocess_stage.ainvoke.assert_awaited_once_with(state_dict, None)

    @pytest.mark.asyncio
    async def test_postprocess_node(self, chat_graph, fake_postprocess_stage):
        fake_postprocess_stage.ainvoke.return_value = "Polished answer"
        state_dict = {"question": "q", "raw_answer": "answer"}
        result = await chat_graph._postprocess_node(state_dict)
        assert result == {"raw_answer": "Polished answer", "postprocessed_answer": "Polished answer"}
        fake_postprocess_stage.ainvoke.assert_awaited_once_with(state_dict, None)

    @pytest.mark.asyncio
    async def test_decide_node(self, chat_graph, fake_mcp_agent):
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
            sg_mock.add_node.assert_any_call(GraphNodeNames.PREPROCESS, chat_graph._preprocess_node)
            sg_mock.add_node.assert_any_call(GraphNodeNames.POSTPROCESS, chat_graph._postprocess_node)
            assert sg_mock.add_node.call_count == 6

    def test_wire_graph_edges(self, chat_graph):
        with patch("assistant.impl.graph.chat_graph.StateGraph", autospec=True) as sg_mock:
            chat_graph._state_graph = sg_mock
            with patch.object(chat_graph, "_add_nodes"):
                chat_graph._wire_graph()

            edges = [c.args for c in sg_mock.add_edge.call_args_list]
            assert edges == [
                (START, GraphNodeNames.DETERMINE_LANGUAGE),
                (START, GraphNodeNames.PREPROCESS),
                (GraphNodeNames.PREPROCESS, GraphNodeNames.REPHRASE_QUESTION),
                (GraphNodeNames.REPHRASE_QUESTION, GraphNodeNames.DECIDE),
                ([GraphNodeNames.DETERMINE_LANGUAGE, GraphNodeNames.DECIDE], GraphNodeNames.POSTPROCESS),
                (GraphNodeNames.POSTPROCESS, GraphNodeNames.REPHRASE_ANSWER),
                (GraphNodeNames.REPHRASE_ANSWER, END),
            ]


########################################################################################
# End-to-end tests – real compiled graph with real Stage runnables
########################################################################################
class RecordingFakeChatModel(FakeChatModel):
    """FakeChatModel that also records the messages it was invoked with."""

    messages_history: list = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.messages_history = []

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        self.messages_history.append(list(messages))
        return super()._generate(messages=messages, stop=stop, run_manager=run_manager, **kwargs)

    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
        return self._generate(messages=messages, stop=stop, run_manager=run_manager, **kwargs)


@pytest.fixture
def pipeline_preprocess_llm() -> RecordingFakeChatModel:
    return RecordingFakeChatModel(answer="preprocessed question")


@pytest.fixture
def pipeline_postprocess_llm() -> RecordingFakeChatModel:
    return RecordingFakeChatModel(answer="postprocessed answer")


@pytest.fixture
def pipeline_preprocess_stage(pipeline_preprocess_llm) -> Stage:
    return Stage(
        llm=pipeline_preprocess_llm,
        system_prompt="You are the preprocessing stage.",
        user_prompt="Question: {question}",
    )


@pytest.fixture
def pipeline_postprocess_stage(pipeline_postprocess_llm) -> Stage:
    return Stage(
        llm=pipeline_postprocess_llm,
        system_prompt="You are the postprocessing stage.",
        user_prompt="Answer: {raw_answer}",
    )


@pytest.fixture
def pipeline_chat_graph(
    fake_llm,
    fake_question_rephraser,
    fake_answer_rephraser,
    fake_mcp_agent,
    pipeline_preprocess_stage,
    pipeline_postprocess_stage,
    fake_info_settings,
) -> ChatGraph:
    """ChatGraph with a real (unpatched) StateGraph and real Stage runnables."""
    return ChatGraph(
        llm=fake_llm,
        question_rephraser=fake_question_rephraser,
        answer_rephraser=fake_answer_rephraser,
        mcp_agent=fake_mcp_agent,
        preprocess_stage=pipeline_preprocess_stage,
        postprocess_stage=pipeline_postprocess_stage,
        information_settings=fake_info_settings,
    )


class TestChatGraphPipeline:
    """Runs the real compiled graph end-to-end, including the two stages."""

    @pytest.mark.asyncio
    async def test_ainvoke_runs_full_pipeline(
        self,
        pipeline_chat_graph,
        fake_mcp_agent,
        fake_question_rephraser,
        fake_answer_rephraser,
    ):
        fake_mcp_agent.ainvoke.return_value = {"messages": [MagicMock(content="raw answer")]}
        fake_question_rephraser.ainvoke.return_value = "rephrased question"
        fake_answer_rephraser.ainvoke.return_value = "butler answer"

        result = await pipeline_chat_graph.ainvoke([("user", "What is the meaning of life?")])

        assert result == "butler answer"

    @pytest.mark.asyncio
    async def test_pipeline_state_and_stage_ordering(
        self,
        pipeline_chat_graph,
        fake_mcp_agent,
        fake_question_rephraser,
        fake_answer_rephraser,
        pipeline_preprocess_llm,
        pipeline_postprocess_llm,
    ):
        fake_mcp_agent.ainvoke.return_value = {"messages": [MagicMock(content="raw answer")]}
        fake_question_rephraser.ainvoke.return_value = "rephrased question"
        fake_answer_rephraser.ainvoke.return_value = "butler answer"

        state = GraphState.create(
            history=[],
            question="What is the meaning of life?",
            additional_info="extra context",
        )
        final_state = await pipeline_chat_graph._graph.ainvoke(input=state)

        # The stage outputs are stored in the final state.
        assert final_state["preprocessed_question"] == "preprocessed question"
        assert final_state["postprocessed_answer"] == "postprocessed answer"
        # The postprocess node runs after the answer was generated and rewrites the raw answer.
        assert final_state["raw_answer"] == "postprocessed answer"
        # The answer rephraser runs after the postprocess stage.
        assert final_state["processed_answer"] == "butler answer"
        # The language detection runs before the postprocess stage.
        assert final_state["question_language"] == "en"

        # The preprocessing stage saw the original question ...
        pre_messages = pipeline_preprocess_llm.messages_history[0]
        pre_user_message = [m for m in pre_messages if isinstance(m, HumanMessage)][0]
        assert "What is the meaning of life?" in pre_user_message.content
        # ... and the remaining pipeline ran with the preprocessed question.
        assert final_state["question"] == "rephrased question"
        rephraser_state = fake_question_rephraser.ainvoke.call_args[0][0]
        assert rephraser_state["question"] == "preprocessed question"

        # The postprocess stage ran after the answer had returned and saw the generated answer.
        post_messages = pipeline_postprocess_llm.messages_history[0]
        post_user_message = [m for m in post_messages if isinstance(m, HumanMessage)][0]
        assert "raw answer" in post_user_message.content
