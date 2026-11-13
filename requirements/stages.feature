@stages
Feature: Question answering stages

  The question answering is extended by a preprocessing stage and a
  postprocessing stage. Each stage carries its own system prompt and its own
  selection of available MCP servers, and can run on an optional SystemOne
  model that limits the tools available to the LLM at that stage.

  Scenario: the preprocessing stage runs with its own system prompt
    Given a chat graph with a preprocessing stage
    When the preprocessing stage runs on the question
    Then the stage LLM call carries the preprocessing system prompt

  Scenario: the postprocessing stage runs with its own system prompt
    Given a chat graph with a postprocessing stage
    When the postprocessing stage runs on the returned answer
    Then the stage LLM call carries the postprocessing system prompt

  Scenario: a stage receives the tools of its available MCP servers
    Given a stage with available MCP servers
    When the stage LLM is created
    Then the stage LLM receives the tools of the available MCP servers

  Scenario: a SystemOne model limits the tools available to the stage LLM
    Given a stage with a configured SystemOne model
    When the stage LLM is created
    Then the tools available to the stage LLM are limited

  Scenario: the SystemOne model is optional
    Given a stage without a configured SystemOne model
    When the stage LLM is created
    Then the stage runs with the main LLM

  Scenario: the SystemOne model filters the MCP servers available to a stage
    Given a stage with a configured SystemOne model
    And available MCP servers
    When the stage LLM is created
    Then the MCP servers available to the stage are filtered by the SystemOne model
