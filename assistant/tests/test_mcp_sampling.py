# test_mcp_sampling.py
"""Unittests for mcp_sampling.py"""

from unittest.mock import AsyncMock, MagicMock

from mcp import types
import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from assistant.impl.mcp_sampling import (
    _convert_mcp_messages,
    _extract_text,
    create_sampling_callback,
)


class TestExtractText:
    def test_text_content(self):
        content = types.TextContent(type="text", text="hello")
        assert _extract_text(content) == "hello"

    def test_non_text_content(self):
        content = types.ImageContent(type="image", data="abc", mimeType="image/png")
        assert _extract_text(content) == ""

    def test_list_of_content_blocks(self):
        blocks = [
            types.TextContent(type="text", text="hello"),
            types.TextContent(type="text", text="world"),
        ]
        assert _extract_text(blocks) == "hello\nworld"


class TestConvertMcpMessages:
    def test_user_message(self):
        msgs = [types.SamplingMessage(role="user", content=types.TextContent(type="text", text="hi"))]
        result = _convert_mcp_messages(msgs)
        assert len(result) == 1
        assert isinstance(result[0], HumanMessage)
        assert result[0].content == "hi"

    def test_assistant_message(self):
        msgs = [types.SamplingMessage(role="assistant", content=types.TextContent(type="text", text="hello"))]
        result = _convert_mcp_messages(msgs)
        assert len(result) == 1
        assert isinstance(result[0], AIMessage)
        assert result[0].content == "hello"

    def test_mixed_messages(self):
        msgs = [
            types.SamplingMessage(role="user", content=types.TextContent(type="text", text="q")),
            types.SamplingMessage(role="assistant", content=types.TextContent(type="text", text="a")),
        ]
        result = _convert_mcp_messages(msgs)
        assert len(result) == 2
        assert isinstance(result[0], HumanMessage)
        assert isinstance(result[1], AIMessage)


class TestCreateSamplingCallback:
    @pytest.mark.asyncio
    async def test_successful_sampling(self):
        llm = AsyncMock()
        llm.ainvoke.return_value = MagicMock(content="LLM response")
        llm.model_name = "test-model"

        callback = create_sampling_callback(llm)
        context = MagicMock()
        params = types.CreateMessageRequestParams(
            messages=[types.SamplingMessage(role="user", content=types.TextContent(type="text", text="hello"))],
            maxTokens=100,
        )

        result = await callback(context, params)

        assert isinstance(result, types.CreateMessageResult)
        assert result.role == "assistant"
        assert result.content.text == "LLM response"
        assert result.model == "test-model"
        llm.ainvoke.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_sampling_with_system_prompt(self):
        llm = AsyncMock()
        llm.ainvoke.return_value = MagicMock(content="response")
        llm.model_name = "test-model"

        callback = create_sampling_callback(llm)
        context = MagicMock()
        params = types.CreateMessageRequestParams(
            messages=[types.SamplingMessage(role="user", content=types.TextContent(type="text", text="hello"))],
            maxTokens=100,
            systemPrompt="You are helpful.",
        )

        await callback(context, params)

        call_args = llm.ainvoke.call_args[0][0]
        assert isinstance(call_args[0], SystemMessage)
        assert call_args[0].content == "You are helpful."
        assert isinstance(call_args[1], HumanMessage)

    @pytest.mark.asyncio
    async def test_sampling_with_temperature_and_stop(self):
        llm = AsyncMock()
        llm.ainvoke.return_value = MagicMock(content="response")
        llm.model_name = "test-model"

        callback = create_sampling_callback(llm)
        context = MagicMock()
        params = types.CreateMessageRequestParams(
            messages=[types.SamplingMessage(role="user", content=types.TextContent(type="text", text="hello"))],
            maxTokens=50,
            temperature=0.5,
            stopSequences=["STOP"],
        )

        await callback(context, params)

        call_kwargs = llm.ainvoke.call_args[1]
        assert call_kwargs["max_tokens"] == 50
        assert call_kwargs["temperature"] == 0.5
        assert call_kwargs["stop"] == ["STOP"]

    @pytest.mark.asyncio
    async def test_sampling_error_handling(self):
        llm = AsyncMock()
        llm.ainvoke.side_effect = RuntimeError("LLM failed")

        callback = create_sampling_callback(llm)
        context = MagicMock()
        params = types.CreateMessageRequestParams(
            messages=[types.SamplingMessage(role="user", content=types.TextContent(type="text", text="hello"))],
            maxTokens=100,
        )

        result = await callback(context, params)

        assert isinstance(result, types.ErrorData)
        assert "LLM failed" in result.message

    @pytest.mark.asyncio
    async def test_sampling_falls_back_to_model_attr(self):
        llm = AsyncMock()
        llm.ainvoke.return_value = MagicMock(content="response")
        del llm.model_name
        llm.model = "ollama-model"

        callback = create_sampling_callback(llm)
        context = MagicMock()
        params = types.CreateMessageRequestParams(
            messages=[types.SamplingMessage(role="user", content=types.TextContent(type="text", text="hello"))],
            maxTokens=100,
        )

        result = await callback(context, params)

        assert result.model == "ollama-model"

    @pytest.mark.asyncio
    async def test_sampling_falls_back_to_unknown_model(self):
        llm = AsyncMock()
        llm.ainvoke.return_value = MagicMock(content="response")
        del llm.model_name
        del llm.model

        callback = create_sampling_callback(llm)
        context = MagicMock()
        params = types.CreateMessageRequestParams(
            messages=[types.SamplingMessage(role="user", content=types.TextContent(type="text", text="hello"))],
            maxTokens=100,
        )

        result = await callback(context, params)

        assert result.model == "unknown"

    @pytest.mark.asyncio
    async def test_sampling_with_zero_temperature(self):
        """temperature=0 is falsy but should still be passed to the LLM."""
        llm = AsyncMock()
        llm.ainvoke.return_value = MagicMock(content="response")
        llm.model_name = "test-model"

        callback = create_sampling_callback(llm)
        context = MagicMock()
        params = types.CreateMessageRequestParams(
            messages=[types.SamplingMessage(role="user", content=types.TextContent(type="text", text="hello"))],
            maxTokens=100,
            temperature=0,
        )

        await callback(context, params)

        call_kwargs = llm.ainvoke.call_args[1]
        assert call_kwargs["temperature"] == 0

    @pytest.mark.asyncio
    async def test_sampling_with_non_string_content(self):
        """When response.content is not a string, it should be converted via str()."""
        llm = AsyncMock()
        llm.ainvoke.return_value = MagicMock(content=["chunk1", "chunk2"])
        llm.model_name = "test-model"

        callback = create_sampling_callback(llm)
        context = MagicMock()
        params = types.CreateMessageRequestParams(
            messages=[types.SamplingMessage(role="user", content=types.TextContent(type="text", text="hello"))],
            maxTokens=100,
        )

        result = await callback(context, params)

        assert isinstance(result, types.CreateMessageResult)
        assert result.content.text == "['chunk1', 'chunk2']"
