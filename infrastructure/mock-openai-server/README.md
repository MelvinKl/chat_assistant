# Mock OpenAI Server

A lightweight mock OpenAI-compatible server for testing purposes.

## Purpose

This server provides a simple implementation of the OpenAI chat completions API for testing the chat assistant without requiring actual LLM deployments like Ollama.

## Features

- OpenAI-compatible `/v1/chat/completions` endpoint
- `/v1/models` endpoint for listing models
- Simple mock responses based on input
- Fast and lightweight for CI/CD testing
- No GPU or large model downloads required

## Running Locally

```bash
cd infrastructure/mock-openai-server
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 11434
```

## Docker

```bash
docker build -f infrastructure/mock-openai-server/Dockerfile -t mock-openai-server .
docker run -p 11434:11434 mock-openai-server
```

## Endpoints

- `POST /v1/chat/completions`: OpenAI chat completions
- `GET /v1/models`: List available models
- `GET /v1/models/{model_id}`: Get specific model info
- `GET /health`: Health check
- `GET /`: Server information

## Usage in Tests

The mock OpenAI server is used in the GitHub Actions test pipeline to provide a fast, reliable LLM backend for testing.

See `.github/workflows/test-pipeline.yml` for usage examples.

## Decision: Mock OpenAI vs Ollama

For CI/CD testing, we chose to create a mock OpenAI server instead of using Ollama because:

1. **Speed**: No model downloads required, tests run faster
2. **Reliability**: Deterministic responses, no network dependencies
3. **Resource Efficiency**: Lower CPU/memory usage in CI/CD
4. **Simplicity**: No need to manage model files or GPU resources

For local development and production, Ollama (or other real LLM providers) should still be used.
