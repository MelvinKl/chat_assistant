# Task: Extended health check

Task Number: 245
Branch: ai/issue-245-extended-health-check

## Required Task

Add a setting that will cause the programm to exit with an error when a defined tool is not available.
The health Check should also make Sure all configured tools are still available.
If at least one of the configured mcp servers does not respond with a tool the health check should fail.

## Steps

- [x] 1. Add a `strict_tool_check` boolean setting to `MCPSettings` in `assistant/src/assistant/impl/settings/mcp_server_settings.py`.
  - Acceptance Criteria:
    - A new field `strict_tool_check: bool = False` is added to `MCPSettings` class.
    - The field is documented and can be set via `SETTINGS_MCP_STRICT_TOOL_CHECK` environment variable.
    - Existing tests in `assistant/tests/test_settings.py` continue to pass.

- [x] 2. Implement startup validation in `assistant/src/assistant/assistant_container.py` that exits with error when `strict_tool_check` is enabled and a configured tool is unavailable.
  - Acceptance Criteria:
    - Modify `_get_mcp_tools()` to track servers that return no tools or error as `failed_servers`.
    - In `_di_config()`, after calling `_get_mcp_tools()`, if `settings_mcp.strict_tool_check` is `True` and any `failed_servers` exist, log error with failed server names and raise `SystemExit(1)`.
    - If `strict_tool_check` is `False`, log warnings for failed servers but continue normally.
    - The validation runs during application startup in the dependency injection setup.

- [ ] 3. Extend the health check endpoints in `assistant/src/assistant/endpoints/health_endpoints.py` to verify all configured MCP servers respond with at least one tool.
  - Acceptance Criteria:
    - Add `_check_mcp_servers_tool_availability()` async function that queries each configured MCP server via `MultiServerMCPClient` and `await mcp_client.get_tools()`.
    - Update `GET /health` endpoint to call `_check_mcp_servers_tool_availability()` and return HTTP 503 with `{"status": "unhealthy", "failed_servers": [...]}` if any server fails to provide tools.
    - Update `GET /readiness` endpoint similarly to return HTTP 503 with `{"status": "not ready", "failed_servers": [...]}` if any server fails.
    - If all servers return tools, both endpoints return HTTP 200 with appropriate success status.
    - Properly clean up MCP client connections after tool availability checks.

- [ ] 4. Add tests for the strict tool check setting and extended health check behavior in `assistant/tests/`.
  - Acceptance Criteria:
    - Tests in `assistant/tests/test_settings.py` verify `strict_tool_check` field defaults to `False` and can be set via `SETTINGS_MCP_STRICT_TOOL_CHECK` environment variable.
    - Tests in `assistant/tests/test_health_endpoints.py` verify:
      - `/health` returns 200 when all MCP servers provide tools.
      - `/health` returns 503 when an MCP server provides no tools.
      - `/readiness` returns 200 when all servers provide tools and 503 when any server fails.
    - Tests verify startup behavior:
      - Application exits with code 1 when `strict_tool_check=True` and an MCP server returns no tools.
      - Application continues normally when `strict_tool_check=False` and an MCP server returns no tools.

- [ ] 5. Run `make test` and confirm it succeeds.
  - Acceptance Criteria:
    - `make test` exits successfully with no failures.
