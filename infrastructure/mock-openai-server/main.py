"""
Mock OpenAI-compatible server for testing

This is a lightweight mock server that implements the OpenAI chat completions API
for testing purposes without requiring a full LLM backend.
"""

import logging
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


class Message(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str
    messages: list[Message]
    temperature: float | None = 0.7
    max_tokens: int | None = 100
    stream: bool | None = False


class ChatCompletionResponseChoice(BaseModel):
    index: int
    message: Message
    finish_reason: str


class ChatCompletionResponseUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: list[ChatCompletionResponseChoice]
    usage: ChatCompletionResponseUsage


class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str


class ModelsResponse(BaseModel):
    object: str = "list"
    data: list[ModelInfo]


def generate_mock_response(messages: list[Message]) -> str:
    """Generate a mock response based on the last user message."""
    if not messages:
        return "Hello! How can I help you?"

    last_message = messages[-1]
    if last_message.role == "user":
        content = last_message.content.lower()
        if "weather" in content:
            return "The weather is sunny and 22°C."
        elif "time" in content:
            return "The current time is 12:00 PM."
        elif "hello" in content or "hi" in content:
            return "Hello! How can I assist you today?"
        else:
            return f"I received your message: {last_message.content}. This is a mock response for testing."
    else:
        return "I understand. How can I help you further?"


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest) -> ChatCompletionResponse:
    """Handle chat completion requests."""
    logger.info(f"Received chat completion request for model: {request.model}")

    response_content = generate_mock_response(request.messages)

    return ChatCompletionResponse(
        id="chatcmpl-mock-123456",
        created=1234567890,
        model=request.model,
        choices=[
            ChatCompletionResponseChoice(
                index=0,
                message=Message(role="assistant", content=response_content),
                finish_reason="stop",
            )
        ],
        usage=ChatCompletionResponseUsage(
            prompt_tokens=len(" ".join(m.content for m in request.messages)),
            completion_tokens=len(response_content),
            total_tokens=len(" ".join(m.content for m in request.messages))
            + len(response_content),
        ),
    )


@app.get("/v1/models")
async def list_models() -> ModelsResponse:
    """List available models."""
    return ModelsResponse(
        data=[
            ModelInfo(id="qwen3:4b", created=1234567890, owned_by="mock"),
            ModelInfo(id="mock-model", created=1234567890, owned_by="mock"),
        ]
    )


@app.get("/v1/models/{model_id}")
async def get_model(model_id: str) -> ModelInfo:
    """Get a specific model."""
    if model_id in ["qwen3:4b", "mock-model"]:
        return ModelInfo(id=model_id, created=1234567890, owned_by="mock")
    raise HTTPException(status_code=404, detail="Model not found")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/")
async def root():
    """Root endpoint with server info."""
    return {
        "name": "mock-openai-server",
        "version": "1.0.0",
        "description": "Mock OpenAI-compatible Server for Testing",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=11434)
