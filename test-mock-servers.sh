#!/bin/bash
# Test script to verify mock servers work correctly

set -e

echo "=== Testing Mock MCP Server ==="
echo "Starting mock MCP server..."
cd infrastructure/mock-mcp-server
python -m venv .venv
source .venv/bin/activate
pip install -q -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 18080 &
MCP_PID=$!
cd ../..

echo "Waiting for mock MCP server to start..."
sleep 3

echo "Testing MCP health endpoint..."
curl -f http://localhost:18080/health || {
    echo "MCP health check failed"
    kill $MCP_PID 2>/dev/null || true
    exit 1
}

echo "Testing MCP root endpoint..."
curl -f http://localhost:18080/ || {
    echo "MCP root endpoint failed"
    kill $MCP_PID 2>/dev/null || true
    exit 1
}

echo "Mock MCP server tests passed!"
kill $MCP_PID 2>/dev/null || true

echo ""
echo "=== Testing Mock OpenAI Server ==="
echo "Starting mock OpenAI server..."
cd infrastructure/mock-openai-server
python -m venv .venv
source .venv/bin/activate
pip install -q -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 11434 &
OPENAI_PID=$!
cd ../..

echo "Waiting for mock OpenAI server to start..."
sleep 3

echo "Testing OpenAI health endpoint..."
curl -f http://localhost:11434/health || {
    echo "OpenAI health check failed"
    kill $OPENAI_PID 2>/dev/null || true
    exit 1
}

echo "Testing OpenAI models endpoint..."
curl -f http://localhost:11434/v1/models || {
    echo "OpenAI models endpoint failed"
    kill $OPENAI_PID 2>/dev/null || true
    exit 1
}

echo "Testing OpenAI chat completions endpoint..."
curl -f -X POST http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3:4b",
    "messages": [
      {"role": "user", "content": "Hello"}
    ]
  }' || {
    echo "OpenAI chat completions endpoint failed"
    kill $OPENAI_PID 2>/dev/null || true
    exit 1
}

echo "Mock OpenAI server tests passed!"
kill $OPENAI_PID 2>/dev/null || true

echo ""
echo "=== All mock server tests passed! ==="
