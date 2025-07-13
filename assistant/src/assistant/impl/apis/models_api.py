from http.client import HTTPException

from pydantic import Field, StrictStr
from typing_extensions import Annotated

from assistant.apis.models_api_base import BaseModelsApi
from assistant.models.delete_model_response import DeleteModelResponse
from assistant.models.list_models_response import ListModelsResponse
from assistant.models.model import Model


class ModelsApi(BaseModelsApi):

    model = Model(id="chat_assistant", created=0, owned_by="No one. This model is a free spirit", object="model")

    async def list_models(
        self,
    ) -> ListModelsResponse:
        return ListModelsResponse(data=[self.model])

    async def retrieve_model(
        self,
        model: Annotated[StrictStr, Field(description="The ID of the model to use for this request")],
    ) -> Model:
        return self.model
