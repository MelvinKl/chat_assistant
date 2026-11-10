"""Unit tests for assistant_api.py"""

from unittest.mock import patch

from fastapi.testclient import TestClient
from pydantic import StrictStr

from assistant.apis.assistant_api_base import BaseAssistantApi


class FirstAssistApi(BaseAssistantApi):
    """A test implementation of the base assistant API, registered first."""

    async def assist(self, body: StrictStr) -> str:
        return "first: " + body


class SecondAssistApi(BaseAssistantApi):
    """A test implementation of the base assistant API, registered second."""

    async def assist(self, body: StrictStr) -> str:
        return "second: " + body


def test_assist(client: TestClient):
    """Implements "the assist endpoint accepts a plain text body"
    (requirements/assist-api.feature)
    """
    body = "body example"
    response = client.post("/assist", json=body)
    assert response.status_code == 200
    # The body is dispatched to the registered assistant implementation —
    # the first entry of the base API registry, which this module registered.
    assert BaseAssistantApi.subclasses[0] is FirstAssistApi
    assert response.json() == f"first: {body}"


def test_assist_no_registered_implementation(client: TestClient):
    """Implements "the endpoint responds not implemented without a registered implementation"
    (requirements/assist-api.feature)
    """
    with patch.object(BaseAssistantApi, "subclasses", ()):
        response = client.post("/assist", json="body example")
    assert response.status_code == 500
    assert response.json()["detail"] == "Not implemented"


def test_implementations_register_themselves_through_the_base_api():
    """Implements "implementations register themselves through the base API"
    (requirements/assist-api.feature)
    """
    # Both implementation classes are defined in this module: importing the
    # module ran their class statements, each of which appended the class to
    # the base API registry through __init_subclass__.
    assert FirstAssistApi in BaseAssistantApi.subclasses
    assert SecondAssistApi in BaseAssistantApi.subclasses


def test_assist_delegates_to_the_first_registered_implementation(client: TestClient):
    """Implements "the endpoint delegates to the first registered implementation"
    (requirements/assist-api.feature)
    """
    body = "body example"
    with patch.object(BaseAssistantApi, "subclasses", (FirstAssistApi, SecondAssistApi)):
        response = client.post("/assist", json=body)
    assert response.status_code == 200
    # Two implementations are registered in import order; the endpoint
    # delegates the body to the first of them.
    assert response.json() == f"first: {body}"
