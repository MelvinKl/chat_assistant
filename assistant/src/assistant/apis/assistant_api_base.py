# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import StrictStr
from typing import Any


class BaseAssistantApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseAssistantApi.subclasses = BaseAssistantApi.subclasses + (cls,)
    async def assist(
        self,
        body: StrictStr,
    ) -> str:
        ...
