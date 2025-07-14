import importlib
import pkgutil

from fastapi import APIRouter, HTTPException, Path
from pydantic import Field, StrictStr
from typing_extensions import Annotated

import assistant.impl.apis
from assistant.apis.models_api_base import BaseModelsApi
from assistant.models.list_models_response import ListModelsResponse
from assistant.models.model import Model

router = APIRouter()

ns_pkg = assistant.impl.apis
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/models",
    responses={
        200: {"model": ListModelsResponse, "description": "OK"},
    },
    tags=["Models"],
    summary="Lists the currently available models, and provides basic information about each one such as the owner and availability.",  # noqa: E501
    response_model_by_alias=True,
)
async def list_models() -> ListModelsResponse:
    """
    Returns a list of available models.

    Returns
    -------
    ListModelsResponse: A response object containing the list of models.
    """
    if not BaseModelsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseModelsApi.subclasses[0]().list_models()


@router.get(
    "/models/{model}",
    responses={
        200: {"model": Model, "description": "OK"},
    },
    tags=["Models"],
    summary="Retrieves a model instance, providing basic information about the model such as the owner and permissioning.",  # noqa: E501
    response_model_by_alias=True,
)
async def retrieve_model(
    model: Annotated[StrictStr, Field(description="The ID of the model to use for this request")] = Path(
        ..., description="The ID of the model to use for this request"
    ),
) -> Model:
    """
    Retrieves a model by its ID.

    Parameters
    ----------
    model (StrictStr): The ID of the model to retrieve.

    Returns
    -------
    Model: The model instance with the specified ID.
    """
    if not BaseModelsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseModelsApi.subclasses[0]().retrieve_model(model)
