@models-api
Feature: OpenAI compatible models endpoint

  The chat assistant exposes OpenAI compatible model listing and retrieval
  endpoints that describe the assistant as a single model.

  Scenario: listing the available models
    Given a running chat assistant application
    When the models endpoint is called
    Then the response status code is 200
    And the response object is "list"
    And the response data contains at least one model

  Scenario: every listed model carries the model fields
    Given a running chat assistant application
    When the models endpoint is called
    Then each listed model has an id
    And each listed model has a created timestamp
    And each listed model has object "model"
    And each listed model has a non empty owned_by value

  Scenario: retrieving a model by id
    Given a running chat assistant application
    When the model retrieval endpoint is called with the model id "chat_assistant"
    Then the response status code is 200
    And the returned model has id "chat_assistant"
    And the returned model has object "model"

  Scenario: retrieving any model id returns the same assistant model
    Given a running chat assistant application
    When the model retrieval endpoint is called with the model id "model-1"
    And the model retrieval endpoint is called with the model id "model-2"
    Then both responses return the same model id

  Scenario: no models API implementation is registered
    Given a chat assistant application without a registered models API implementation
    When the models endpoint is called
    Then the response status code is 500
    And the response detail is "Not implemented"
