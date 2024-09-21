# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from fastapi import File, UploadFile

from base_component_api.models.chat_response import ChatResponse
from base_component_api.models.key_value import KeyValue


class BaseComponentApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseComponentApi.subclasses = BaseComponentApi.subclasses + (cls,)
    async def act(
        self,
        body: str,
    ) -> str:
        ...


    async def answer_question(
        self,
        body: str,
    ) -> ChatResponse:
        ...


    async def get_available_actions(
        self,
    ) -> List[KeyValue]:
        ...


    async def upload_document(
        self,
        file: UploadFile = File(...)
    ) -> None:
        ...
