# coding: utf-8

from fastapi.testclient import TestClient


from base_component_api.models.chat_response import ChatResponse  # noqa: F401
from base_component_api.models.key_value import KeyValue  # noqa: F401


def test_act(client: TestClient):
    """Test case for act"""
    body = "body_example"

    headers = {}
    # uncomment below to make a request
    # response = client.request(
    #    "POST",
    #    "/act",
    #    headers=headers,
    #    json=body,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_answer_question(client: TestClient):
    """Test case for answer_question"""
    body = "body_example"

    headers = {}
    # uncomment below to make a request
    # response = client.request(
    #    "POST",
    #    "/question",
    #    headers=headers,
    #    json=body,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_get_available_actions(client: TestClient):
    """Test case for get_available_actions"""

    headers = {}
    # uncomment below to make a request
    # response = client.request(
    #    "GET",
    #    "/availbale/actions",
    #    headers=headers,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_upload_document(client: TestClient):
    """Test case for upload_document"""

    headers = {}
    # uncomment below to make a request
    # response = client.request(
    #    "POST",
    #    "/documents",
    #    headers=headers,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200
