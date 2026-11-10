@helm-deployment
Feature: Kubernetes deployment via helm chart

  The helm chart in infrastructure/helm deploys the chat assistant, its MCP
  servers and a local Ollama instance to a kubernetes cluster.

  Scenario: the chart deploys the assistant
    Given the helm chart
    When the chart is rendered
    Then a deployment named assistant runs the chat assistant image
    And the assistant container listens on port 8080
    And the deployment uses the pull secret

  Scenario: the chart exposes the assistant through a service
    When the chart is rendered
    Then a service named assistant exposes port 8080 inside the cluster

  Scenario: the ingress can be toggled
    Given assistant.ingress.enabled set to false
    When the chart is rendered
    Then no ingress is created
    Given assistant.ingress.enabled set to true
    When the chart is rendered with the configured host
    Then an ingress routes the host to the assistant service
    And a cert-manager certificate is created for the host

  Scenario: a pull secret is created from the ghcr credentials
    Given the ghcrIo username, pat and email values
    When the chart is rendered
    Then a pull secret with the ghcr.io docker config is created

  Scenario: the mcp servers settings are rendered into a mounted config map
    Given mcpServers values with server definitions
    When the chart is rendered
    Then a config map contains the mcp servers settings as json
    And the assistant deployment mounts the config map at /config/mcp

  Scenario: the subagent settings are rendered into a mounted config map
    Given subagents values with subagent definitions
    When the chart is rendered
    Then a config map contains the subagent settings as json
    And the assistant deployment mounts the config map at /config/subagents

  Scenario: the openai settings are rendered as a secret
    Given assistant.settings.openai values
    When the chart is rendered
    Then a secret contains the base64 encoded openai settings
    And the assistant deployment injects the secret as environment variables

  Scenario: the prompt settings are rendered as environment variables
    Given assistant.settings.prompt and additionalInformation values
    When the chart is rendered
    Then the assistant config map carries the prompts and the additional information as environment variables

  Scenario: each mcp server deployment gets its own resources
    Given mcpServers.deployments entries with name, port, image, command, secrets and config
    When the chart is rendered
    Then each entry gets a deployment, a service, a config map and a secret
    And each deployment injects its config map and its secret as environment variables

  Scenario: the default assistant egress policy allows only the internal networks
    Given the default assistant egress values
    When the chart is rendered
    Then an egress network policy for the assistant allows only
      | cidr           |
      | 10.0.0.0/8     |
      | 172.16.0.0/12  |
      | 192.168.0.0/16 |

  Scenario: mcp server deployments are egress disabled by default
    Given the default mcp server deployment values
    When the chart is rendered
    Then no egress traffic is allowed for the mcp server pods

  Scenario: an enabled egress without allowed hosts allows all egress
    Given an egress policy enabled with an empty allowed hosts list
    When the chart is rendered
    Then the network policy allows all egress

  Scenario: the ollama subchart is enabled by default
    Given the default chart values
    When the chart is rendered
    Then the ollama subchart is deployed
    And the configured LLM model is pulled into ollama

  Scenario: the rendered assistant environment matches the settings the application reads
    When the chart is rendered with the default values
    Then every environment variable key rendered for the assistant exists in the application settings models

  Scenario: the default values contain only keys consumed by the chart templates
    When the default values file is read
    Then every top level key has a consuming chart template
