# Task: Add mcp-sampling support for all attached MCP Servers.

Task Number: 208
Branch: ai/issue-208-add-mcp-sampling-support-for-a

## Required Task

The Chat Assistant should be able to provide an LLM via MCP sampling to an attached MCP Server.

## Steps

- [ ] 1. Examine the current MCP client implementation to understand how to integrate sampling support.
  - Acceptance Criteria:
    - Identify where MCP clients are initialized in the codebase.
    - Determine the interface for providing a sampling callback to MCP clients.
    - Review the langchain_mcp_adapters documentation for sampling callback requirements.

- [ ] 2. Implement a sampling callback function that uses the assistant's LLM to handle sampling requests from MCP servers.
  - Acceptance Criteria:
    - Create a function that accepts MCP sampling parameters (messages, model preferences, etc.).
    - The function must use the assistant's configured LLM (ChatOllama or ChatOpenAI) to generate responses.
    - The function must handle errors gracefully and return appropriate MCP sampling responses.
    - The callback must be compatible with the MultiServerMCPClient sampling interface.

- [ ] 3. Modify the MCP client setup to register the sampling callback with all MCP server connections.
  - Acceptance Criteria:
    - Update the _get_mcp_tools function or MCP client initialization to include the sampling callback.
    - Ensure the callback is registered for every MCP server connection (both stdio and HTTP transports).
    - Verify that the assistant's LLM is properly passed to the sampling callback.
    - Confirm that existing MCP tool functionality remains unaffected.

- [ ] 4. Add tests to verify the sampling callback works correctly with different MCP server configurations.
  - Acceptance Criteria:
    - Write unit tests that simulate MCP sampling requests from servers.
    - Test that the callback correctly invokes the assistant's LLM and returns formatted responses.
    - Test error handling when the LLM is unavailable or returns errors.
    - Ensure tests cover both stdio and HTTP transport scenarios.

- [ ] 5. Run `make test` to verify all tests pass and no regressions are introduced.
  - Acceptance Criteria:
    - The `make test` command completes successfully.
    - All existing tests continue to pass.
    - New tests for sampling functionality pass.