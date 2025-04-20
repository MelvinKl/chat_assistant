# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import Field, StrictBool, StrictInt, StrictStr, field_validator  # noqa: F401
from typing import List, Optional  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from assistant.models.usage_response import UsageResponse  # noqa: F401


def test_usage_audio_speeches(client: TestClient):
    """Test case for usage_audio_speeches

    Get audio speeches usage details for the organization.
    """
    params = [("start_time", 56),     ("end_time", 56),     ("bucket_width", 1d),     ("project_ids", ['project_ids_example']),     ("user_ids", ['user_ids_example']),     ("api_key_ids", ['api_key_ids_example']),     ("models", ['models_example']),     ("group_by", ['group_by_example']),     ("limit", 56),     ("page", 'page_example')]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/organization/usage/audio_speeches",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_usage_audio_transcriptions(client: TestClient):
    """Test case for usage_audio_transcriptions

    Get audio transcriptions usage details for the organization.
    """
    params = [("start_time", 56),     ("end_time", 56),     ("bucket_width", 1d),     ("project_ids", ['project_ids_example']),     ("user_ids", ['user_ids_example']),     ("api_key_ids", ['api_key_ids_example']),     ("models", ['models_example']),     ("group_by", ['group_by_example']),     ("limit", 56),     ("page", 'page_example')]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/organization/usage/audio_transcriptions",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_usage_code_interpreter_sessions(client: TestClient):
    """Test case for usage_code_interpreter_sessions

    Get code interpreter sessions usage details for the organization.
    """
    params = [("start_time", 56),     ("end_time", 56),     ("bucket_width", 1d),     ("project_ids", ['project_ids_example']),     ("group_by", ['group_by_example']),     ("limit", 56),     ("page", 'page_example')]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/organization/usage/code_interpreter_sessions",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_usage_completions(client: TestClient):
    """Test case for usage_completions

    Get completions usage details for the organization.
    """
    params = [("start_time", 56),     ("end_time", 56),     ("bucket_width", 1d),     ("project_ids", ['project_ids_example']),     ("user_ids", ['user_ids_example']),     ("api_key_ids", ['api_key_ids_example']),     ("models", ['models_example']),     ("batch", True),     ("group_by", ['group_by_example']),     ("limit", 56),     ("page", 'page_example')]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/organization/usage/completions",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_usage_costs(client: TestClient):
    """Test case for usage_costs

    Get costs details for the organization.
    """
    params = [("start_time", 56),     ("end_time", 56),     ("bucket_width", 1d),     ("project_ids", ['project_ids_example']),     ("group_by", ['group_by_example']),     ("limit", 7),     ("page", 'page_example')]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/organization/costs",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_usage_embeddings(client: TestClient):
    """Test case for usage_embeddings

    Get embeddings usage details for the organization.
    """
    params = [("start_time", 56),     ("end_time", 56),     ("bucket_width", 1d),     ("project_ids", ['project_ids_example']),     ("user_ids", ['user_ids_example']),     ("api_key_ids", ['api_key_ids_example']),     ("models", ['models_example']),     ("group_by", ['group_by_example']),     ("limit", 56),     ("page", 'page_example')]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/organization/usage/embeddings",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_usage_images(client: TestClient):
    """Test case for usage_images

    Get images usage details for the organization.
    """
    params = [("start_time", 56),     ("end_time", 56),     ("bucket_width", 1d),     ("sources", ['sources_example']),     ("sizes", ['sizes_example']),     ("project_ids", ['project_ids_example']),     ("user_ids", ['user_ids_example']),     ("api_key_ids", ['api_key_ids_example']),     ("models", ['models_example']),     ("group_by", ['group_by_example']),     ("limit", 56),     ("page", 'page_example')]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/organization/usage/images",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_usage_moderations(client: TestClient):
    """Test case for usage_moderations

    Get moderations usage details for the organization.
    """
    params = [("start_time", 56),     ("end_time", 56),     ("bucket_width", 1d),     ("project_ids", ['project_ids_example']),     ("user_ids", ['user_ids_example']),     ("api_key_ids", ['api_key_ids_example']),     ("models", ['models_example']),     ("group_by", ['group_by_example']),     ("limit", 56),     ("page", 'page_example')]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/organization/usage/moderations",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_usage_vector_stores(client: TestClient):
    """Test case for usage_vector_stores

    Get vector stores usage details for the organization.
    """
    params = [("start_time", 56),     ("end_time", 56),     ("bucket_width", 1d),     ("project_ids", ['project_ids_example']),     ("group_by", ['group_by_example']),     ("limit", 56),     ("page", 'page_example')]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/organization/usage/vector_stores",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

