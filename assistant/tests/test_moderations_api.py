# coding: utf-8

from fastapi.testclient import TestClient


from assistant.models.create_moderation_request import CreateModerationRequest  # noqa: F401
from assistant.models.create_moderation_response import CreateModerationResponse  # noqa: F401


def test_create_moderation(client: TestClient):
    """Test case for create_moderation

    Classifies if text and/or image inputs are potentially harmful. Learn more in the [moderation guide](/docs/guides/moderation). 
    """
    create_moderation_request = {"input":"I want to kill them.","model":"omni-moderation-2024-09-26"}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/moderations",
    #    headers=headers,
    #    json=create_moderation_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

