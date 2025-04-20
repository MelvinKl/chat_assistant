# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import Field, StrictInt, StrictStr, field_validator  # noqa: F401
from typing import List, Optional  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from assistant.models.assistant_object import AssistantObject  # noqa: F401
from assistant.models.create_assistant_request import CreateAssistantRequest  # noqa: F401
from assistant.models.create_message_request import CreateMessageRequest  # noqa: F401
from assistant.models.create_run_request import CreateRunRequest  # noqa: F401
from assistant.models.create_thread_and_run_request import CreateThreadAndRunRequest  # noqa: F401
from assistant.models.create_thread_request import CreateThreadRequest  # noqa: F401
from assistant.models.delete_assistant_response import DeleteAssistantResponse  # noqa: F401
from assistant.models.delete_message_response import DeleteMessageResponse  # noqa: F401
from assistant.models.delete_thread_response import DeleteThreadResponse  # noqa: F401
from assistant.models.list_assistants_response import ListAssistantsResponse  # noqa: F401
from assistant.models.list_messages_response import ListMessagesResponse  # noqa: F401
from assistant.models.list_run_steps_response import ListRunStepsResponse  # noqa: F401
from assistant.models.list_runs_response import ListRunsResponse  # noqa: F401
from assistant.models.message_object import MessageObject  # noqa: F401
from assistant.models.modify_assistant_request import ModifyAssistantRequest  # noqa: F401
from assistant.models.modify_message_request import ModifyMessageRequest  # noqa: F401
from assistant.models.modify_run_request import ModifyRunRequest  # noqa: F401
from assistant.models.modify_thread_request import ModifyThreadRequest  # noqa: F401
from assistant.models.run_object import RunObject  # noqa: F401
from assistant.models.run_step_object import RunStepObject  # noqa: F401
from assistant.models.submit_tool_outputs_run_request import SubmitToolOutputsRunRequest  # noqa: F401
from assistant.models.thread_object import ThreadObject  # noqa: F401


def test_cancel_run(client: TestClient):
    """Test case for cancel_run

    Cancels a run that is `in_progress`.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/threads/{thread_id}/runs/{run_id}/cancel".format(thread_id='thread_id_example', run_id='run_id_example'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_create_assistant(client: TestClient):
    """Test case for create_assistant

    Create an assistant with a model and instructions.
    """
    create_assistant_request = {"reasoning_effort":"medium","top_p":1,"instructions":"instructions","tool_resources":{"code_interpreter":{"file_ids":["file_ids","file_ids","file_ids","file_ids","file_ids"]},"file_search":{"vector_store_ids":["vector_store_ids"],"vector_stores":[{"chunking_strategy":{"type":"auto"},"metadata":{"key":"metadata"},"file_ids":["file_ids","file_ids","file_ids","file_ids","file_ids"]}]}},"metadata":{"key":"metadata"},"response_format":"auto","name":"name","temperature":1,"description":"description","model":"gpt-4o","tools":[{"type":"code_interpreter"},{"type":"code_interpreter"},{"type":"code_interpreter"},{"type":"code_interpreter"},{"type":"code_interpreter"}]}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/assistants",
    #    headers=headers,
    #    json=create_assistant_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_create_message(client: TestClient):
    """Test case for create_message

    Create a message.
    """
    create_message_request = {"metadata":{"key":"metadata"},"role":"user","attachments":[{"file_id":"file_id","tools":[{"type":"code_interpreter"},{"type":"code_interpreter"}]},{"file_id":"file_id","tools":[{"type":"code_interpreter"},{"type":"code_interpreter"}]}],"content":"CreateMessageRequest_content"}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/threads/{thread_id}/messages".format(thread_id='thread_id_example'),
    #    headers=headers,
    #    json=create_message_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_create_run(client: TestClient):
    """Test case for create_run

    Create a run.
    """
    create_run_request = {"reasoning_effort":"medium","instructions":"instructions","additional_instructions":"additional_instructions","metadata":{"key":"metadata"},"assistant_id":"assistant_id","additional_messages":[{"metadata":{"key":"metadata"},"role":"user","attachments":[{"file_id":"file_id","tools":[{"type":"code_interpreter"},{"type":"code_interpreter"}]},{"file_id":"file_id","tools":[{"type":"code_interpreter"},{"type":"code_interpreter"}]}],"content":"CreateMessageRequest_content"},{"metadata":{"key":"metadata"},"role":"user","attachments":[{"file_id":"file_id","tools":[{"type":"code_interpreter"},{"type":"code_interpreter"}]},{"file_id":"file_id","tools":[{"type":"code_interpreter"},{"type":"code_interpreter"}]}],"content":"CreateMessageRequest_content"}],"tools":[{"type":"code_interpreter"},{"type":"code_interpreter"},{"type":"code_interpreter"},{"type":"code_interpreter"},{"type":"code_interpreter"}],"truncation_strategy":{"last_messages":1,"type":"auto"},"top_p":1,"max_completion_tokens":256,"response_format":"auto","parallel_tool_calls":1,"stream":1,"temperature":1,"tool_choice":{},"model":"gpt-4o","max_prompt_tokens":256}
    params = [("include", ['include_example'])]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/threads/{thread_id}/runs".format(thread_id='thread_id_example'),
    #    headers=headers,
    #    json=create_run_request,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_create_thread(client: TestClient):
    """Test case for create_thread

    Create a thread.
    """
    create_thread_request = {"tool_resources":{"code_interpreter":{"file_ids":["file_ids","file_ids","file_ids","file_ids","file_ids"]},"file_search":{"vector_store_ids":["vector_store_ids"],"vector_stores":[{"chunking_strategy":{"type":"auto"},"metadata":{"key":"metadata"},"file_ids":["file_ids","file_ids","file_ids","file_ids","file_ids"]}]}},"metadata":{"key":"metadata"},"messages":[{"metadata":{"key":"metadata"},"role":"user","attachments":[{"file_id":"file_id","tools":[{"type":"code_interpreter"},{"type":"code_interpreter"}]},{"file_id":"file_id","tools":[{"type":"code_interpreter"},{"type":"code_interpreter"}]}],"content":"CreateMessageRequest_content"},{"metadata":{"key":"metadata"},"role":"user","attachments":[{"file_id":"file_id","tools":[{"type":"code_interpreter"},{"type":"code_interpreter"}]},{"file_id":"file_id","tools":[{"type":"code_interpreter"},{"type":"code_interpreter"}]}],"content":"CreateMessageRequest_content"}]}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/threads",
    #    headers=headers,
    #    json=create_thread_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_create_thread_and_run(client: TestClient):
    """Test case for create_thread_and_run

    Create a thread and run it in one request.
    """
    create_thread_and_run_request = {"instructions":"instructions","tool_resources":{"code_interpreter":{"file_ids":["file_ids","file_ids","file_ids","file_ids","file_ids"]},"file_search":{"vector_store_ids":["vector_store_ids"]}},"metadata":{"key":"metadata"},"assistant_id":"assistant_id","thread":{"tool_resources":{"code_interpreter":{"file_ids":["file_ids","file_ids","file_ids","file_ids","file_ids"]},"file_search":{"vector_store_ids":["vector_store_ids"],"vector_stores":[{"chunking_strategy":{"type":"auto"},"metadata":{"key":"metadata"},"file_ids":["file_ids","file_ids","file_ids","file_ids","file_ids"]}]}},"metadata":{"key":"metadata"},"messages":[{"metadata":{"key":"metadata"},"role":"user","attachments":[{"file_id":"file_id","tools":[{"type":"code_interpreter"},{"type":"code_interpreter"}]},{"file_id":"file_id","tools":[{"type":"code_interpreter"},{"type":"code_interpreter"}]}],"content":"CreateMessageRequest_content"},{"metadata":{"key":"metadata"},"role":"user","attachments":[{"file_id":"file_id","tools":[{"type":"code_interpreter"},{"type":"code_interpreter"}]},{"file_id":"file_id","tools":[{"type":"code_interpreter"},{"type":"code_interpreter"}]}],"content":"CreateMessageRequest_content"}]},"tools":[{"type":"code_interpreter"},{"type":"code_interpreter"},{"type":"code_interpreter"},{"type":"code_interpreter"},{"type":"code_interpreter"}],"truncation_strategy":{"last_messages":1,"type":"auto"},"top_p":1,"max_completion_tokens":256,"response_format":"auto","parallel_tool_calls":1,"stream":1,"temperature":1,"tool_choice":{},"model":"gpt-4o","max_prompt_tokens":256}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/threads/runs",
    #    headers=headers,
    #    json=create_thread_and_run_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_delete_assistant(client: TestClient):
    """Test case for delete_assistant

    Delete an assistant.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "DELETE",
    #    "/assistants/{assistant_id}".format(assistant_id='assistant_id_example'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_delete_message(client: TestClient):
    """Test case for delete_message

    Deletes a message.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "DELETE",
    #    "/threads/{thread_id}/messages/{message_id}".format(thread_id='thread_id_example', message_id='message_id_example'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_delete_thread(client: TestClient):
    """Test case for delete_thread

    Delete a thread.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "DELETE",
    #    "/threads/{thread_id}".format(thread_id='thread_id_example'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_get_assistant(client: TestClient):
    """Test case for get_assistant

    Retrieves an assistant.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/assistants/{assistant_id}".format(assistant_id='assistant_id_example'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_get_message(client: TestClient):
    """Test case for get_message

    Retrieve a message.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/threads/{thread_id}/messages/{message_id}".format(thread_id='thread_id_example', message_id='message_id_example'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_get_run(client: TestClient):
    """Test case for get_run

    Retrieves a run.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/threads/{thread_id}/runs/{run_id}".format(thread_id='thread_id_example', run_id='run_id_example'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_get_run_step(client: TestClient):
    """Test case for get_run_step

    Retrieves a run step.
    """
    params = [("include", ['include_example'])]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/threads/{thread_id}/runs/{run_id}/steps/{step_id}".format(thread_id='thread_id_example', run_id='run_id_example', step_id='step_id_example'),
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_get_thread(client: TestClient):
    """Test case for get_thread

    Retrieves a thread.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/threads/{thread_id}".format(thread_id='thread_id_example'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_list_assistants(client: TestClient):
    """Test case for list_assistants

    Returns a list of assistants.
    """
    params = [("limit", 20),     ("order", desc),     ("after", 'after_example'),     ("before", 'before_example')]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/assistants",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_list_messages(client: TestClient):
    """Test case for list_messages

    Returns a list of messages for a given thread.
    """
    params = [("limit", 20),     ("order", desc),     ("after", 'after_example'),     ("before", 'before_example'),     ("run_id", 'run_id_example')]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/threads/{thread_id}/messages".format(thread_id='thread_id_example'),
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_list_run_steps(client: TestClient):
    """Test case for list_run_steps

    Returns a list of run steps belonging to a run.
    """
    params = [("limit", 20),     ("order", desc),     ("after", 'after_example'),     ("before", 'before_example'),     ("include", ['include_example'])]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/threads/{thread_id}/runs/{run_id}/steps".format(thread_id='thread_id_example', run_id='run_id_example'),
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_list_runs(client: TestClient):
    """Test case for list_runs

    Returns a list of runs belonging to a thread.
    """
    params = [("limit", 20),     ("order", desc),     ("after", 'after_example'),     ("before", 'before_example')]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/threads/{thread_id}/runs".format(thread_id='thread_id_example'),
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_modify_assistant(client: TestClient):
    """Test case for modify_assistant

    Modifies an assistant.
    """
    modify_assistant_request = {"reasoning_effort":"medium","top_p":1,"instructions":"instructions","tool_resources":{"code_interpreter":{"file_ids":["file_ids","file_ids","file_ids","file_ids","file_ids"]},"file_search":{"vector_store_ids":["vector_store_ids"]}},"metadata":{"key":"metadata"},"response_format":"auto","name":"name","temperature":1,"description":"description","model":"ModifyAssistantRequest_model","tools":[{"type":"code_interpreter"},{"type":"code_interpreter"},{"type":"code_interpreter"},{"type":"code_interpreter"},{"type":"code_interpreter"}]}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/assistants/{assistant_id}".format(assistant_id='assistant_id_example'),
    #    headers=headers,
    #    json=modify_assistant_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_modify_message(client: TestClient):
    """Test case for modify_message

    Modifies a message.
    """
    modify_message_request = {"metadata":{"key":"metadata"}}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/threads/{thread_id}/messages/{message_id}".format(thread_id='thread_id_example', message_id='message_id_example'),
    #    headers=headers,
    #    json=modify_message_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_modify_run(client: TestClient):
    """Test case for modify_run

    Modifies a run.
    """
    modify_run_request = {"metadata":{"key":"metadata"}}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/threads/{thread_id}/runs/{run_id}".format(thread_id='thread_id_example', run_id='run_id_example'),
    #    headers=headers,
    #    json=modify_run_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_modify_thread(client: TestClient):
    """Test case for modify_thread

    Modifies a thread.
    """
    modify_thread_request = {"tool_resources":{"code_interpreter":{"file_ids":["file_ids","file_ids","file_ids","file_ids","file_ids"]},"file_search":{"vector_store_ids":["vector_store_ids"]}},"metadata":{"key":"metadata"}}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/threads/{thread_id}".format(thread_id='thread_id_example'),
    #    headers=headers,
    #    json=modify_thread_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_submit_tool_ouputs_to_run(client: TestClient):
    """Test case for submit_tool_ouputs_to_run

    When a run has the `status: \"requires_action\"` and `required_action.type` is `submit_tool_outputs`, this endpoint can be used to submit the outputs from the tool calls once they're all completed. All outputs must be submitted in a single request. 
    """
    submit_tool_outputs_run_request = {"stream":1,"tool_outputs":[{"output":"output","tool_call_id":"tool_call_id"},{"output":"output","tool_call_id":"tool_call_id"}]}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/threads/{thread_id}/runs/{run_id}/submit_tool_outputs".format(thread_id='thread_id_example', run_id='run_id_example'),
    #    headers=headers,
    #    json=submit_tool_outputs_run_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

