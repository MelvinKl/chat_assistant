# Mock MCP Server

A lightweight mock MCP (Model Context Protocol) server for testing purposes.

## Purpose

This server provides a simple implementation of the MCP protocol for testing the chat assistant without requiring actual MCP server deployments.

## Features

- Implements MCP protocol over SSE (Server-Sent Events)
- Provides mock tools:
  - `get_weather`: Returns mock weather information
  - `get_time`: Returns mock time information
- No LLM backend required
- Fast and lightweight for CI/CD testing

## Running Locally

```bash
cd infrastructure/mock-mcp-server
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080
```

## Docker

```bash
docker build -f infrastructure/mock-mcp-server/Dockerfile -t mock-mcp-server .
docker run -p 8080:8080 mock-mcp-server
```

## Endpoints

- `GET /sse`: SSE endpoint for MCP communication
- `GET /health`: Health check
- `GET /`: Server information

## Usage in Tests

The mock MCP server is used in the GitHub Actions test pipeline to verify that the chat assistant can connect to and use MCP servers.

See `.github/workflows/test-pipeline.yml` for usage examples.
