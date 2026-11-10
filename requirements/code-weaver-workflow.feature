@code-weaver
Feature: Code weaver workflow

  The repository wires the code-weaver factory into its GitHub workflows to
  turn labeled issues into pull requests.

  Scenario: the workflow starts when an issue is labeled
    When an issue receives a label
    Then the code-weaver workflow starts for the issue

  Scenario: the workflow can be started manually
    Given a manual workflow dispatch
    When the workflow is run with an optional issue number
    Then the code-weaver workflow starts for the given issue

  Scenario: the factory job references a pinned factory version
    When the code-weaver workflow file is read
    Then the factory job uses the reusable factory workflow
    And the reference pins an owner and a version tag rather than a moving branch ref

  Scenario: the factory runs on the configured runner
    When the code-weaver workflow file is read
    Then the factory job declares no runner of its own
    And the runner input is set to self-hosted

  Scenario: the factory clones its runtime tree from main
    When the code-weaver workflow file is read
    Then the factory ref input is main

  Scenario: the factory loop budget and timeout are configured
    When the code-weaver workflow file is read
    Then the job timeout is 2000
    And the maximum loop count is 25

  Scenario: the factory uses the configured LLM model
    When the code-weaver workflow file is read
    Then the llm model input is Qwen3.8

  Scenario: the factory only acts on requirements labeled issues
    When the code-weaver workflow file is read
    Then the ai requirements label input is code-weaver

  Scenario: credentials are passed as secrets
    When the code-weaver workflow file is read
    Then the job receives the gh token and the pi configuration as secrets
    And no credential is passed as a plain input
