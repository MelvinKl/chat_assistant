"""Unit tests for models_api.py"""

import pytest

from assistant.impl.apis.models_api import ModelsApi


@pytest.fixture
def models_api():
    """Create ModelsApi instance."""
    return ModelsApi()


@pytest.mark.asyncio
async def test_list_models(models_api):
    """Test list models endpoint."""
    response = await models_api.list_models()

    assert hasattr(response, "data")
    assert isinstance(response.data, list)
    assert len(response.data) > 0
    assert response.object == "list"


@pytest.mark.asyncio
async def test_list_models_contains_expected_fields(models_api):
    """Test that returned models have required fields."""
    response = await models_api.list_models()

    model = response.data[0]
    assert hasattr(model, "id")
    assert hasattr(model, "created")
    assert hasattr(model, "object")
    assert hasattr(model, "owned_by")
    assert model.object == "model"


@pytest.mark.asyncio
async def test_retrieve_model(models_api):
    """Test retrieve model endpoint."""
    response = await models_api.retrieve_model("any-model-id")

    assert response.id == "any-model-id"
    assert response.object == "model"
    assert len(response.owned_by) > 0


@pytest.mark.asyncio
async def test_retrieve_model_ignores_input_id(models_api):
    """Test that retrieve model returns model with input ID."""
    response1 = await models_api.retrieve_model("model-1")
    response2 = await models_api.retrieve_model("model-2")

    assert response1.id == "model-1"
    assert response2.id == "model-2"
