# coding: utf-8
import logging

from mcp import types
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from mcp.shared.context import RequestContext

logger = logging.getLogger(__name__)


def _convert_mcp_messages(messages: list[types.SamplingMessage]) -> list[HumanMessage | AIMessage]:
    """Convert MCP SamplingMessages to LangChain message format."""
    result = []
    for msg in messages:
        text = _extract_text(msg.content)
        if msg.role == "user":
            result.append(HumanMessage(content=text))
        else:
            result.append(AIMessage(content=text))
    return result


def _extract_text(content: types.SamplingMessageContentBlock | list[types.SamplingMessageContentBlock]) -> str:
    """Extract text from MCP content block(s)."""
    if isinstance(content, list):
        return "\n".join(_extract_text(block) for block in content)
    if isinstance(content, types.TextContent):
        return content.text
    return ""


def create_sampling_callback(llm: BaseChatModel):
    """Create an MCP sampling callback that uses the given LLM."""

    async def sampling_callback(
        context: RequestContext,
        params: types.CreateMessageRequestParams,
    ) -> types.CreateMessageResult | types.ErrorData:
        try:
            messages = []
            if params.systemPrompt:
                messages.append(SystemMessage(content=params.systemPrompt))
            messages.extend(_convert_mcp_messages(params.messages))

            kwargs = {}
            if params.maxTokens:
                kwargs["max_tokens"] = params.maxTokens
            if params.temperature is not None:
                kwargs["temperature"] = params.temperature
            if params.stopSequences:
                kwargs["stop"] = params.stopSequences

            response = await llm.ainvoke(messages, **kwargs)
            response_text = response.content if isinstance(response.content, str) else str(response.content)

            return types.CreateMessageResult(
                role="assistant",
                content=types.TextContent(type="text", text=response_text),
                model=getattr(llm, "model_name", getattr(llm, "model", "unknown")),
            )
        except Exception as e:
            logger.error("MCP sampling callback error: %s", e)
            return types.ErrorData(
                code=types.INTERNAL_ERROR,
                message=str(e),
            )

    return sampling_callback
