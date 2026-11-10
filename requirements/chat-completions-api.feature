@chat-completions-api
Feature: OpenAI compatible chat completions endpoint

  The chat assistant exposes an OpenAI compatible chat completions endpoint
  that processes conversation requests through the chat processing graph.

  Background:
    Given a running chat assistant application

  Scenario: accepting a valid chat completion request
    Given a chat completion request with model "test-model"
    And a request message with role "user" and content "Hello"
    When the chat completions endpoint is called with the request
    Then the response status code is 200
    And the response body is a chat completion response

  Scenario: the response echoes the requested model and object type
    Given a valid chat completion request
    When the chat completions endpoint is called with the request
    Then the response model equals the requested model
    And the response object is "chat.completion"
    And the response carries a non empty id
    And the response carries a created timestamp

  Scenario: the response contains a single finished assistant choice
    Given a valid chat completion request
    When the chat completions endpoint is called with the request
    Then the response contains exactly one choice
    And the choice has index 0
    And the choice finish reason is "stop"
    And the choice message has role "assistant"

  Scenario: the response usage reports zero token counts
    Given a valid chat completion request
    When the chat completions endpoint is called with the request
    Then the response usage reports zero prompt tokens
    And the response usage reports zero completion tokens
    And the response usage reports zero total tokens

  Scenario: request messages are converted to ordered history entries
    Given a chat completion request with the following messages
      | role        | content        |
      | user        | What is 2+2?   |
      | assistant   | It is 4        |
      | user        | And 3+3?       |
    When the chat completions endpoint is called with the request
    Then the chat graph is invoked with all messages in request order
    And the first history entry pairs role "user" with content "What is 2+2?"
    And the second history entry pairs role "assistant" with content "It is 4"
    And the third history entry pairs role "user" with content "And 3+3?"

  Scenario: the choice content is the processed answer of the chat graph
    Given a chat graph that answers with the processed answer "Forty two"
    And a valid chat completion request
    When the chat completions endpoint is called with the request
    Then the choice message content is "Forty two"

  Scenario: a request without a model is rejected
    Given a chat completion request without the model field
    When the chat completions endpoint is called with the request
    Then the response status code is 422

  Scenario: a request without messages is rejected
    Given a chat completion request without the messages field
    When the chat completions endpoint is called with the request
    Then the response status code is 422

  Scenario: no chat API implementation is registered
    Given a chat assistant application without a registered chat API implementation
    When the chat completions endpoint is called with a valid request
    Then the response status code is 500
    And the response detail is "Not implemented"
