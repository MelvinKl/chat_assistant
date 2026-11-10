# 3. Goals

## 3.1 Project Goals

1. **A local virtual assistant.** The assistant runs entirely on the operator's
   own machine or server; nothing needs to leave the local network.
2. **An OpenAI-compatible surface.** Chat completions (`POST /chat/completions`),
   model listing and retrieval (`GET /models`, `GET /models/{model}`) and a
   modular `POST /assist` endpoint, so any OpenAI-compatible client works
   unchanged.
3. **LLM-shaped conversation processing.** Every request travels through a
   state graph that detects the question language, rephrases the question with
   history, answers it through an MCP tool-capable agent, and rephrases the
   answer in the question's language.
4. **Extensibility without code.** Skills are contributed by MCP servers
   (configuration, not source), and specialized subagents receive dedicated
   system prompts and dedicated tool selections.
5. **Kubernetes-deployable, locally developable.** One Helm chart deploys the
   assistant, its MCP servers and a local ollama LLM backend; Tilt plus a k3d
   cluster give live-reload development with an attachable debugger.

## 3.2 Quality Goals (As a Whole)

The system-wide quality goals, as specified in chapter 1:

* **Privacy** — the LLM is hosted locally (ollama subchart); the assistant
  pod's egress is restricted to the internal CIDR ranges by default.
* **Offline operation** — the runtime performs no external network calls.
* **Robustness** — a failing MCP server is logged and skipped during tool
  loading and turns the health status `unhealthy`; the remaining servers keep
  serving tools and the chat path keeps working.
* **Testability** — the requirements are Gherkin scenarios (128 of them in 14
  feature files under `requirements/`); the pytest oracle references each
  scenario from a test docstring, and the coverage guard in
  `assistant/tests/test_scenario_coverage.py` verifies both directions of that
  alignment (chapter 10).
* **Security by default** — MCP server deployments have egress disabled by
  default; credentials live in Kubernetes secrets (pull secret, OpenAI
  settings, per-server secrets) and, in the factory workflow, only in secrets.
* **Reproducibility** — `uv` with a committed lockfile for the Python
  environment; pinned versions for CI actions, the local charts and the
  code-weaver factory workflow reference.

## 3.3 Derived Goals

* A single stable model identity: the models endpoints present the assistant
  as one model (`chat_assistant`), whatever model id a client requests.
* Liveness for the cluster: `/health` and `/readiness` endpoints plus a
  background thread that re-probes every configured MCP server on a five
  minute interval.
* A machine-actionable maintenance loop: the code-weaver factory plans,
  implements and reviews changes against the requirements oracle and this
  documentation, within a bounded loop budget and timeout.

## 3.4 Out-of-Scope Items

* **The `components/` tree.** The README's Directory Structure section lists a
  `components/` directory (containing `home-assistant`,
  `base-component-api`, …) that is **not present** in the repository tree. The
  documentation follows the tree; the discrepancy is recorded in chapter 11
  and surfaced by the `repository-structure` feature of the oracle.
* **Dynamic knowledge settings.** A `SETTINGS_DYNAMIC_KNOWLEDGE_*` family
  appears in one test fixture but no settings module of the application reads
  it; it is an inert template remnant (chapter 11).
* Multi-tenancy, a web front-end, and any deployment beyond a single
  assistant deployment with its MCP servers are not part of the system.
