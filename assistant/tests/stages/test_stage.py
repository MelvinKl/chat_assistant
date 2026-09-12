"""
Unit-tests for the Stage runnable.

Run with e.g.:

    $ pytest tests/stages/test_stage.py -vv

"""

import pytest
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool

from assistant.impl.stages.stage import Stage

from ..fake_chat_model import FakeChatModel


class FakeTool(BaseTool):
    """A tool that returns a fixed result."""

    name: str = "fake_tool"
    description: str = "A fake tool for testing."

    def _run(self, **kwargs) -> str:
        return "tool result"


class ToolCallingFakeChatModel(FakeChatModel):
    """Fake chat model that issues one tool call before answering."""

    call_count: int = 0
    messages_history: list = []

    def __init__(self, **kwargs):
        super().__init__(answer="final answer", **kwargs)
        self.call_count = 0
        self.messages_history = []

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        self.messages_history.append(list(messages))
        self.call_count += 1
        if self.call_count == 1:
            message = AIMessage(content="", tool_calls=[{"name": "fake_tool", "args": {"x": 1}, "id": "call-1"}])
        else:
            message = AIMessage(content=self.answer)
        return ChatResult(generations=[ChatGeneration(message=message)])

    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
        return self._generate(messages=messages, stop=stop, run_manager=run_manager, **kwargs)


@pytest.fixture
def dummy_llm():
    return FakeChatModel(answer="staged!")


@pytest.fixture
def simple_stage(dummy_llm):
    return Stage(
        llm=dummy_llm,
        system_prompt="System: {system_context}",
        user_prompt="User: {user_input}",
    )


def test_stage_initialisation():
    """Sanity that construction populates expected private attributes."""
    llm = FakeChatModel(answer="foo")
    stage = Stage(llm=llm, system_prompt="SYS: {val}", user_prompt="USR: {input}")

    assert stage._llm is llm
    assert stage._tools == {}
    actual_str = str(stage._prompt_template.messages)
    assert "SYS: {val}" in actual_str
    assert "USR: {input}" in actual_str


def test_stage_initialisation_with_tools():
    """Tools are bound to the llm and indexed by name."""
    llm = FakeChatModel(answer="foo")
    tool = FakeTool()
    stage = Stage(llm=llm, system_prompt="SYS", user_prompt="USR: {input}", tools=[tool])

    assert stage._tools == {"fake_tool": tool}


@pytest.mark.asyncio
async def test_ainvoke_basic_flow(simple_stage):
    """Exercises the async path without tools."""
    state = {"system_context": "ctx", "user_input": "how are you?"}
    answer = await simple_stage.ainvoke(state)

    assert answer == "staged!"


def test_invoke_basic_flow(simple_stage):
    """Exercises the sync path without tools."""
    state = {"system_context": "ctx", "user_input": "what is life?"}
    answer = simple_stage.invoke(state)

    assert answer == "staged!"


@pytest.mark.asyncio
async def test_ainvoke_passes_kwargs_through(simple_stage):
    """Check that extra kwargs wind up in the LLM call."""
    fake_llm = simple_stage._llm  # type: ignore[attr-defined]
    config = RunnableConfig(tags=["test"])
    await simple_stage.ainvoke(
        {"system_context": "x", "user_input": "y"},
        config=config,
        temperature=0.5,
        max_tokens=128,
    )

    assert fake_llm.kwargs_history
    kwargs = fake_llm.kwargs_history[-1]
    assert kwargs["temperature"] == 0.5
    assert kwargs["max_tokens"] == 128


@pytest.mark.asyncio
async def test_ainvoke_runs_tool_calls():
    """A tool call issued by the llm is executed and the final answer is returned."""
    llm = ToolCallingFakeChatModel()
    stage = Stage(llm=llm, system_prompt="SYS", user_prompt="USR: {input}", tools=[FakeTool()])

    answer = await stage.ainvoke({"input": "run the fake tool"})

    assert answer == "final answer"
    assert llm.call_count == 2
    second_call_messages = llm.messages_history[1]
    tool_messages = [m for m in second_call_messages if isinstance(m, ToolMessage)]
    assert len(tool_messages) == 1
    assert tool_messages[0].tool_call_id == "call-1"
    assert tool_messages[0].content == "tool result"


def test_invoke_runs_tool_calls():
    """The sync path executes tool calls as well."""
    llm = ToolCallingFakeChatModel()
    stage = Stage(llm=llm, system_prompt="SYS", user_prompt="USR: {input}", tools=[FakeTool()])

    answer = stage.invoke({"input": "run the fake tool"})

    assert answer == "final answer"
    assert llm.call_count == 2


@pytest.mark.asyncio
async def test_ainvoke_unknown_tool_is_handled():
    """A tool call for an unknown tool does not break the stage."""
    llm = ToolCallingFakeChatModel()
    stage = Stage(llm=llm, system_prompt="SYS", user_prompt="USR: {input}")

    answer = await stage.ainvoke({"input": "run a missing tool"})

    assert answer == "final answer"


def test_mandatory_state_parameters_are_fulfilled():
    """If the prompt requires fields missing in state, expect KeyError on invoke."""
    llm = FakeChatModel(answer="ok")
    stage = Stage(llm=llm, system_prompt="{a}", user_prompt="{b}")

    with pytest.raises(KeyError, match=r".*(a|b).*"):
        stage.invoke({})


# ------------------------------------------------------------
# Test running the file itself (quick smoke test)
# ------------------------------------------------------------
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
