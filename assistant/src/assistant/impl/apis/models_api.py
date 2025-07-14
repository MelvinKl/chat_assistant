from pydantic import Field, StrictStr
from typing_extensions import Annotated

from assistant.apis.models_api_base import BaseModelsApi
from assistant.models.list_models_response import ListModelsResponse
from assistant.models.model import Model


class ModelsApi(BaseModelsApi):
    """Implementation of OpenAI compatible models API for chat assistant."""

    model = Model(id="chat_assistant", created=0, owned_by="No one. This model is a free spirit", object="model")

    async def list_models(
        self,
    ) -> ListModelsResponse:
        """
        Returns a list of available models.

        Returns
        -------
        ListModelsResponse: A response object containing the list of models.
        """
        return ListModelsResponse(data=[self.model])

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
        return self.model
