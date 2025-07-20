"""
Unit-tests for the Rephraser runnable.

Run with e.g.:

    $ pytest tests/test_rephraser.py -vv

"""

import pytest

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.outputs import ChatGeneration, ChatResult

from assistant.impl.rephraser.rephraser import Rephraser
from ..fake_chat_model import FakeChatModel



@pytest.fixture
def dummy_llm():
    return FakeChatModel(answer="re-phrased!")


@pytest.fixture
def simple_rephraser(dummy_llm):
    return Rephraser(
        llm=dummy_llm,
        system_prompt="System: {system_context}",
        user_prompt="User: {user_question}",
    )


def test_rephraser_initialisation():
    """Sanity that construction populates expected private attributes."""
    llm = FakeChatModel(answer="foo")
    r = Rephraser(
        llm=llm,
        system_prompt="SYS: {val}",
        user_prompt="USR: {question}",
    )

    assert r._llm is llm
    expected_template = "SYS: {val}\nUSR: {question}"  # ChatPromptTemplate formats this in order
    actual_str = str(r._prompt_template.messages)
    assert "SYS: {val}" in actual_str
    assert "USR: {question}" in actual_str


@pytest.mark.asyncio
async def test_ainvoke_basic_flow(simple_rephraser):
    """Exercises the async path."""
    state = {"system_context": "ctx", "user_question": "how are you?"}
    answer = await simple_rephraser.ainvoke(state)

    assert answer == "re-phrased!"


def test_invoke_basic_flow(simple_rephraser):
    """Ensure invoke delegates to ainvoke via asyncio.run()."""
    state = {"system_context": "ctx", "user_question": "what is life?"}
    answer = simple_rephraser.invoke(state)

    assert answer == "re-phrased!"


@pytest.mark.asyncio
async def test_ainvoke_passes_kwargs_through(simple_rephraser):
    """Check that extra kwargs wind up in the LLM call."""
    fake_llm = simple_rephraser._llm  # type: ignore[attr-defined]
    config = RunnableConfig(tags=["test"])
    await simple_rephraser.ainvoke(
        {"system_context": "x", "user_question": "y"},
        config=config,
        temperature=0.5,
        max_tokens=128,
    )

    # Our fake captures the kwargs for the last call
    assert fake_llm.kwargs_history
    kwargs = fake_llm.kwargs_history[-1]
    assert kwargs["temperature"] == 0.5
    assert kwargs["max_tokens"] == 128


@pytest.mark.asyncio
async def test_prompt_rendering_includes_state():
    """Assert that the constructed prompt contains the variables from the state dict."""
    llm = FakeChatModel(answer="answer")

    # We can spy on _generate to see the formatted messages
    calls = []

    def capture_generate(*a, **kw):
        calls.append(a[0] if "messages" not in kw.keys() else kw["messages"])
        gen = ChatGeneration(message=AIMessage(content="answer"))
        return ChatResult(generations=[gen])

    llm._generate = capture_generate

    r = Rephraser(llm, system_prompt="sys({var})", user_prompt="user({msg})")
    await r.ainvoke({"var": "test_var", "msg": "hello"})

    msgs = calls[0]
    sys_msg = msgs[0]
    user_msg = msgs[1]

    assert sys_msg.content == "sys(test_var)"
    assert user_msg.content == "user(hello)"


def test_mandatory_state_parameters_are_fulfilled():
    """If PromptTemplate requires fields missing in state, expect KeyError on invoke."""
    llm = FakeChatModel(answer="ok")
    r = Rephraser(llm, system_prompt="{a}", user_prompt="{b}")

    with pytest.raises(KeyError, match=r".*(a|b).*"):
        r.invoke({})


# ------------------------------------------------------------
# Test running the file itself (quick smoke test)
# ------------------------------------------------------------
if __name__ == "__main__":
    pytest.main([__file__, "-v"])