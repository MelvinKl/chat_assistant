@local-development
Feature: Local development environment

  The repository provides a Tilt based live development environment, a local
  k3d cluster setup and container based development tooling.

  Scenario: the local env script creates a local k3d cluster
    When the create_local_env script is run
    Then a k3d cluster with one server node and a local registry is created
    And the nginx ingress controller is installed
    And the script waits for the cluster nodes to be ready

  Scenario: tilt builds the assistant image with live updates
    When tilt is started
    Then the assistant image is built from the assistant Dockerfile
    And changes in the assistant sources are synced into the running container

  Scenario: tilt disables the ingress for local development
    When tilt is started
    Then the helm release is deployed with the ingress disabled

  Scenario: in debug mode the assistant waits for the debugger
    Given the tilt debug flag enabled
    When the assistant container starts
    Then it runs under the debugger listening on port 5679
    And it waits for a debugger client to attach

  Scenario: tilt forwards the api and debugger ports
    When tilt is started
    Then port 8080 is forwarded for the assistant api
    And port 5679 is forwarded for the debugger

  Scenario: a custom LLM disables the local ollama deployment
    Given a custom SETTINGS_OPENAI_BASE_URL in the environment
    When tilt is started
    Then the helm release disables the ollama subchart

  Scenario: the makefile exposes format, lint and test targets
    When the make targets are run
    Then the format target applies isort and black inside the assistant project
    And the lint target runs flake8 inside the assistant project
    And the test target runs the lint and the pytest suite via uv

  Scenario: the CI test and lint job validates pull requests
    When a pull request targets main
    Then the workflow installs the dependencies with uv
    And the workflow runs the lint target
    And the workflow runs the test target

  Scenario: the CI docker image job publishes release images
    When a release is published
    Then the assistant image is built and pushed tagged with the release name
    And the image is re tagged as latest

  Scenario: the devcontainer provides the development tooling
    When the devcontainer is started
    Then a python 3.13 image with kubernetes, helm and tilt tooling is running
