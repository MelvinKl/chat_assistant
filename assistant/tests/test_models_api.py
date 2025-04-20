# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import Field, StrictStr  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from assistant.models.delete_model_response import DeleteModelResponse  # noqa: F401
from assistant.models.list_models_response import ListModelsResponse  # noqa: F401
from assistant.models.model import Model  # noqa: F401


def test_delete_model(client: TestClient):
    """Test case for delete_model

    Delete a fine-tuned model. You must have the Owner role in your organization to delete a model.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "DELETE",
    #    "/models/{model}".format(model='ft:gpt-4o-mini:acemeco:suffix:abc123'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_list_models(client: TestClient):
    """Test case for list_models

    Lists the currently available models, and provides basic information about each one such as the owner and availability.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/models",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_retrieve_model(client: TestClient):
    """Test case for retrieve_model

    Retrieves a model instance, providing basic information about the model such as the owner and permissioning.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/models/{model}".format(model='gpt-4o-mini'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

