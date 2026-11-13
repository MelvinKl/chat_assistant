"""
Unit-tests for the question answering Stage component.

Run with e.g.:

    $ pytest tests/test_stages.py -vv

"""

import pytest
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.tools import tool
from langchain_core.utils.function_calling import convert_to_openai_tool
from langchain_openai import ChatOpenAI

from assistant.impl.settings.system_one_settings import SystemOneSettings
from assistant.impl.stages.stage import Stage

from .fake_chat_model import FakeChatModel


class BindableFakeChatModel(FakeChatModel):
    """A fake model that supports bind_tools, like the ChatOpenAI main LLM does."""

    def bind_tools(self, tools, **kwargs):
        return self.bind(tools=[convert_to_openai_tool(tool) for tool in tools], **kwargs)


def make_tool(name: str):
    """Build a throwaway tool named ``name``, standing in for an MCP server tool."""

    @tool(name)
    def fake_tool() -> str:
        """A throwaway tool standing in for an MCP server tool."""
        return name

    return fake_tool


def capture_llm_messages(llm: FakeChatModel) -> list:
    """Spy on the fake model to record the messages of every stage LLM call."""
    calls: list = []

    def capture_generate(*args, **kwargs):
        calls.append(kwargs["messages"] if "messages" in kwargs else args[0])
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=llm.answer))])

    llm._generate = capture_generate
    return calls


@pytest.mark.asyncio
async def test_preprocessing_stage_runs_with_its_own_system_prompt():
    """Implements "the preprocessing stage runs with its own system prompt"
    (requirements/stages.feature)

    The preprocessing stage of a chat graph runs an LLM call on the
    question; the call carries the preprocessing system prompt as its
    system message.
    """
    llm = FakeChatModel(answer="the preprocessed question")
    stage = Stage(
        llm=llm,
        system_prompt="the preprocessing system prompt",
        user_prompt="the question is {question}",
    )
    calls = capture_llm_messages(llm)

    await stage.ainvoke({"question": "What is the weather like?"})

    assert [type(message).__name__ for message in calls[0]] == ["SystemMessage", "HumanMessage"]
    assert calls[0][0].content == "the preprocessing system prompt"


@pytest.mark.asyncio
async def test_postprocessing_stage_runs_with_its_own_system_prompt():
    """Implements "the postprocessing stage runs with its own system prompt"
    (requirements/stages.feature)

    The postprocessing stage of a chat graph runs an LLM call on the
    returned answer; the call carries the postprocessing system prompt as
    its system message.
    """
    llm = FakeChatModel(answer="the postprocessed answer")
    stage = Stage(
        llm=llm,
        system_prompt="the postprocessing system prompt",
        user_prompt="the returned answer is {answer}",
    )
    calls = capture_llm_messages(llm)

    await stage.ainvoke({"answer": "the returned answer"})

    assert [type(message).__name__ for message in calls[0]] == ["SystemMessage", "HumanMessage"]
    assert calls[0][0].content == "the postprocessing system prompt"


def test_stage_receives_the_tools_of_its_available_mcp_servers():
    """Implements "a stage receives the tools of its available MCP servers"
    (requirements/stages.feature)

    Given a stage whose available MCP servers provide tools, when the
    stage LLM is created, the stage LLM receives the tools of those
    available MCP servers.
    """
    llm = BindableFakeChatModel(answer="the stage answer")
    stage = Stage(
        llm=llm,
        system_prompt="the stage system prompt",
        user_prompt="the content is {content}",
        tools=[make_tool("the first stage tool"), make_tool("the second stage tool")],
    )

    created = stage.create_llm()

    assert created.bound is llm
    assert [entry["function"]["name"] for entry in created.kwargs["tools"]] == [
        "the first stage tool",
        "the second stage tool",
    ]


def test_a_system_one_model_limits_the_tools_available_to_the_stage_llm():
    """Implements "a SystemOne model limits the tools available to the stage LLM"
    (requirements/stages.feature)

    Given a stage with a configured SystemOne model, when the stage LLM is
    created, the stage LLM runs on the SystemOne model and the tools
    available to it are limited to the tools of the stage's available MCP
    servers.
    """
    llm = FakeChatModel(answer="the stage answer")
    system_one = SystemOneSettings(
        model="the system one model",
        base_url="http://the system one url",
        api_key="the system one api key",
    )
    stage = Stage(
        llm=llm,
        system_prompt="the stage system prompt",
        user_prompt="the content is {content}",
        tools=[make_tool("the stage tool")],
        system_one=system_one,
    )

    created = stage.create_llm()

    assert isinstance(created.bound, ChatOpenAI)
    assert created.bound.model == "the system one model"
    assert created.bound is not llm
    assert [entry["function"]["name"] for entry in created.kwargs["tools"]] == ["the stage tool"]


def test_the_system_one_model_is_optional():
    """Implements "the SystemOne model is optional"
    (requirements/stages.feature)

    A stage without a configured SystemOne model runs on the main LLM —
    both a stage given no SystemOne settings at all and a stage whose
    SystemOne settings configure no model.
    """
    llm = FakeChatModel(answer="the stage answer")
    without_settings = Stage(
        llm=llm,
        system_prompt="the stage system prompt",
        user_prompt="the content is {content}",
    )
    with_empty_settings = Stage(
        llm=llm,
        system_prompt="the stage system prompt",
        user_prompt="the content is {content}",
        system_one=SystemOneSettings(),
    )

    assert without_settings.create_llm() is llm
    assert with_empty_settings.create_llm() is llm
