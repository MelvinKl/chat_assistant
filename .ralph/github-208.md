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

- [x] 2. Implement a sampling callback function that uses the assistant's LLM to handle sampling requests from MCP servers.
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
      - **Integration point:** Import `create_sampling_callback` from `assistant.impl.mcp_sampling`
      - **Callback creation:** Call `sampling_callback = create_sampling_callback(context, llm)` to instantiate the callback with RequestContext and LLM instance
      - **Registration:** Pass `sampling_callback` via `session_kwargs = {"sampling_callback": sampling_callback}` dict
    - Ensure the callback is registered for every MCP server connection (both stdio and HTTP transports).
      - Add `session_kwargs = {"sampling_callback": sampling_callback}` before building server_dict
      - Pass `session_kwargs` to `MultiServerMCPClient(server_dict, session_kwargs=session_kwargs)` constructor
      - The MultiServerMCPClient will automatically register the callback with each MCP server session
    - Verify that the assistant's LLM is properly passed to the sampling callback.
      - The `context` parameter should be the RequestContext from the method signature
      - The `llm` parameter should be the assistant's configured instance (ChatOllama or ChatOpenAI)
      - Confirm the callback receives both parameters to handle sampling requests with proper context
    - Confirm that existing MCP tool functionality remains unaffected.
      - Tool discovery and execution should continue to work as before
      - Sampling callback operates independently from tool invocation
      - Verify that no changes to tool-related logic are needed

- [ ] 4. Add tests to verify the sampling callback works correctly with different MCP server configurations.
  - Acceptance Criteria:
    - Write unit tests that simulate MCP sampling requests from servers.
      - **Test file location:** `assistant/tests/test_mcp_sampling.py`
      - Import `create_sampling_callback` from `assistant.impl.mcp_sampling`
      - Use `mcp.types.CreateMessageRequestParams` with `messages` list and optional `systemPrompt`, `maxTokens`, `temperature`, `stopSequences`
      - Use `mcp.types.SamplingMessage` to construct message objects with `role` (user/assistant) and `content` fields
      - Test with various message formats: single user message, assistant messages, mixed multi-turn conversations
    - Test that the callback correctly invokes the assistant's LLM and returns formatted responses.
      - Mock the LLM using unittest.mock.AsyncMock to simulate `llm.ainvoke()` calls
      - Verify callback returns `types.CreateMessageResult` with `role="assistant"`, `content` (TextContent), and `model` fields
      - Verify system prompt is passed to LLM when provided via `systemPrompt` parameter
      - Test temperature parameter is passed as kwargs to `llm.ainvoke()`
      - Test maxTokens parameter is passed as kwargs to `llm.ainvoke()`
      - Test stopSequences parameter is passed as kwargs to `llm.ainvoke()`
      - Confirm TextContent object contains the LLM-generated response text
    - Test error handling when the LLM is unavailable or returns errors.
      - Mock LLM to raise exceptions and verify callback returns `types.ErrorData`
      - Verify ErrorData contains appropriate error code and error message
      - Test with various exception types (ValueError, timeout, LLM service errors)
    - Ensure tests cover both stdio and HTTP transport scenarios.
      - Tests should be transport-agnostic since sampling_callback is registered at session level
      - Create test cases that verify callback behavior independent of transport mechanism
      - Both transports will use the same callback instance, so test coverage applies universally

- [ ] 5. Run `make test` to verify all tests pass and no regressions are introduced.
  - Acceptance Criteria:
    - The `make test` command completes successfully.
      - Execute from project root directory: `make test`
      - Command runs linting checks (ruff) and full test suite
      - All checks should pass with zero errors
    - All existing tests continue to pass.
      - MCP tool tests in `assistant/tests/test_assistant_container.py` should pass without modification
      - MCP-related integration tests should verify tool discovery still works
      - Other assistant-related tests should pass unaffected
      - Verify no regressions in existing MCP tool functionality
    - New tests for sampling functionality pass.
      - All unit tests in `assistant/tests/test_mcp_sampling.py` should pass
      - Verify specific test cases:
        - Message conversion (SamplingMessage to LangChain message format)
        - LLM invocation with various parameter combinations
        - Error handling with different exception scenarios
        - Response formatting (CreateMessageResult with role, content, model)
        - Optional parameter handling (systemPrompt, temperature, maxTokens, stopSequences)
      - Sampling callback tests should be independent from transport layer
      - Integration tests should verify callback is properly registered in MultiServerMCPClient

(End of file - total 78 lines)