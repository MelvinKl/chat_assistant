@health
Feature: Health and readiness endpoints

  The chat assistant exposes health and readiness endpoints and continuously
  monitors the reachability of its configured MCP servers.

  Scenario: the health endpoint reports the application status and version
    Given a running chat assistant application
    When the health endpoint is called
    Then the response status code is 200
    And the response status is "healthy"
    And the response version equals the chat assistant application version

  Scenario: the readiness endpoint reports the application as ready
    Given a running chat assistant application
    When the readiness endpoint is called
    Then the response status code is 200
    And the response status is "ready"
    And the response version equals the chat assistant application version

  Scenario: the health check thread starts on the first health request
    Given a running chat assistant application
    When the health endpoint is called for the first time
    Then a background health check thread is started

  Scenario: the health check probes every configured MCP server
    Given MCP servers configured for the assistant
    When the background health check runs
    Then every configured MCP server is probed for tool loading
    And a stdio server is probed with its command and args
    And a remote server is probed with its url, transport and headers

  Scenario: the health check repeats on a five minute interval
    Given a started background health check
    When one round of checks finishes
    Then the check waits 300 seconds before the next round

  Scenario: a failing MCP server turns the health status unhealthy
    Given one configured MCP server that fails to load its tools
    When the background health check runs
    Then the health status is "unhealthy"

  Scenario: all reachable MCP servers keep the health status healthy
    Given configured MCP servers that all load their tools
    When the background health check runs
    Then the health status is "healthy"

  Scenario: without configured MCP servers the health status stays healthy
    Given no MCP servers configured for the assistant
    When the background health check runs
    Then the health status is "healthy"
