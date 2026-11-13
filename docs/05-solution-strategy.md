# 5. Solution Strategy

## 5.1 Key Forces

| Force | Consequence for the solution |
|---|---|
| **Privacy** — the assistant must operate without internet access | A local LLM (ollama subchart) and egress-governed pods: the assistant's egress policy allows only the internal CIDR ranges by default, and the MCP servers' egress policy is disabled in the default values (chapter 9) |
| **Extensibility** — skills must be addable by users, not by the developers | MCP servers contribute tools through configuration; a `deep agent` uses them, and named subagents receive the tools of the servers that assign to them |
| **Testability** — behaviour must be verifiable in a plain CI runner | The requirements are Gherkin features; the oracle is plain `pytest` (no BDD runner is a dependency); a coverage guard test makes the scenario-to-test alignment machine-checkable |
| **Autonomous maintenance** — a machine, not a team, maintains the repository | Every artefact the factory acts on must be stable and machine-actionable: pinned workflow references, a locked dependency set, a Gherkin oracle, structured documentation |
| **A small code base** — one application, a few components | A single composition root (the `inject` container) wires everything; the API layer delegates to registered implementations through base-class registries |

## 5.2 Key Decisions

| Decision | Choice made | Consequences |
|---|---|---|
| How API implementations plug in | Base classes (`BaseChatApi`, `BaseModelsApi`, `BaseAssistantApi`) keep a `subclasses` tuple filled by `__init_subclass__`; the routers import `assistant.impl` (resp. `assistant.impl.apis`) so implementations register themselves on import | Pluggable implementations without any configuration; the endpoint delegates to the first registered subclass; an empty registry answers 500 `Not implemented` |
| How components are composed | `assistant_container.configure()` binds the LLM (from the OpenAI settings), both rephrasers, the preprocessing and postprocessing stages (each with its system prompt from the prompt settings, the tools of the servers assigned to it and the optional `SystemOneSettings` model), the MCP tool groups, the settings objects, the `ChatGraph` constructor and the MCP agent (a `deep agent`); `nest_asyncio.apply()` is patched at import time so `asyncio.run` works inside uvicorn for MCP tool loading | One composition root; every binding the oracle checks lives in one module |
| What the agent is | `create_deep_agent(model, tools, subagents)`: the main agent gets the tools of MCP servers without an `agent` assignment; each configured subagent gets a dedicated system prompt plus the tools of the servers that name it; a server whose `agent` field is `preprocessing` or `postprocessing` has its tools routed to the respective question answering stage instead | Specialized, context-cheap subagents (chapter 7, block "dependency container") |
| How MCP servers are reached | One `MultiServerMCPClient` per configured server (stdio: `command`/`args`; sse/http: `url`/`transport`/`headers`); a failing server is logged and skipped, the others keep loading; tools are grouped under their agent key (`None` = main agent, a subagent name = that subagent, `preprocessing`/`postprocessing` = the respective question answering stage) | A dead server degrades the tool set and the health status; it never breaks the others |
| How a chat request is processed | A six-node LangGraph: `START` feeds the `preprocessing` stage, which fans out to `determine_language` and `rephrase_question`; `rephrase_question` feeds `decide`; both predecessors converge into `rephrase_answer`, which feeds the `postprocessing` stage, ending the graph; state is the typed `GraphState` | The preprocessing stage prepares the question before language detection and question rephrasing run in parallel; the postprocessing stage shapes the rephrased answer; the single `processed_answer` (the postprocessing stage's output) is what the HTTP layer returns |
| How liveness is observed | `GET /health` starts a background thread on first call; the thread probes every configured MCP server, flips a lock-guarded status global to `unhealthy` on failure, and repeats on a 300 s interval; `GET /readiness` is a static answer | No external liveness dependency; the probe doubles as a tool re-load (chapter 8, scenario 3) |
| How the oracle is aligned with the tests | Each pytest test that implements a Gherkin scenario cites it in its docstring (`Implements "<title>" (requirements/<file>.feature)`, or the machine form `requirements/<file>.feature::<title>`); `tests/test_scenario_coverage.py` verifies every extracted scenario is cited and that no citation dangles | The alignment is a CI-runnable assertion, not a convention (chapter 10) |
| How the system is documented | An arc42 tree under `docs/` (established by the issue-11 run); the README stays the human-facing front door | One structured, machine-navigable source; discrepancies between README and tree are recorded, not hidden (chapter 11) |

## 5.3 Strategy

The system is layered into three rings:

1. **A thin HTTP shell.** FastAPI routers for the OpenAI-compatible surface
   (chat completions, models) plus the modular `assist` endpoint and the
   health/readiness probes. The routers know nothing about the LLM; they
   delegate to whatever implementation registered itself.
2. **A DI-composed brain.** The container module assembles the `ChatOpenAI`
   LLM, the two rephrasers, the preprocessing and postprocessing stages, the
   MCP tool groups, the `ChatGraph`, and the
   `deep agent`. The chat graph is where a request becomes an answer; the
   stages and the rephrasers are the graph's linguistic muscles; the deep
   agent is where MCP
   tools and subagents do the work.
3. **A nervous system of MCP servers.** Configured servers are connected at
   startup (and re-probed every five minutes by the health thread); their
   tools hang off the agents, and the assistant offers the LLM back to the
   servers through the MCP sampling capability.

Quality is structurally enforced rather than hoped for: the Gherkin oracle
under `requirements/` is the single source of truth for behaviour, the pytest
oracle under `assistant/tests/` cites the scenarios it implements, the
coverage guard makes that citation complete and non-dangling, and the
repository's own `make test` target (lint + pytest via uv) is the gate the CI
test job runs. Operations closes the loop: the cluster is provisioned by a
script, the image is published by the release workflow (or live-reloaded by
Tilt in development), and the factory maintains the code against the oracle.
