@assist-api
Feature: Modular assist endpoint

  The chat assistant exposes a POST /assist endpoint that accepts a plain text
  question and delegates it to a registered assistant API implementation.

  Scenario: the assist endpoint accepts a plain text body
    Given a running chat assistant application
    When the assist endpoint is called with the text body "body example"
    Then the body is dispatched to the registered assistant implementation

  Scenario: the endpoint responds not implemented without a registered implementation
    Given a chat assistant application without a registered assistant API implementation
    When the assist endpoint is called with a text body
    Then the response status code is 500
    And the response detail is "Not implemented"

  Scenario: implementations register themselves through the base API
    Given an assistant API implementation class that subclasses the base assistant API
    When the implementation module is imported
    Then the base API registry contains the implementation

  Scenario: the endpoint delegates to the first registered implementation
    Given two registered assistant API implementations in import order
    When the assist endpoint is called with a text body
    Then the first registered implementation handles the request
