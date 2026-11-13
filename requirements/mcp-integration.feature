@mcp-integration
Feature: MCP server integration

  The assistant loads its MCP server configuration, connects to every configured
  server and registers their tools for the agent.

  Scenario: the server settings are loaded from the mcp config file
    Given a json file with server definitions at the mcp config path
    When the mcp server settings are loaded
    Then the settings contain one server per definition

  Scenario: the mcp config path can be overridden by an environment variable
    Given the MCP_SETTINGS_PATH environment variable pointing at an alternate file
    When the mcp server settings are loaded with a different default path
    Then the settings are read from the file named by the environment variable

  Scenario: a server definition carries name, transport and connection details
    Given a server definition with a name, a url and a transport
    When the server model is validated
    Then the server carries its name
    And the server carries its url and transport
    And the server has empty defaults for command, args and env

  Scenario: a missing config file yields an empty server list
    Given a mcp config path that does not exist
    When the mcp server settings are loaded
    Then the settings contain no servers

  Scenario: an invalid json config file raises a value error
    Given a mcp config file containing invalid json
    When the mcp server settings are loaded
    Then a value error is raised reporting invalid json

  Scenario: a stdio server is connected with its command
    Given a server definition with stdio transport, a command and args
    When the tools of the server are loaded
    Then the mcp client is created with the command, the args and the stdio transport

  Scenario: a remote server is connected with its url
    Given a server definition with sse transport and a url
    When the tools of the server are loaded
    Then the mcp client is created with the url and the sse transport

  Scenario: server headers are preserved on the connection
    Given a server definition with sse transport and authorization headers
    When the tools of the server are loaded
    Then the mcp client receives the configured headers

  Scenario: every server is connected with its own client
    Given two configured mcp servers
    When the tools of the servers are loaded
    Then each server is connected through a separate mcp client

  Scenario: a failing server does not prevent the other servers from loading tools
    Given one server that fails to load tools and one server that succeeds
    When the tools of the servers are loaded
    Then the tools of the succeeding server are registered
    And the failure is logged without aborting the load

  Scenario: server tools are grouped by their agent assignment
    Given one server without an agent and one server with an agent name
    When the tools of the servers are loaded
    Then the tools of the first server are registered under the main agent
    And the tools of the second server are registered under the named subagent

  Scenario: a server assigned to the preprocessing stage registers its tools for that stage
    Given an mcp server with the agent preprocessing
    When the tools of the server are loaded
    Then the tools of the server are registered under the preprocessing stage

  Scenario: a server assigned to the postprocessing stage registers its tools for that stage
    Given an mcp server with the agent postprocessing
    When the tools of the server are loaded
    Then the tools of the server are registered under the postprocessing stage
