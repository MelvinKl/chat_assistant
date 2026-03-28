# Task: Add mcp-sampling support for all attached MCP Servers.

Task Number: 208
Branch: ai/issue-208-add-mcp-sampling-support-for-a

## Required Task

The Chat Assistant should be able to provide an LLM via MCP sampling to an attached MCP Server.

## Steps

- [x] 1. Examine the current MCP client implementation to understand how to integrate sampling support.
  - Acceptance Criteria:
    - Identify where MCP clients are initialized in the codebase.
    - Determine the interface for providing a sampling callback to MCP clients.
    - Review the langchain_mcp_adapters documentation for sampling callback requirements.

- [ ] 2. Implement a sampling callback function that uses the assistant's LLM to handle sampling requests from MCP servers.
  - Acceptance Criteria:
    - Create a function that accepts MCP sampling parameters (messages, model preferences, etc.).
      - **Implementation location:** `assistant/src/assistant/impl/mcp_sampling.py` (create_sampling_callback function)
      - **Function signature:** `async def sampling_callback(context: RequestContext, params: types.CreateMessageRequestParams) -> types.CreateMessageResult | types.ErrorData`
      - **Parameters from params:** messages (list of SamplingMessage), systemPrompt (optional), maxTokens (optional), temperature (optional), stopSequences (optional)
    - The function must use the assistant's configured LLM (ChatOllama or ChatOpenAI) to generate responses.
      - Use `llm.ainvoke()` with converted LangChain message format (HumanMessage, AIMessage, SystemMessage)
      - Support temperature, maxTokens, and stopSequences kwargs
    - The function must handle errors gracefully and return appropriate MCP sampling responses.
      - Return `types.CreateMessageResult` on success with role, content (TextContent), and model name
      - Return `types.ErrorData` on failure with error code and message
    - The callback must be compatible with the MultiServerMCPClient sampling interface.
      - Uses langchain_mcp_adapters.client.MultiServerMCPClient for registration
      - Returns MCP protocol-compliant response objects

- [ ] 3. Modify the MCP client setup to register the sampling callback with all MCP server connections.
  - Acceptance Criteria:
    - Update the _get_mcp_tools function or MCP client initialization to include the sampling callback.
      - **File to modify:** `assistant/src/assistant/assistant_container.py` in `_get_mcp_tools()` function
      - **Integration point:** Create sampling callback by calling `create_sampling_callback(llm)` and pass it via `session_kwargs` dict
    - Ensure the callback is registered for every MCP server connection (both stdio and HTTP transports).
      - Add `session_kwargs = {"sampling_callback": sampling_callback}` before building server_dict
      - Include session_kwargs in both stdio transport config (command, args, transport) and HTTP transport config (url, transport)
      - Pass server_dict to `MultiServerMCPClient(server_dict)` constructor
    - Verify that the assistant's LLM is properly passed to the sampling callback.
      - Ensure `llm` parameter from _get_mcp_tools is passed to create_sampling_callback function
      - LLM should be the assistant's configured instance (ChatOllama or ChatOpenAI)
    - Confirm that existing MCP tool functionality remains unaffected.
      - Tool discovery and execution should continue to work as before
      - Sampling callback operates independently from tool invocation

- [ ] 4. Add tests to verify the sampling callback works correctly with different MCP server configurations.
  - Acceptance Criteria:
    - Write unit tests that simulate MCP sampling requests from servers.
      - **Test file location:** `assistant/tests/test_mcp_sampling.py`
      - Use mcp.types.CreateMessageRequestParams to construct test requests
      - Test with various message formats: user messages, assistant messages, mixed conversations
    - Test that the callback correctly invokes the assistant's LLM and returns formatted responses.
      - Verify successful sampling with system prompts (systemPrompt parameter)
      - Test temperature and stopSequences parameter passing to LLM
      - Verify maxTokens parameter is correctly applied
      - Confirm response contains role, content (TextContent), and model name fields
    - Test error handling when the LLM is unavailable or returns errors.
      - Mock LLM errors and verify ErrorData responses with appropriate error codes
      - Test graceful degradation scenarios
    - Ensure tests cover both stdio and HTTP transport scenarios.
      - Tests should be transport-agnostic since sampling_callback is registered at session level
      - Both transports use same session_kwargs mechanism

- [ ] 5. Run `make test` to verify all tests pass and no regressions are introduced.
  - Acceptance Criteria:
    - The `make test` command completes successfully.
      - Execute from project root directory
      - Runs linting checks and full test suite
    - All existing tests continue to pass.
      - MCP tool tests in `assistant/tests/test_assistant_container.py` should pass
      - Other assistant-related tests should pass
    - New tests for sampling functionality pass.
      - All tests in `assistant/tests/test_mcp_sampling.py` should pass
      - Verify specific test cases for message conversion, LLM invocation, error handling, and parameter handling