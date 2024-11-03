# coding: utf-8

from typing import Any, ClassVar, Dict, List, Tuple  # noqa: F401

from fastapi import UploadFile
from pydantic import StrictStr

from base_component_api.models.chat_response import ChatResponse
from base_component_api.models.description import Description


class BaseComponentApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseComponentApi.subclasses = BaseComponentApi.subclasses + (cls,)

    async def assist(
        self,
        body: StrictStr,
    ) -> ChatResponse: ...

    async def get_description(
        self,
    ) -> Description: ...

    async def upload_document(
        self,
        file: UploadFile,
    ) -> None: ...
