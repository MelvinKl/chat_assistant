"""Unit tests for chat_api.py"""

from unittest.mock import AsyncMock

import pytest

from assistant.impl.apis.chat_api import ChatApi
from assistant.models.chat_completion_messages import ChatCompletionMessages
from assistant.models.chat_completion_request import ChatCompletionRequest


@pytest.fixture
def mock_chat_graph():
    """Mock ChatGraph for testing."""
    mock_graph = AsyncMock()
    mock_graph.ainvoke = AsyncMock(return_value="Test response")
    return mock_graph


@pytest.fixture
def chat_api(mock_chat_graph):
    """Create ChatApi instance with mocked dependencies."""
    # Create instance without calling __init__ to avoid injection requirements
    api = ChatApi.__new__(ChatApi)
    api._chat_graph = mock_chat_graph
    return api


@pytest.mark.asyncio
async def test_chat_completions_basic_flow(chat_api, mock_chat_graph):
    """Test basic chat completion flow."""
    request = ChatCompletionRequest(
        model="test-model",
        messages=[
            ChatCompletionMessages(role="user", content="Hello"),
            ChatCompletionMessages(role="assistant", content="Hi there"),
        ],
    )

    # Call the internal implementation directly, bypassing the @inject.params decorator
    response = await chat_api.chat_completions(request, chat_graph=chat_api._chat_graph)

    assert response.model == "test-model"
    assert response.object == "chat.completion"
    assert len(response.choices) == 1
    assert response.choices[0].message.content == "Test response"
    assert response.choices[0].message.role == "assistant"
    assert response.choices[0].finish_reason == "stop"


@pytest.mark.asyncio
async def test_chat_completions_converts_messages_to_history(chat_api, mock_chat_graph):
    """Test that messages are correctly converted to history tuples."""
    request = ChatCompletionRequest(
        model="test-model",
        messages=[
            ChatCompletionMessages(role="user", content="What is 2+2?"),
            ChatCompletionMessages(role="assistant", content="It is 4"),
            ChatCompletionMessages(role="user", content="And 3+3?"),
        ],
    )

    response = await chat_api.chat_completions(request, chat_graph=chat_api._chat_graph)

    # Verify that graph was called with correct history format
    mock_chat_graph.ainvoke.assert_awaited_once()
    call_args = mock_chat_graph.ainvoke.call_args[0][0]
    assert call_args == [
        ("user", "What is 2+2?"),
        ("assistant", "It is 4"),
        ("user", "And 3+3?"),
    ]


@pytest.mark.asyncio
async def test_chat_completions_returns_valid_response_structure(chat_api):
    """Test that response has all required fields."""
    request = ChatCompletionRequest(
        model="test-model",
        messages=[ChatCompletionMessages(role="user", content="Test")],
    )

    response = await chat_api.chat_completions(request, chat_graph=chat_api._chat_graph)

    # Check required fields
    assert hasattr(response, "id")
    assert response.id is not None
    assert len(response.id) > 0
    assert hasattr(response, "created")
    assert response.created > 0
    assert hasattr(response, "usage")
    assert response.usage.prompt_tokens == 0
    assert response.usage.completion_tokens == 0
    assert response.usage.total_tokens == 0


@pytest.mark.asyncio
async def test_chat_completions_with_single_message(chat_api):
    """Test chat completion with single message."""
    request = ChatCompletionRequest(
        model="test-model",
        messages=[ChatCompletionMessages(role="user", content="Hello")],
    )

    response = await chat_api.chat_completions(request, chat_graph=chat_api._chat_graph)

    assert response.model == "test-model"
    assert len(response.choices) == 1
    assert response.choices[0].index == 0
