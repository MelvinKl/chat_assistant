# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import Field, StrictInt, StrictStr  # noqa: F401
from typing import Optional  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from assistant.models.invite import Invite  # noqa: F401
from assistant.models.invite_delete_response import InviteDeleteResponse  # noqa: F401
from assistant.models.invite_list_response import InviteListResponse  # noqa: F401
from assistant.models.invite_request import InviteRequest  # noqa: F401


def test_delete_invite(client: TestClient):
    """Test case for delete_invite

    Delete an invite. If the invite has already been accepted, it cannot be deleted.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    # response = client.request(
    #    "DELETE",
    #    "/organization/invites/{invite_id}".format(invite_id='invite_id_example'),
    #    headers=headers,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_invite_user(client: TestClient):
    """Test case for invite_user

    Create an invite for a user to the organization. The invite must be accepted by the user before they have access to the organization.
    """
    invite_request = {
        "role": "reader",
        "projects": [{"role": "member", "id": "id"}, {"role": "member", "id": "id"}],
        "email": "email",
    }

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    # response = client.request(
    #    "POST",
    #    "/organization/invites",
    #    headers=headers,
    #    json=invite_request,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_list_invites(client: TestClient):
    """Test case for list_invites

    Returns a list of invites in the organization.
    """
    params = [("limit", 20), ("after", "after_example")]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    # response = client.request(
    #    "GET",
    #    "/organization/invites",
    #    headers=headers,
    #    params=params,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_retrieve_invite(client: TestClient):
    """Test case for retrieve_invite

    Retrieves an invite.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    # response = client.request(
    #    "GET",
    #    "/organization/invites/{invite_id}".format(invite_id='invite_id_example'),
    #    headers=headers,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200
