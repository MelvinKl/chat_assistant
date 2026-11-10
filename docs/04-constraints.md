# 4. Constraints

## 4.1 Technical Constraints

| Constraint | Source |
|---|---|
| Python `>=3.13,<3.14` for the application | `assistant/pyproject.toml` (`requires-python`); the image builds on `python:3.13` (`assistant/Dockerfile`) |
| The app is served by uvicorn on `0.0.0.0:8080` | `CMD` in `assistant/Dockerfile`; containerPort 8080 in the Helm deployment |
| All application settings read from environment variables (per-family prefixes) with optional `.env` file support, unrelated variables ignored | The `SettingsConfigDict(env_prefix=…, env_file=".env", extra="ignore")` of every settings module in `assistant/src/assistant/impl/settings/` |
| MCP server and subagent definitions arrive as mounted JSON files (`/config/mcp/SETTINGS_MCP_SERVERS`, `/config/subagents/SETTINGS_SUBAGENTS`), overridable through `MCP_SETTINGS_PATH` / `SUBAGENT_SETTINGS_PATH` | `load_mcp_settings_from_json`, `load_subagent_settings_from_json` |
| The REST contract follows `assistant/openapi.yaml`; the pydantic models under `assistant/src/assistant/models/` are generated (openapi-generator, see `assistant/src/.openapi-generator/`) | the generator bookkeeping in the tree |
| MCP tool loading needs an event loop from inside the running uvicorn process; the container module patches the loop policy with `nest_asyncio.apply()` at import time | `assistant/src/assistant/assistant_container.py` |
| MCP clients are built with `langchain-mcp-adapters` (`MultiServerMCPClient`, one per configured server) over the `mcp` SDK | project dependencies |
| The default LLM backend is the local ollama instance (`http://ollama:11434/v1`, model `qwen3:4b`) provided by the ollama subchart; a custom LLM disables the local ollama deployment (Tilt) | chart `values.yaml`; the `Tiltfile` |

## 4.2 Organizational Constraints

* **The repository is maintained by the code-weaver factory.** The reusable
  factory workflow is pinned to an owner plus version tag
  (`MelvinKl/code-weaver/.github/workflows/factory.yml@19`) — a moving branch
  ref is not a stable ref. The factory job declares no runner of its own
  (a reusable-workflow job may only carry `uses`/`with`/`secrets`); the runner
  is supplied as the `runner` input (`self-hosted`) and must have `pi`
  pre-installed and configured. The runtime tree is cloned at `factory-ref:
  main`, the loop budget is 25 loops within a 2000-minute job timeout, the
  LLM model is `Qwen3.8`, and only issues labeled `code-weaver` are acted on.
  Credentials (`GH_TOKEN`, the `PI_*` configuration variables) are passed as
  secrets, never as plain inputs.
* **The brownfield test-oracle alignment run (issue 11) is scoped to the test
  oracle.** Per the brownfield clause of that run, no plan step implements or
  modifies product code, workflows, the chart, the README, or any requirement
  file; the changed files are the tests under `assistant/tests/` (and the
  issue's plan file). This documentation tree is the one addition that run
  makes outside the test oracle (the repository previously carried no arc42
  documentation).
* **The README is the primary human-facing documentation.** The arc42 tree under
  `docs/` complements it; where the two can drift, the oracle's
  `repository-structure` feature keeps the README's claims machine-checked
  against the tree.
