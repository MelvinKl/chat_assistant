@rephraser
Feature: Question and answer rephrasing

  The assistant rephrases incoming questions and raw answers with LLM driven
  rephrasers that are configured through the prompt settings.

  Scenario: the rephraser builds a prompt with a system and a user message
    Given a rephraser with a system prompt template and a user prompt template
    When the prompt template is built
    Then it contains one system message from the system prompt
    And it contains one user message from the user prompt

  Scenario: template placeholders are rendered from the state
    Given a rephraser whose templates reference state variables
    When the rephraser is invoked with a state that fulfils all template variables
    Then the rendered system and user messages contain the state values

  Scenario: the async invocation returns the LLM answer content
    Given a rephraser backed by an LLM that answers "re-phrased!"
    When the rephraser is invoked asynchronously with a state
    Then the result is "re-phrased!"

  Scenario: the sync invocation returns the LLM answer content
    Given a rephraser backed by an LLM that answers "re-phrased!"
    When the rephraser is invoked synchronously with a state
    Then the result is "re-phrased!"

  Scenario: extra keyword arguments are passed to the LLM
    Given a rephraser backed by a recording LLM
    When the rephraser is invoked with a temperature and a max token argument
    Then the LLM receives the temperature argument
    And the LLM receives the max token argument

  Scenario: a missing template variable fails the invocation
    Given a rephraser whose user prompt references the variable "a"
    When the rephraser is invoked with a state that lacks the variable
    Then the invocation raises a key error naming the missing variable

  Scenario: the question rephraser uses the question rephrasing prompts
    Given prompt settings with question rephrasing system and user prompts
    When the dependency container is configured
    Then the bound question rephraser uses the configured system and user prompts

  Scenario: the answer rephraser uses the answer rephrasing prompts
    Given prompt settings with answer rephrasing system and user prompts
    When the dependency container is configured
    Then the bound answer rephraser uses the configured system and user prompts

  Scenario: the default question rephrasing prompts cover the graph state
    Given the chart default question rephrasing prompts
    When the user prompt template is read
    Then it references the question, history and additional info placeholders
    And the system prompt instructs to rephrase the question with the relevant information from the history

  Scenario: the default answer rephrasing prompts rephrase in the question language
    Given the chart default answer rephrasing prompts
    When the system prompt template is read
    Then it references the question language placeholder
    And the user prompt template references the question, raw answer and additional info placeholders
