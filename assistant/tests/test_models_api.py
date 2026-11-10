"""Unit tests for models_api.py"""

from unittest.mock import patch

import pytest

from assistant.apis.models_api_base import BaseModelsApi
from assistant.impl.apis.models_api import ModelsApi


@pytest.fixture
def models_api():
    """Create ModelsApi instance."""
    return ModelsApi()


@pytest.mark.asyncio
async def test_list_models(models_api):
    """Test list models endpoint.

    Implements "listing the available models"
    (requirements/models-api.feature)
    """
    response = await models_api.list_models()

    assert hasattr(response, "data")
    assert isinstance(response.data, list)
    assert len(response.data) > 0
    assert response.object == "list"


@pytest.mark.asyncio
async def test_list_models_contains_expected_fields(models_api):
    """Test that returned models have required fields.

    Implements "every listed model carries the model fields"
    (requirements/models-api.feature)
    """
    response = await models_api.list_models()

    model = response.data[0]
    assert hasattr(model, "id")
    assert hasattr(model, "created")
    assert hasattr(model, "object")
    assert hasattr(model, "owned_by")
    assert model.object == "model"


@pytest.mark.asyncio
async def test_retrieve_model(models_api):
    """Test retrieve model endpoint.

    Implements "retrieving a model by id"
    (requirements/models-api.feature)
    """
    response = await models_api.retrieve_model("any-model-id")

    assert response.id == "chat_assistant"
    assert response.object == "model"
    assert len(response.owned_by) > 0


@pytest.mark.asyncio
async def test_retrieve_model_ignores_input_id(models_api):
    """Test that retrieve model returns same model regardless of input.

    Implements "retrieving any model id returns the same assistant model"
    (requirements/models-api.feature)
    """
    response1 = await models_api.retrieve_model("model-1")
    response2 = await models_api.retrieve_model("model-2")

    assert response1.id == response2.id


########################################################################################
# Endpoint-level tests against the assistant application
########################################################################################
def test_models_api_no_registered_implementation(client):
    """Implements "no models API implementation is registered"
    (requirements/models-api.feature)
    """
    with patch.object(BaseModelsApi, "subclasses", ()):
        response = client.get("/models")
    assert response.status_code == 500
    assert response.json()["detail"] == "Not implemented"
