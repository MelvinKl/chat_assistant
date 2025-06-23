# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import StrictInt, StrictStr, field_validator  # noqa: F401
from typing import Optional  # noqa: F401
from assistant.models.admin_api_key import AdminApiKey  # noqa: F401
from assistant.models.admin_api_keys_create_request import AdminApiKeysCreateRequest  # noqa: F401
from assistant.models.admin_api_keys_delete200_response import AdminApiKeysDelete200Response  # noqa: F401
from assistant.models.api_key_list import ApiKeyList  # noqa: F401


def test_admin_api_keys_create(client: TestClient):
    """Test case for admin_api_keys_create

    Create an organization admin API key
    """
    admin_api_keys_create_request = assistant.AdminApiKeysCreateRequest()

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    # response = client.request(
    #    "POST",
    #    "/organization/admin_api_keys",
    #    headers=headers,
    #    json=admin_api_keys_create_request,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_admin_api_keys_delete(client: TestClient):
    """Test case for admin_api_keys_delete

    Delete an organization admin API key
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    # response = client.request(
    #    "DELETE",
    #    "/organization/admin_api_keys/{key_id}".format(key_id='key_id_example'),
    #    headers=headers,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_admin_api_keys_get(client: TestClient):
    """Test case for admin_api_keys_get

    Retrieve a single organization API key
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    # response = client.request(
    #    "GET",
    #    "/organization/admin_api_keys/{key_id}".format(key_id='key_id_example'),
    #    headers=headers,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_admin_api_keys_list(client: TestClient):
    """Test case for admin_api_keys_list

    List organization API keys
    """
    params = [("after", "after_example"), ("order", asc), ("limit", 20)]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    # response = client.request(
    #    "GET",
    #    "/organization/admin_api_keys",
    #    headers=headers,
    #    params=params,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200
