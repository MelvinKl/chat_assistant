@configuration
Feature: Application settings

  The assistant reads its configuration from environment variables and a .env
  file and wires the resulting components into a dependency container.

  Scenario: the LLM is created from the openai settings
    Given the SETTINGS_OPENAI_MODEL, SETTINGS_OPENAI_BASE_URL and SETTINGS_OPENAI_API_KEY environment variables
    When the dependency container is configured
    Then an openai compatible chat model is created with the configured model, base url and api key

  Scenario: the prompt settings are read from the environment
    Given the four SETTINGS_PROMPTS_ environment variables
    When the prompt settings are created
    Then the settings carry the question rephrasing system and user prompts
    And the settings carry the answer rephrasing system and user prompts

  Scenario: the additional information is read from the environment
    Given the SETTINGS_ADDITIONAL_INFORMATION environment variable
    When the information settings are created
    Then the settings carry the configured additional information

  Scenario: the api name and description are read from the environment
    Given the SETTINGS_API_NAME and SETTINGS_API_DESCRIPTION environment variables
    When the api settings are created
    Then the settings carry the configured name and description

  Scenario: the settings are loaded from a .env file
    Given a .env file with settings values
    When a settings object is created
    Then the values from the .env file are used

  Scenario: unrelated environment variables are ignored
    Given environment variables that match no settings field
    When a settings object is created
    Then no validation error is raised

  Scenario: the container binds the agent components
    Given configured LLM, tools, subagents, prompts and information settings
    When the dependency container is configured
    Then the question rephraser is bound with the question rephrasing prompts
    And the answer rephraser is bound with the answer rephrasing prompts
    And the tools, the mcp settings, the information settings and the chat graph are bound
    And the mcp agent is bound as the deep agent of the LLM

  Scenario: nested event loops are allowed for MCP tool loading
    When the assistant container module is imported
    Then the asyncio event loop policy is patched to allow nested event loops
