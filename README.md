# Chat Assistant

Chat Assistant is a locally deployable, privacy-focused virtual assistant powered by a Large Language Model (LLM). Designed to function without requiring internet access, it ensures data security and user privacy while delivering intelligent and context-aware assistance. The application supports extensibility through the Model Context Protocol (MCP), allowing users to add custom skills and functionalities seamlessly.

Key Features:

- Local Deployment:
    Run the application entirely on your local machine or server, ensuring complete control over your data and environment.

- No Internet Required:
    Operates offline, making it ideal for secure environments or areas with limited connectivity.

- LLM-Powered Intelligence:
    Leverages a Large Language Model to provide natural language understanding and context-aware responses.

- Extensible via MCP:
    Add new skills and capabilities using the Model Context Protocol (MCP), enabling tailored functionality to meet specific needs.

- Privacy-Focused:
    The LLM can be hosted locally, ensuring that no data ever leaves the local network.


# Installation
This application is build to run on a kubernetes cluster. The `infrastructure/helm` directory contains a helm chart for easy deployment.

## Configuration
Here is an explanation of the configuration options available through the `infrastructure/helm/values.yaml` file:

### Pull Secret
|Key|Default value|Explanation|
|---|---|---|
|`ghcrIo.username`|-|Your Ghcr username. This value is used to create a pull secret so the images can be pulled.|
|`ghcrIo.pat`|-|Your Ghcr pat. This value is used to create a pull secret so the images can be pulled.|
|`ghcrIo.email`|-|Your Ghcr username. This value is used to create a pull secret so the images can be pulled.|

### Ingress
|Key|Default value|Explanation|
|---|---|---|
|`assistant.ingress.enabled`|`true`|Enables or disables the ingress.|
|`assistant.ingress.host`|`assistant.localhost`|The host for the ingress.|

### Prompts
|Key|Default value|Explanation|
|---|---|---|
|`assistant.settings.prompt.SETTINGS_PROMPTS_REPHRASE_QUESTION_SYSTEM_PROMPT`|`Your job is to rephrase the questions so they contain all the relevant information from the history required to answer the question.`|The system prompt used for rephrasing of the initial question. Usable placeholders are: `question`,`history`|
|`assistant.settings.prompt.SETTINGS_PROMPTS_REPHRASE_QUESTION_USER_PROMPT`|`Question: {question}\nHistory: {history}`|The user prompt used for rephrasing of the initial question. Usable placeholders are: `question`,`history`|
|`assistant.settings.prompt.SETTINGS_PROMPTS_REPHRASE_ANSWER_SYSTEM_PROMPT`|`You are James, a butler of the aristocracy.\nYou will get asked questions and will be provided with the correct answer.\nHowever the answer might not be worded suitable for your master. Your job is to rephrase the answer in a way that is suitable for your master.\nAnswer in the following language: {question_language}`|The system prompt used for rephrasing the final answer. Usable placeholders are: `question`,`history`, `question_language`,`additional_info`,`raw_answer`|
|`assistant.settings.prompt.SETTINGS_PROMPTS_REPHRASE_ANSWER_USER_PROMPT`|`Question: {question}\nAnswer: {raw_answer}`|The user prompt used for rephrasing the final answer. Usable placeholders are: `question`,`history`, `question_language`,`additional_info`,`raw_answer`|

### LLM Settings
|Key|Default value|Explanation|
|---|---|---|
|`assistant.settings.openai.SETTINGS_OPENAI_MODEL`|`qwen3:4b`|The used LLM.|
|`assistant.settings.openai.SETTINGS_OPENAI_BASE_URL`|`http://ollama:11434/v1`|The host of the LLM provider. Defaults to the ollama instance that can be installed using this helm chart.|
|`assistant.settings.openai.SETTINGS_OPENAI_API_KEY`|`changeme`|The apikey for the LLM provider. If ollama is used this value is not required.|

### Other Settings
|Key|Default value|Explanation|
|---|---|---|
|`assistant.settings.additionalInformation`|`Fun Fact: Your source code is available under Apache2 license`|Additional information that is given to the LLM. This can be things like, the position of the home, the name of the user, etc. This value is loaded as a string, there are no requirements on the format.|

### MCP Server
This configuration is for the available skills in the chat assistant. By default [this](https://github.com/MelvinKl/mcp-weather) mcp server for weather information is configured. Keep in mind that this mcp server requires the geo coordinates of the location you want a weather forecast for.
An example prompt using this mcp server would be:
```
"How is the weather at latitude:49.0148,longitude:8.4?"
```

The 'mcpServers' configuration consists of two subsections:
#### Deployments
This section governs the deployment of additional mcp server. If the mcp server you want to use is alread deployed you can skip this section.
Each deployment should be an array item containing the following information:

|Key|Default value|Explanation|
|---|---|---|
|`name`|`weather`|Name of the MCP server to deploy|
|`port`|`8080`|Port of the MCP server|
|`image`|`ghcr.io/melvinkl/mcp-weather/server:latest`|Image of the MCP server|
|`command`|`["uv","run","python","src/main.py"]`|(Optional) Run command for the MCP server|
|`secrets`|`TRANSPORT: sse`|Values that will  be saved as kubernetes secret and injected as env vars into the MCP server.|

#### Servers
This section configures the connection to the used MCP servers.
Each MCP server should be an array item containing the following information:

|Key|Default value|Explanation|
|---|---|---|
|`name`|`weather`|Name of the MCP server|
|`url`|`http://weather:8080/sse`|Connection URL of the MCP server|
|`transport`|`sse`|Connection protocol used|
|`headers`|-|Optional. Dictionary of additional values to send as headers to the server|

### Ollama
Ollama can be used as a local LLM provider. For a full overview of available configuration options please see [here](https://github.com/otwld/ollama-helm)

|Key|Default value|Explanation|
|---|---|---|
|`ollama.enabled`|`true`|Enables or disables the Ollama deployment|

## Directory Structure
The repository is organized as follows:

### `assistant`
* The chat assistant API and its endpoints. This includes an OpenAI compatible chat completion endpoint and a modular assistant endpoint.

### `components`
* Directory containing additional components for extending the chat assistant.
* `home-assistant`: Component for integrating with Home Assistant.

### `infrastructure/helm`
* Contains the Helm chart for deploying the chat assistant to a Kubernetes cluster.

### `infrastructure/local/create_local_env.sh`
* Setup script for creating a local k3d cluster for development purposes.

### `.vscode` and `.devcontainer`
* Contain configuration files for debugging with Visual Studio Code and developing in a devcontainer, respectively.

## Getting Started
To get started with the chat assistant, follow these steps:

1. Create a new Kubernetes cluster using `infrastructure/local/create_local_env.sh`.
2. Create a `.env` file in the root of the repository with required secrets, such as `SETTINGS_HOMEASSISTANT_APIKEY`.
3. Use `Tiltfile` to start the chat assistant application.
4. When using `Tiltfile`, the APIs will wait for the debugger to connect.

## Development
This repository provides a `Tiltfile` for local development. It supports live-reloading for the assistant component and easy debugging.

## Testing

### Full Testing Pipeline
The full testing pipeline (unit tests, linting, and e2e tests) can be run using:
```bash
make test
```

Note: E2E tests require the chat assistant service to be deployed and accessible at `http://localhost:8080`. If the service is not available, E2E tests will wait and eventually fail.

### Unit Tests Only
To run only unit tests and linting (without E2E tests):
```bash
make lint
cd assistant; uv run --extra dev pytest .
```

### E2E Tests Only
To run only end-to-end tests:
```bash
make test-e2e
```

### Mock Servers for Testing
The repository includes lightweight mock servers for CI/CD testing:

#### Mock MCP Server (`infrastructure/mock-mcp-server`)
A mock Model Context Protocol server that provides test tools without requiring actual MCP deployments.

#### Mock OpenAI Server (`infrastructure/mock-openai-server`)
A mock OpenAI-compatible server that provides fast, deterministic responses for testing without requiring LLM deployments.

**Decision Note**: For CI/CD testing, we use mock servers instead of Ollama because:
- No model downloads required (faster test runs)
- Deterministic responses (more reliable tests)
- Lower resource usage (more efficient CI/CD)

For local development and production, real LLM providers like Ollama should be used.

### E2E Testing Pipeline
The GitHub Actions workflow (`.github/workflows/test-pipeline.yml`) runs end-to-end tests by:
1. Creating a KinD cluster
2. Building and deploying the chat assistant with mock servers
3. Running curl-based tests against the deployed services
