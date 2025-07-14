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
|`command`|`["poetry","run","python","src/main.py"]`|(Optional) Run command for the MCP server|
|`secrets`|`TRANSPORT: sse`|Values that will  be saved as kubernetes secret and injected as env vars into the MCP server.|

#### Servers
This section configures the connection to the used MCP servers.
Each MCP server should be an array item containing the following information:

|Key|Default value|Explanation|
|---|---|---|
|`name`|`weather`|Name of the MCP server|
|`url`|`http://weather:8080/sse`|Connection URL of the MCP server|
|`transport`|`sse`|Connection protocol used|

### Ollama
Ollama can be used as a local LLM provider. For a full overview of available configuration options please see [here](https://github.com/otwld/ollama-helm)

|Key|Default value|Explanation|
|---|---|---|
|`ollama.enabled`|`true`|Enables or disables the Ollama deployment|
