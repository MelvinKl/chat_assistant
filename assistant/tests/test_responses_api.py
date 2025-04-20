# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import Field, StrictInt, StrictStr, field_validator  # noqa: F401
from typing import Any, List, Optional  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from assistant.models.create_response import CreateResponse  # noqa: F401
from assistant.models.error import Error  # noqa: F401
from assistant.models.includable import Includable  # noqa: F401
from assistant.models.response import Response  # noqa: F401
from assistant.models.response_item_list import ResponseItemList  # noqa: F401


def test_create_response(client: TestClient):
    """Test case for create_response

    Creates a model response. Provide [text](/docs/guides/text) or [image](/docs/guides/images) inputs to generate [text](/docs/guides/text) or [JSON](/docs/guides/structured-outputs) outputs. Have the model call your own [custom code](/docs/guides/function-calling) or use built-in [tools](/docs/guides/tools) like [web search](/docs/guides/tools-web-search) or [file search](/docs/guides/tools-file-search) to use your own data as input for the model's response. 
    """
    create_response = {"instructions":"instructions","include":["file_search_call.results","file_search_call.results"],"metadata":{"key":"metadata"},"reasoning":{"effort":"medium","generate_summary":"concise"},"store":1,"tools":[{"vector_store_ids":["vector_store_ids","vector_store_ids"],"max_num_results":6,"ranking_options":{"score_threshold":0.14658129805029452,"ranker":"auto"},"filters":{"type":"eq","value":"ComparisonFilter_value","key":"key"},"type":"file_search"},{"vector_store_ids":["vector_store_ids","vector_store_ids"],"max_num_results":6,"ranking_options":{"score_threshold":0.14658129805029452,"ranker":"auto"},"filters":{"type":"eq","value":"ComparisonFilter_value","key":"key"},"type":"file_search"}],"top_p":1,"input":"CreateResponse_allOf_input","previous_response_id":"previous_response_id","parallel_tool_calls":1,"stream":0,"temperature":1,"tool_choice":"none","model":"gpt-4o","text":{"format":{"type":"text"}},"user":"user-1234","truncation":"disabled","max_output_tokens":0}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/responses",
    #    headers=headers,
    #    json=create_response,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_delete_response(client: TestClient):
    """Test case for delete_response

    Deletes a model response with the given ID. 
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "DELETE",
    #    "/responses/{response_id}".format(response_id='resp_677efb5139a88190b512bc3fef8e535d'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_get_response(client: TestClient):
    """Test case for get_response

    Retrieves a model response with the given ID. 
    """
    params = [("include", [assistant.Includable()])]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/responses/{response_id}".format(response_id='resp_677efb5139a88190b512bc3fef8e535d'),
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_list_input_items(client: TestClient):
    """Test case for list_input_items

    Returns a list of input items for a given response.
    """
    params = [("limit", 20),     ("order", 'order_example'),     ("after", 'after_example'),     ("before", 'before_example')]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/responses/{response_id}/input_items".format(response_id='response_id_example'),
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

