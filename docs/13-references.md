# 13. References

**In-repository:**

* `README.md` — the primary human-facing documentation (installation,
  configuration tables, directory structure, getting started, development)
* `requirements/*.feature` — the requirements oracle:
  `assist-api` (4), `chat-completions-api` (9), `chat-graph` (12),
  `code-weaver-workflow` (9), `configuration` (8), `health-api` (8),
  `helm-deployment` (15), `local-development` (10), `mcp-integration` (11),
  `mcp-sampling` (13), `models-api` (5), `rephraser` (10),
  `repository-structure` (6), `subagents` (8) — 128 scenarios
* `plans/11.md` — the brownfield test-oracle alignment plan (16 steps) whose
  run established this documentation tree and the coverage guard
* `LICENSE` — Apache License 2.0
* `assistant/pyproject.toml`, `assistant/uv.lock` — the project definition and
  the locked environment
* `assistant/openapi.yaml`, `assistant/src/.openapi-generator/` — the API
  contract and the generator bookkeeping (openapi-generator
  7.10.0-SNAPSHOT)
* `.github/workflows/test-and-lint.yml`, `docker-image.yml`,
  `code-weaver.yml` — the CI and factory configuration
* `Makefile`, `Tiltfile`, `.devcontainer/devcontainer.json`,
  `.vscode/settings.json`, `.vscode/launch.json` — the local development
  environment
* `infrastructure/helm/` (`Chart.yaml`, `Chart.lock`, `values.yaml`,
  `templates/`), `infrastructure/local/` — the deployment artefacts

**External:**

* [arc42](https://arc42.org) — the documentation template (the 13-chapter
  structure this tree follows)
* The code-weaver factory — `MelvinKl/code-weaver`; the reusable
  `factory.yml` is pinned in `.github/workflows/code-weaver.yml` to the
  version tag `@19`
* The ollama Helm chart — `otwld/ollama-helm` (version 1.93.0, digest
  `sha256:5b8c…d52344` in `Chart.lock`); the local LLM backend
* The mcp-weather MCP server — `MelvinKl/mcp-weather`; the default configured
  skill
* The bitnami `nginx-ingress-controller` chart (10.3.0) — local ingress
  provisioning
* The Python stacks the app is built on — FastAPI, uvicorn, pydantic /
  pydantic-settings, `inject`, LangChain (core / openai / community),
  LangGraph, the `mcp` SDK, `langchain-mcp-adapters`, `deepagents`,
  `nest-asyncio`, `langdetect`; managed with [uv](https://docs.astral.sh/uv/)
