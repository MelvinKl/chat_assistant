# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import Field, StrictInt, StrictStr  # noqa: F401
from typing import List, Optional  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from assistant.models.user import User  # noqa: F401
from assistant.models.user_delete_response import UserDeleteResponse  # noqa: F401
from assistant.models.user_list_response import UserListResponse  # noqa: F401
from assistant.models.user_role_update_request import UserRoleUpdateRequest  # noqa: F401


def test_delete_user(client: TestClient):
    """Test case for delete_user

    Deletes a user from the organization.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "DELETE",
    #    "/organization/users/{user_id}".format(user_id='user_id_example'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_list_users(client: TestClient):
    """Test case for list_users

    Lists all of the users in the organization.
    """
    params = [("limit", 20),     ("after", 'after_example'),     ("emails", ['emails_example'])]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/organization/users",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_modify_user(client: TestClient):
    """Test case for modify_user

    Modifies a user's role in the organization.
    """
    user_role_update_request = {"role":"owner"}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/organization/users/{user_id}".format(user_id='user_id_example'),
    #    headers=headers,
    #    json=user_role_update_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_retrieve_user(client: TestClient):
    """Test case for retrieve_user

    Retrieves a user by their identifier.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/organization/users/{user_id}".format(user_id='user_id_example'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

