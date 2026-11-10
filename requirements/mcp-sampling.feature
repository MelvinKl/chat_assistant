@mcp-sampling
Feature: MCP sampling support

  The assistant serves the MCP sampling capability, letting attached MCP servers
  use the assistant LLM through a sampling callback.

  Scenario: the sampling callback is registered with every connected mcp server
    Given configured mcp servers
    When the tools of the servers are loaded
    Then every mcp client connection carries the sampling callback of the LLM

  Scenario: mcp user messages are converted to human messages
    Given an mcp sampling message with role user and text content
    When the mcp messages are converted
    Then the result contains a human message with the text content

  Scenario: mcp assistant messages are converted to ai messages
    Given an mcp sampling message with role assistant and text content
    When the mcp messages are converted
    Then the result contains an ai message with the text content

  Scenario: text content blocks are extracted
    Given a text content block with the text "hello"
    When the content is extracted
    Then the result is "hello"

  Scenario: multiple content blocks are joined with newlines
    Given a list of two text content blocks
    When the content is extracted
    Then the result joins both texts with a newline

  Scenario: non text content blocks yield no text
    Given a non text content block
    When the content is extracted
    Then the result is an empty string

  Scenario: the sampling system prompt becomes the leading system message
    Given a sampling request with a system prompt
    When the sampling callback runs
    Then the LLM receives the system prompt as a leading system message

  Scenario: sampling parameters are mapped onto the LLM call
    Given a sampling request with max tokens, temperature and stop sequences
    When the sampling callback runs
    Then the LLM is called with the max token value
    And the LLM is called with the temperature value
    And the LLM is called with the stop sequences

  Scenario: a zero temperature is still passed to the LLM
    Given a sampling request with temperature zero
    When the sampling callback runs
    Then the LLM is called with temperature zero

  Scenario: the sampling result carries the assistant role and the model name
    Given a sampling callback backed by an LLM with a known model name
    When the sampling callback runs
    Then the result is a create message result with role assistant
    And the result content is the text content of the LLM answer
    And the result model is the model name of the LLM

  Scenario: the model name falls back to the model attribute and then to unknown
    Given a sampling callback backed by an LLM without a model name
    When the sampling callback runs
    Then the result model is the model attribute of the LLM
    And for an LLM without any model information the result model is "unknown"

  Scenario: a failing LLM call yields an mcp error
    Given a sampling callback backed by an LLM that raises an error
    When the sampling callback runs
    Then the result is an error data with the internal error code
    And the error message contains the LLM error

  Scenario: a non string LLM answer is stringified in the result
    Given a sampling callback backed by an LLM returning list content
    When the sampling callback runs
    Then the result content is the string representation of the list
