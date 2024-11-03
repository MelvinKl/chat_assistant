# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import StrictStr
from typing import Any, List
from openapi_server.models.chat_response import ChatResponse
from openapi_server.models.key_value import KeyValue


class BaseComponentApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseComponentApi.subclasses = BaseComponentApi.subclasses + (cls,)
    async def assist(
        self,
        body: StrictStr,
    ) -> ChatResponse:
        ...


    async def get_description(
        self,
    ) -> List[KeyValue]:
        ...


    async def upload_document(
        self,
    ) -> None:
        ...
