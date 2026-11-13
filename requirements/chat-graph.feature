@chat-graph
Feature: Chat processing graph

  The chat assistant processes each request with a state graph that determines
  the question language, rephrases the question, answers it through the MCP
  agent and rephrases the answer.

  Scenario: the graph contains the six processing nodes
    Given a chat graph
    When the node names are read
    Then the node names are
      | node               | value              |
      | determine language | determine_language |
      | rephrase question  | rephrase_question  |
      | decide             | decide             |
      | rephrase answer    | rephrase_answer    |
      | preprocessing      | preprocessing      |
      | postprocessing     | postprocessing     |

  Scenario: the graph starts with the preprocessing step
    Given a chat graph
    When the graph wiring is read
    Then the start node connects to the preprocessing node
    And the preprocessing node connects to the determine language node
    And the preprocessing node connects to the rephrase question node

  Scenario: the question rephrasing feeds the decision
    Given a chat graph
    When the graph wiring is read
    Then the rephrase question node connects to the decide node

  Scenario: language detection and decision converge into the answer rephrasing
    Given a chat graph
    When the graph wiring is read
    Then the determine language node connects to the rephrase answer node
    And the decide node connects to the rephrase answer node
    And the rephrase answer node connects to the postprocessing node
    And the postprocessing node connects to the end node

  Scenario: an empty request yields the no question answer
    Given a chat graph
    When the graph is invoked with an empty message list
    Then the result is "No question has been found."

  Scenario: the last message is used as the question
    Given a chat graph
    When the graph is invoked with a message list whose last entry is a user question
    Then the initial graph state question equals the content of the last message

  Scenario: earlier messages become history entries
    Given a chat graph
    When the graph is invoked with messages before the final question
    Then each earlier message becomes a history entry formatted as its role followed by its content

  Scenario: the initial state carries the additional information
    Given information settings with the additional information "extra context"
    And a chat graph built with the information settings
    When the graph is invoked with a single question
    Then the initial graph state carries the additional information "extra context"

  Scenario: the invocation result is the processed answer
    Given a chat graph whose graph run ends with a processed answer
    When the graph is invoked with a question
    Then the returned result equals the processed answer of the final state

  Scenario: the language node detects the language of the question
    Given a chat graph
    And a question written in German
    When the determine language node runs on the state
    Then the state question language is set to the detected language of the question

  Scenario: the decide node asks the MCP agent the rephrased question
    Given a chat graph
    When the decide node runs on a state with the rephrased question
    Then the MCP agent is invoked with the question as its messages
    And the raw answer is the content of the last agent message

  Scenario: the graph can be exported as an image
    Given a chat graph
    When the graph is drawn into a target directory
    Then a chat graph png file exists in the target directory

  Scenario: the SystemOne model determines if the users goal can be reached
    Given a chat graph with a configured SystemOne model
    When the graph is invoked with a user question
    Then the SystemOne model determines if the users goal can be reached at all with the available MCP servers

  Scenario: an unreachable goal skips the stages up to the answer generation
    Given a chat graph with a configured SystemOne model
    And a user question whose goal cannot be reached with the available MCP servers
    When the graph is invoked with the question
    Then the stages up to the answer generation are skipped
    And the returned answer informs the user that no MCP servers are currently available to help
