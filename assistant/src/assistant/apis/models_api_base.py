# coding: utf-8

from typing import ClassVar

from pydantic import Field, StrictStr
from typing_extensions import Annotated

from assistant.models.list_models_response import ListModelsResponse
from assistant.models.model import Model


class BaseModelsApi:
    """Base class for model API. OpenAI compatible."""

    subclasses: ClassVar[tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseModelsApi.subclasses = BaseModelsApi.subclasses + (cls,)

    async def list_models(
        self,
    ) -> ListModelsResponse:
        """
        Returns a list of available models.

        Returns
        -------
        ListModelsResponse: A response object containing the list of models.
        """

    async def retrieve_model(
        self,
        model: Annotated[StrictStr, Field(description="The ID of the model to use for this request")],
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
