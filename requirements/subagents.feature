@subagents
Feature: Subagents

  The assistant supports specialized subagents that receive dedicated system
  prompts and a dedicated selection of MCP tools.

  Scenario: the subagent settings are loaded from the subagents config file
    Given a json file with subagent definitions at the subagents config path
    When the subagent settings are loaded
    Then the settings contain one subagent per definition

  Scenario: the subagents config path can be overridden by an environment variable
    Given the SUBAGENT_SETTINGS_PATH environment variable pointing at an alternate file
    When the subagent settings are loaded with a different default path
    Then the settings are read from the file named by the environment variable

  Scenario: a subagent definition consists of name, description and system prompt
    Given a subagent definition with a name, a description and a system prompt
    When the subagent model is validated
    Then the subagent carries its name
    And the subagent carries its description
    And the subagent carries its system prompt

  Scenario: a missing config file yields no subagents
    Given a subagents config path that does not exist
    When the subagent settings are loaded
    Then the settings contain no subagents

  Scenario: an invalid json config file raises a value error
    Given a subagents config file containing invalid json
    When the subagent settings are loaded
    Then a value error is raised

  Scenario: the deep agent is created with the main agent tools and the subagents
    Given an LLM, main agent tools and configured subagents
    When the dependency container is configured
    Then a deep agent is created with the LLM
    And the main agent receives the tools without an agent assignment
    And each configured subagent is passed to the deep agent

  Scenario: a subagent receives the tools of its assigned servers
    Given a subagent named weather and an mcp server with the agent weather
    When the tools of the servers are loaded
    Then the subagent weather receives the tools of the server

  Scenario: a subagent without assigned servers receives no tools
    Given a subagent whose name matches no mcp server agent
    When the tools of the servers are loaded
    Then the subagent receives an empty tool list
