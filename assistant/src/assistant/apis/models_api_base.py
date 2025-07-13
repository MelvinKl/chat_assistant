# coding: utf-8

from typing import ClassVar

from pydantic import Field, StrictStr
from typing_extensions import Annotated

from assistant.models.delete_model_response import DeleteModelResponse
from assistant.models.list_models_response import ListModelsResponse
from assistant.models.model import Model


class BaseModelsApi:
    subclasses: ClassVar[tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseModelsApi.subclasses = BaseModelsApi.subclasses + (cls,)

    async def list_models(
        self,
    ) -> ListModelsResponse: ...

    async def retrieve_model(
        self,
        model: Annotated[StrictStr, Field(description="The ID of the model to use for this request")],
    ) -> Model: ...
