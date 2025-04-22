# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from assistant.apis.models_api_base import BaseModelsApi
import assistant.impl.apis

import assistant.impl.apis
from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)

from assistant.models.extra_models import TokenModel  # noqa: F401
from pydantic import Field, StrictStr
from typing_extensions import Annotated
from assistant.models.delete_model_response import DeleteModelResponse
from assistant.models.list_models_response import ListModelsResponse
from assistant.models.model import Model


router = APIRouter()

ns_pkg = assistant.impl.apis
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.delete(
    "/models/{model}",
    responses={
        200: {"model": DeleteModelResponse, "description": "OK"},
    },
    tags=["Models"],
    summary="Delete a fine-tuned model. You must have the Owner role in your organization to delete a model.",
    response_model_by_alias=True,
)
async def delete_model(
    model: Annotated[StrictStr, Field(description="The model to delete")] = Path(..., description="The model to delete"),

) -> DeleteModelResponse:
    if not BaseModelsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseModelsApi.subclasses[0]().delete_model(model)


@router.get(
    "/models",
    responses={
        200: {"model": ListModelsResponse, "description": "OK"},
    },
    tags=["Models"],
    summary="Lists the currently available models, and provides basic information about each one such as the owner and availability.",
    response_model_by_alias=True,
)
async def list_models(

) -> ListModelsResponse:
    if not BaseModelsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseModelsApi.subclasses[0]().list_models()


@router.get(
    "/models/{model}",
    responses={
        200: {"model": Model, "description": "OK"},
    },
    tags=["Models"],
    summary="Retrieves a model instance, providing basic information about the model such as the owner and permissioning.",
    response_model_by_alias=True,
)
async def retrieve_model(
    model: Annotated[StrictStr, Field(description="The ID of the model to use for this request")] = Path(..., description="The ID of the model to use for this request"),

) -> Model:
    if not BaseModelsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseModelsApi.subclasses[0]().retrieve_model(model)
