# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import Field, StrictInt, StrictStr, field_validator  # noqa: F401
from typing import Dict, Optional  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from assistant.models.chat_completion_deleted import ChatCompletionDeleted  # noqa: F401
from assistant.models.chat_completion_list import ChatCompletionList  # noqa: F401
from assistant.models.chat_completion_message_list import ChatCompletionMessageList  # noqa: F401
from assistant.models.create_chat_completion_request import CreateChatCompletionRequest  # noqa: F401
from assistant.models.create_chat_completion_response import CreateChatCompletionResponse  # noqa: F401
from assistant.models.update_chat_completion_request import UpdateChatCompletionRequest  # noqa: F401


def test_create_chat_completion(client: TestClient):
    """Test case for create_chat_completion

    **Starting a new project?** We recommend trying [Responses](/docs/api-reference/responses)  to take advantage of the latest OpenAI platform features. Compare [Chat Completions with Responses](/docs/guides/responses-vs-chat-completions?api-mode=responses).  ---  Creates a model response for the given chat conversation. Learn more in the [text generation](/docs/guides/text-generation), [vision](/docs/guides/vision), and [audio](/docs/guides/audio) guides.  Parameter support can differ depending on the model used to generate the response, particularly for newer reasoning models. Parameters that are only supported for reasoning models are noted below. For the current state of  unsupported parameters in reasoning models,  [refer to the reasoning guide](/docs/guides/reasoning).
    """
    create_chat_completion_request = {
        "reasoning_effort": "medium",
        "top_logprobs": 11,
        "metadata": {"key": "metadata"},
        "logit_bias": {"key": 5},
        "seed": 7,
        "functions": [
            {"name": "name", "description": "description", "parameters": {"key": ""}},
            {"name": "name", "description": "description", "parameters": {"key": ""}},
            {"name": "name", "description": "description", "parameters": {"key": ""}},
            {"name": "name", "description": "description", "parameters": {"key": ""}},
            {"name": "name", "description": "description", "parameters": {"key": ""}},
        ],
        "function_call": "none",
        "presence_penalty": -1.413674807798822,
        "tools": [
            {
                "function": {"name": "name", "description": "description", "strict": 0, "parameters": {"key": ""}},
                "type": "function",
            },
            {
                "function": {"name": "name", "description": "description", "strict": 0, "parameters": {"key": ""}},
                "type": "function",
            },
        ],
        "web_search_options": {
            "search_context_size": "medium",
            "user_location": {
                "approximate": {"country": "country", "city": "city", "timezone": "timezone", "region": "region"},
                "type": "approximate",
            },
        },
        "logprobs": 0,
        "top_p": 1,
        "max_completion_tokens": 0,
        "modalities": ["text", "text"],
        "frequency_penalty": 0.4109824732281613,
        "response_format": {"type": "text"},
        "stream": 0,
        "temperature": 1,
        "tool_choice": "none",
        "model": "gpt-4o",
        "service_tier": "auto",
        "audio": {"voice": "ash", "format": "wav"},
        "max_tokens": 2,
        "store": 0,
        "n": 1,
        "stop": "\n",
        "prediction": {"type": "content", "content": "PredictionContent_content"},
        "messages": [
            {"role": "developer", "name": "name", "content": "ChatCompletionRequestDeveloperMessage_content"},
            {"role": "developer", "name": "name", "content": "ChatCompletionRequestDeveloperMessage_content"},
        ],
        "stream_options": {"include_usage": 1},
        "user": "user-1234",
    }

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    # response = client.request(
    #    "POST",
    #    "/chat/completions",
    #    headers=headers,
    #    json=create_chat_completion_request,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_delete_chat_completion(client: TestClient):
    """Test case for delete_chat_completion

    Delete a stored chat completion. Only Chat Completions that have been created with the `store` parameter set to `true` can be deleted.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    # response = client.request(
    #    "DELETE",
    #    "/chat/completions/{completion_id}".format(completion_id='completion_id_example'),
    #    headers=headers,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_get_chat_completion(client: TestClient):
    """Test case for get_chat_completion

    Get a stored chat completion. Only Chat Completions that have been created with the `store` parameter set to `true` will be returned.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    # response = client.request(
    #    "GET",
    #    "/chat/completions/{completion_id}".format(completion_id='completion_id_example'),
    #    headers=headers,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_get_chat_completion_messages(client: TestClient):
    """Test case for get_chat_completion_messages

    Get the messages in a stored chat completion. Only Chat Completions that have been created with the `store` parameter set to `true` will be returned.
    """
    params = [("after", "after_example"), ("limit", 20), ("order", asc)]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    # response = client.request(
    #    "GET",
    #    "/chat/completions/{completion_id}/messages".format(completion_id='completion_id_example'),
    #    headers=headers,
    #    params=params,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_list_chat_completions(client: TestClient):
    """Test case for list_chat_completions

    List stored Chat Completions. Only Chat Completions that have been stored with the `store` parameter set to `true` will be returned.
    """
    params = [
        ("model", "model_example"),
        ("metadata", {"key": "metadata_example"}),
        ("after", "after_example"),
        ("limit", 20),
        ("order", asc),
    ]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    # response = client.request(
    #    "GET",
    #    "/chat/completions",
    #    headers=headers,
    #    params=params,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_update_chat_completion(client: TestClient):
    """Test case for update_chat_completion

    Modify a stored chat completion. Only Chat Completions that have been created with the `store` parameter set to `true` can be modified. Currently, the only supported modification is to update the `metadata` field.
    """
    update_chat_completion_request = assistant.UpdateChatCompletionRequest()

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    # response = client.request(
    #    "POST",
    #    "/chat/completions/{completion_id}".format(completion_id='completion_id_example'),
    #    headers=headers,
    #    json=update_chat_completion_request,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200
