"""Custom LLM tool selector middleware compatible with OpenRouter."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Annotated, Any, Literal, Union

from langchain.agents.middleware import LLMToolSelectorMiddleware
from pydantic import Field, TypeAdapter
from typing_extensions import TypedDict

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from langchain.tools import BaseTool

    from langchain.agents.middleware.types import (
        ContextT,
        ModelRequest,
        ModelResponse,
        ResponseT,
    )

logger = logging.getLogger(__name__)


class OpenRouterCompatibleToolSelector(LLMToolSelectorMiddleware):
    """Tool selector that uses function_calling instead of json_schema for OpenRouter compatibility."""

    async def awrap_model_call(
        self,
        request: "ModelRequest[ContextT]",
        handler: Callable[["ModelRequest[ContextT]"], Awaitable["ModelResponse[ResponseT]"]],
    ) -> "ModelResponse[ResponseT]":
        selection_request = self._prepare_selection_request(request)
        if selection_request is None:
            return await handler(request)

        type_adapter = self._create_tool_selection_response(selection_request.available_tools)
        schema = type_adapter.json_schema()
        structured_model = selection_request.model.with_structured_output(schema, method="function_calling")

        response = await structured_model.ainvoke(
            [
                {"role": "system", "content": selection_request.system_message},
                selection_request.last_user_message,
            ]
        )

        if not isinstance(response, dict):
            msg = f"Expected dict response, got {type(response)}"
            raise AssertionError(msg)

        modified_request = self._process_selection_response(
            response,
            selection_request.available_tools,
            selection_request.valid_tool_names,
            request,
        )
        return await handler(modified_request)

    def wrap_model_call(
        self,
        request: "ModelRequest[ContextT]",
        handler: Callable[["ModelRequest[ContextT]"], "ModelResponse[ResponseT]"],
    ) -> "ModelResponse[ResponseT]":
        selection_request = self._prepare_selection_request(request)
        if selection_request is None:
            return handler(request)

        type_adapter = self._create_tool_selection_response(selection_request.available_tools)
        schema = type_adapter.json_schema()
        structured_model = selection_request.model.with_structured_output(schema, method="function_calling")

        response = structured_model.invoke(
            [
                {"role": "system", "content": selection_request.system_message},
                selection_request.last_user_message,
            ]
        )

        if not isinstance(response, dict):
            msg = f"Expected dict response, got {type(response)}"
            raise AssertionError(msg)

        modified_request = self._process_selection_response(
            response,
            selection_request.available_tools,
            selection_request.valid_tool_names,
            request,
        )
        return handler(modified_request)

    @staticmethod
    def _create_tool_selection_response(tools: list["BaseTool"]) -> TypeAdapter[Any]:
        if not tools:
            msg = "Invalid usage: tools must be non-empty"
            raise AssertionError(msg)

        literals = [Annotated[Literal[tool.name], Field(description=tool.description)] for tool in tools]
        selected_tool_type = Union[tuple(literals)]  # type: ignore[valid-type]

        description = "Tools to use. Place the most relevant tools first."

        class ToolSelectionResponse(TypedDict):
            tools: Annotated[list[selected_tool_type], Field(description=description)]  # type: ignore[valid-type]

        return TypeAdapter(ToolSelectionResponse)
