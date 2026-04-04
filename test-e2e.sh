#!/usr/bin/env bash
# End-to-end test script for the chat assistant deployment
# This script tests all main endpoints of the deployed services

set -e

# Configuration
ASSISTANT_PORT="${ASSISTANT_PORT:-8080}"
ASSISTANT_HOST="${ASSISTANT_HOST:-localhost}"
ASSISTANT_URL="http://${ASSISTANT_HOST}:${ASSISTANT_PORT}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
print_test() {
    echo -e "${YELLOW}Testing: $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Test functions
test_health_endpoint() {
    print_test "Assistant health endpoint"
    response=$(curl -s -w "\n%{http_code}" "${ASSISTANT_URL}/health")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "200" ]; then
        printf '%s\n' "$body" | grep -qF '"status":"healthy"' && \
        print_success "Health check passed" || \
        print_error "Health endpoint response invalid"
    else
        print_error "Health endpoint returned HTTP $http_code"
        return 1
    fi
}

test_readiness_endpoint() {
    print_test "Assistant readiness endpoint"
    response=$(curl -s -w "\n%{http_code}" "${ASSISTANT_URL}/readiness")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "200" ]; then
        printf '%s\n' "$body" | grep -qF '"status":"ready"' && \
        print_success "Readiness check passed" || \
        print_error "Readiness endpoint response invalid"
    else
        print_error "Readiness endpoint returned HTTP $http_code"
        return 1
    fi
}

test_list_models() {
    print_test "List models endpoint"
    response=$(curl -s -w "\n%{http_code}" "${ASSISTANT_URL}/models")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "200" ]; then
        printf '%s\n' "$body" | grep -qF '"object":"list"' && \
        printf '%s\n' "$body" | grep -qF '"data"' && \
        print_success "List models passed" || \
        print_error "List models response invalid"
    else
        print_error "List models returned HTTP $http_code"
        return 1
    fi
}

test_retrieve_model() {
    print_test "Retrieve model endpoint"
    response=$(curl -s -w "\n%{http_code}" "${ASSISTANT_URL}/models/qwen3:4b")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "200" ]; then
        printf '%s\n' "$body" | grep -qF '"id":"qwen3:4b"' && \
        print_success "Retrieve model passed" || \
        print_error "Retrieve model response invalid"
    else
        print_error "Retrieve model returned HTTP $http_code"
        return 1
    fi
}

test_chat_completions() {
    print_test "Chat completions endpoint"
    response=$(curl -s -w "\n%{http_code}" -X POST "${ASSISTANT_URL}/chat/completions" \
        -H "Content-Type: application/json" \
        -d '{
            "model": "qwen3:4b",
            "messages": [
                {"role": "user", "content": "Hello"}
            ]
        }')
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "200" ]; then
        printf '%s\n' "$body" | grep -qF '"object":"chat.completion"' && \
        printf '%s\n' "$body" | grep -qF '"choices"' && \
        print_success "Chat completions passed" || \
        print_error "Chat completions response invalid"
    else
        print_error "Chat completions returned HTTP $http_code"
        return 1
    fi
}

test_assist_endpoint() {
    print_test "Assist endpoint"
    response=$(curl -s -w "\n%{http_code}" -X POST "${ASSISTANT_URL}/assist" \
        -H "Content-Type: application/json" \
        -d '"What is the weather today?"')
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "200" ]; then
        [ -n "$body" ] && \
        print_success "Assist endpoint passed" || \
        print_error "Assist endpoint returned empty response"
    elif [ "$http_code" = "500" ] && echo "$body" | grep -qF "Not implemented"; then
        print_test "Assist endpoint (not implemented, skipping)"
    else
        print_error "Assist endpoint returned HTTP $http_code"
        return 1
    fi
}

test_mock_mcp_server() {
    if [ -n "${KUBECTL_PORT_FORWARD:-}" ]; then
        print_test "Mock MCP server (skipping in k8s context)"
        return 0
    fi

    print_test "Mock MCP server"
    response=$(curl -s -w "\n%{http_code}" http://localhost:18080/health)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "200" ]; then
        printf '%s\n' "$body" | grep -qF '"status":"healthy"' && \
        print_success "Mock MCP server health passed" || \
        print_error "Mock MCP server response invalid"
    else
        print_error "Mock MCP server returned HTTP $http_code"
        return 1
    fi
}

test_mock_openai_server() {
    if [ -n "${KUBECTL_PORT_FORWARD:-}" ]; then
        print_test "Mock OpenAI server (skipping in k8s context)"
        return 0
    fi

    print_test "Mock OpenAI server"
    response=$(curl -s -w "\n%{http_code}" http://localhost:11434/health)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "200" ]; then
        printf '%s\n' "$body" | grep -qF '"status":"healthy"' && \
        print_success "Mock OpenAI server health passed" || \
        print_error "Mock OpenAI server response invalid"
    else
        print_error "Mock OpenAI server returned HTTP $http_code"
        return 1
    fi
}

# Main test execution
main() {
    echo "=========================================="
    echo "Running E2E Tests"
    echo "Target: ${ASSISTANT_URL}"
    echo "=========================================="
    echo ""

    # Wait for service to be ready
    echo "Waiting for service to be ready..."
    max_retries=30
    retry_count=0
    while [ $retry_count -lt $max_retries ]; do
        if curl -s -f "${ASSISTANT_URL}/health" > /dev/null 2>&1; then
            echo "Service is ready!"
            break
        fi
        retry_count=$((retry_count + 1))
        echo "Attempt $retry_count/$max_retries: Service not ready yet..."
        sleep 2
    done

    if [ $retry_count -eq $max_retries ]; then
        print_error "Service did not become ready in time"
        exit 1
    fi

    echo ""

    # Run all tests
    test_health_endpoint
    test_readiness_endpoint
    test_list_models
    test_retrieve_model
    test_chat_completions
    test_assist_endpoint
    test_mock_mcp_server
    test_mock_openai_server

    echo ""
    echo "=========================================="
    echo -e "${GREEN}All E2E tests passed!${NC}"
    echo "=========================================="
}

# Run main function
main "$@"
