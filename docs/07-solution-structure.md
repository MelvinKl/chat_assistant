# 7. Solution Strategy — Building Blocks

## 7.1 Building Blocks Overview

The repository as a set of building blocks:

| Block (path) | Role |
|---|---|
| `assistant/src/assistant/main.py` | The FastAPI application (`title="Chat assistant API"`, `version="2.3.0"`): mounts the chat, models, assist and health routers, then calls `configure()` |
| `assistant/src/assistant/assistant_container.py` | The dependency container (`inject`): the composition root — LLM, rephrasers, MCP tool groups, settings, chat graph, deep agent; patches `nest_asyncio` at import |
| `assistant/src/assistant/apis/` | The HTTP layer: routers plus the base registries (`chat_api_base`, `models_api_base`, `assistant_api_base`) |
| `assistant/src/assistant/impl/apis/`, `impl/endpoints/` | The registered implementations (`ChatApi`, `ModelsApi`) and the generated endpoint stubs (`default_assist_endpoint`, `default_get_description_endpoint`) |
| `assistant/src/assistant/impl/graph/` | The chat processing graph (`chat_graph.py`: `ChatGraph`, `GraphNodeNames`) and its typed state (`graph_state.py`: `GraphState`) |
| `assistant/src/assistant/impl/rephraser/` | The `Rephraser` runnable (system + user prompt template over a state dict, sync/async invocation) |
| `assistant/src/assistant/impl/mcp_sampling.py` | The MCP sampling support (`_extract_text`, `_convert_mcp_messages`, `create_sampling_callback`) |
| `assistant/src/assistant/impl/settings/` | The settings modules: `openai_settings`, `prompt_settings`, `information_settings`, `api_settings`, `mcp_server_settings`, `subagent_settings` |
| `assistant/src/assistant/endpoints/` | The health/readiness router with the background MCP probe thread; plus orphaned generated endpoint stubs (see chapter 11) |
| `assistant/src/assistant/models/` | The pydantic request/response models, generated from `assistant/openapi.yaml` by openapi-generator (bookkeeping in `assistant/src/.openapi-generator/`) |
| `assistant/tests/` | The pytest oracle: per-area test modules plus `conftest.py`, `fake_chat_model.py` and the scenario coverage guard `test_scenario_coverage.py` (chapter 10) |
| `infrastructure/helm/` | The Helm chart (deployment, service, ingress, pull secret, secrets, config maps, per-MCP-server resources, egress policies, the ollama subchart) |
| `infrastructure/local/` | `create_local_env.sh` + `k3d-cluster-config.yaml`: the local k3d cluster with registry and nginx ingress |
| `.github/workflows/` | `test-and-lint.yml` (PR gate), `docker-image.yml` (release images), `code-weaver.yml` (the factory) |
| `Tiltfile`, `Makefile`, `.devcontainer/`, `.vscode/` | The local development environment: live-reload builds, port forwards, debug attach, format/lint/test targets |
| `requirements/` | The Gherkin oracle: 14 feature files, 128 scenarios |
| `docs/` | This arc42 documentation |
| `LICENSE` | Apache License 2.0 |

## 7.2 Key Allocation

| Concept | Realized in |
|---|---|
| OpenAI-compatible HTTP surface | `apis/chat_api.py`, `apis/models_api.py` (routers) delegating to `impl/apis/` (implementations) via the base registries |
| Modular assist endpoint | `apis/assistant_api.py` delegating to `BaseAssistantApi.subclasses[0]` |
| LLM creation | `assistant_container._di_config` from `OpenAISetttings` |
| Question/answer rephrasing | `impl/rephraser/rephraser.py`, bound as `question_rephraser` / `answer_rephraser` |
| Chat processing | `impl/graph/chat_graph.py` (nodes, edges, `ainvoke`, image export), `impl/graph/graph_state.py` |
| MCP tool loading | `assistant_container._get_mcp_tools` (one `MultiServerMCPClient` per server) |
| MCP sampling | `impl/mcp_sampling.py` (`create_sampling_callback`) |
| Subagent configuration | `impl/settings/subagent_settings.py`; subagents are composed in `_di_config` |
| Subagents as agents | the `deepagents` `create_deep_agent` call in `_di_config` |
| Health & readiness | `endpoints/health_endpoints.py` (router, status global, probe thread) |
| Configuration | the six settings modules + the mounted JSON config files |
| Deployment | the chart under `infrastructure/helm` |
| Local development | `Tiltfile`, `infrastructure/local/`, `.devcontainer/`, `Makefile` |
| CI / image publication | `.github/workflows/test-and-lint.yml`, `docker-image.yml` |
| Autonomous maintenance | `.github/workflows/code-weaver.yml` |
| Requirements oracle | `requirements/*.feature` |
| Oracle alignment guard | `assistant/tests/test_scenario_coverage.py` |

## 7.3 Key Interfaces

**I1 — REST (OpenAI-compatible).** The mounted routes:

| Route | Behaviour |
|---|---|
| `POST /chat/completions` | Delegates to the first registered `BaseChatApi` subclass; 422 on validation failure (missing `model` or `messages`); 500 `Not implemented` when no implementation is registered |
| `GET /models`, `GET /models/{model}` | Delegates to the first registered `BaseModelsApi` subclass; answers with the single `chat_assistant` model; 500 `Not implemented` when none is registered |
| `POST /assist` | Accepts a plain text body; delegates to the first registered `BaseAssistantApi` subclass; 500 `Not implemented` when none is registered |
| `GET /health` | Starts the background MCP probe thread on first call; returns `{status, version}` |
| `GET /readiness` | Static `{status: "ready", version}` |

**I2 — Configuration.** Environment-variable families (all with `.env`
support, `extra="ignore"`):

| Family | Prefix / source | Fields |
|---|---|---|
| `OpenAISetttings` | `SETTINGS_OPENAI_*` | `model`, `base_url`, `api_key` |
| `PromptSettings` | `SETTINGS_PROMPTS_*` | the four rephrasing prompts (`rephrase_question_system_prompt`, `rephrase_question_user_prompt`, `rephrase_answer_system_prompt`, `rephrase_answer_user_prompt`) |
| `InformationSettings` | `SETTINGS_ADDITIONAL_*` | `information` |
| `APISetttings` | `SETTINGS_API_*` | `name`, `description` |
| `MCPSettings` | file `/config/mcp/SETTINGS_MCP_SERVERS` (override: `MCP_SETTINGS_PATH`) | `servers`: `name`, `transport`, `url`, `command`, `args`, `env`, `agent`, `headers` |
| `SubagentSettings` | file `/config/subagents/SETTINGS_SUBAGENTS` (override: `SUBAGENT_SETTINGS_PATH`) | `subagents`: `name`, `description`, `system_prompt` |

**I3 — MCP.** The assistant connects to each configured server with its own
`MultiServerMCPClient` (stdio: `command`/`args`; sse/http: `url`/`transport`
/`headers`), loads the server's tools at startup, and — where a server
requests it — serves the LLM through the sampling capability (chapter 8,
scenario 2). The `mcp` SDK's `ClientSession` exposes the sampling hook; the
assistant's handler is `create_sampling_callback`, registered on every
connection under `session_kwargs` — the installed langchain-mcp-adapters takes
no callback at the client level (chapter 11, risk 9, records the pre-fix
state).

**I4 — The code-weaver factory.** Inputs of the pinned reusable workflow:
`job-timeout: 2000`, `max-loops: 25`, `issue-number`,
`ai-requirements-label: code-weaver`, `llm-model: Qwen3.8`,
`runner: self-hosted`, `factory-ref: main`; secrets `GH_TOKEN`,
`PI_MODELS`, `PI_SETTINGS`, `PI_MCP`, `PI_EXTENSION_ENV`.

## 7.4 Cross-Cutting Concepts

* **The settings pattern.** Every configuration concern is a pydantic-settings
  module with an environment prefix, `.env` support and `extra="ignore"` —
  new families are added by a new module, not by touching the container.
* **The registry pattern.** Base classes collect subclasses through
  `__init_subclass__`; routers import the implementation package to trigger
  registration and then delegate to the first entry — the empty-registry 500
  `Not implemented` is the closed-world answer.
* **Dependency injection.** One `inject` container, one `configure()`; every
  binding is visible in one module and individually testable.
* **Egress policy.** A shared Helm template renders an egress `NetworkPolicy`
  per deployment: enabled + hosts → allow-list; enabled + no hosts → allow
  all; disabled → no egress rules.
* **The scenario reference convention.** Tests cite the Gherkin scenario they
  implement in their docstring; the coverage guard parses both the feature
  files and the test docstrings and verifies the alignment in both directions
  (chapter 10).

## 7.5 Building Block Details

### The assistant application

`main.py` builds the FastAPI app, includes the four routers and calls
`configure()`. The container (`assistant_container.py`) reads all six settings
families, creates the `ChatOpenAI` LLM, loads the MCP tools per server
(`_get_mcp_tools`: a failing server is logged and skipped; tools are grouped
under the server's `agent` key, `None` meaning the main agent), composes the
deep agent with the configured subagents (each subagent receives the tools of
the servers that name it, else none), and binds both rephrasers, the tool
group, the `MCPSettings` and `InformationSettings` objects, the `ChatGraph`
constructor and the `mcp_agent`.

The chat graph (`chat_graph.py`) is a compiled `StateGraph(GraphState)` with
four nodes — `rephrase_question`, `determine_language`, `decide`,
`rephrase_answer` — wired `START → determine_language ∥ rephrase_question →
decide → rephrase_answer → END` (both predecessors converge into
`rephrase_answer`). `ainvoke` maps the incoming message list onto the state
(the last message is the question, the earlier ones become `role: content`
history entries, the additional information comes from the information
settings), runs the graph, and returns the `processed_answer`; an empty input
short-circuits to `No question has been found.`. `draw_graph` exports the
compiled graph as a PNG via the Mermaid API.

### The test oracle and the coverage guard

The oracle under `assistant/tests/` is plain `pytest`/`pytest-asyncio` (the
dev extras of `assistant/pyproject.toml`); no BDD runner exists, which is why
the scenario-reference convention lives in the tests themselves. The modules:
`test_settings` (the configuration and MCP server settings),
`test_mcp_client_setup` (MCP tool loading and client connections, plus the
sampling callback registration on every connection — chapter 11),
`test_mcp_sampling` (sampling), `test_subagent_settings` (the subagents
config file loading), `test_container` (the container's
bound rephrasers and the chart default prompts), `test_chat_api`,
`test_models_api`, `test_assistant_api` (the modular assist endpoint —
body dispatch, the empty-registry 500, self-registration and the
first-registered delegation, exercised against the oracle's own
`BaseAssistantApi` implementations, as the tree carries no product
implementation), `test_health_endpoints` (the health and readiness
responses, plus the probe thread — the thread start on the first
request, the per-server probe dicts, the 300 s round interval, the
failing-server unhealthy flip and the all-reachable healthy status),
`test_helm_deployment` (the rendered helm chart — every template evaluated
with the module's own go-template subset — chapter 11), `test_local_development` (the local development tooling — the
Tiltfile, the k3d bootstrap script and cluster config, the devcontainer, the
make targets and the CI workflows, inspected statically),
`test_code_weaver_workflow` (the code-weaver factory workflow — the
``.github/workflows/code-weaver.yml`` file parsed as yaml: the label trigger
and the manual dispatch, the pinned factory reference, the runner, budget
and model inputs, and the secrets-only credential passing),
`test_integration`,
`graph/test_chat_graph`, `rephraser/test_rephraser`,
shared by `conftest.py` and `fake_chat_model.py`.

The guard, `test_scenario_coverage.py`, introduces the convention and makes
it machine-checkable:

* **Extraction** — every `Scenario:` title of every
  `requirements/*.feature` file is collected (14 files, 128 scenarios).
* **Reference scan** — every test function's docstring is scanned for
  citations in the two accepted machine forms:
  `Implements "<scenario title>" (requirements/<name>.feature)` and the
  separator form `requirements/<name>.feature::<scenario title>`.
* **Guard 1 (coverage)** — parametrised per feature file: every extracted
  scenario of that file must be cited by at least one test. The guard is
  parametrised per area on purpose: it turns green per area as the
  referencing tests of `plans/11.md` land step by step, and is fully green
  once the plan is complete.
* **Guard 2 (no dangling references)** — every citation must resolve to a
  `Scenario:` title that the very feature file it names carries.

### The Helm chart

`Chart.yaml` (name `assistant`, v0.0.1) with the ollama subchart
(condition `ollama.enabled`, default true); `templates/` renders the assistant
deployment (image `ghcr.io/melvinkl/chat_assistant/assistant:latest`, port
8080, the pull secret, the mounted MCP/subagents config maps, envFrom from the
settings config map and the OpenAI secret, debug vs normal args), the service,
the ingress plus cert-manager certificate (toggle `assistant.ingress.enabled`),
the pull secret (from the `ghcrIo` values), the assistant secret (base64 of
the OpenAI settings), the settings config map, the MCP/subagents config maps,
and — per MCP server deployment — a config map, a secret, a service, a
deployment and an optional egress policy. See chapter 9 for the full
resource table.

### The factory workflow

`.github/workflows/code-weaver.yml` is described in chapter 8, scenario 4;
its constraints (pinned ref, runner input, budgets, secrets) are the
organisational constraints of chapter 4.
