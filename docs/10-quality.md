# 10. Quality

## 10.1 Quality Requirements

| Requirement | Driver |
|---|---|
| Privacy: no data leaves the local network | project goal (chapter 3) |
| Offline operation: the runtime makes no external calls | project goal |
| Robustness: a failing MCP server degrades tool loading and flips the health status; the chat path keeps working | the per-server client isolation and the probe thread design |
| Security: the assistant's egress policy allows only the internal CIDR ranges by default and the MCP servers' egress policy is disabled in the default values; credentials only in Kubernetes secrets / workflow secrets | the chart egress policies; the factory's secrets-only credential passing |
| Testability: every requirement is a Gherkin scenario; the alignment between scenarios and the pytest oracle is machine-guarded | the issue-11 brownfield alignment run |
| Reproducibility: `uv` lockfile, pinned CI action versions, pinned local chart versions, a pinned factory workflow reference | the CI and factory configuration |
| Maintainability by automation: the repository is maintained by a machine (the code-weaver factory) inside a bounded budget | the factory constraints (chapter 4) |

## 10.2 Quality Scenarios — The Executable Oracle

The quality scenarios are the Gherkin files under `requirements/`; they are
the single source of truth for behaviour, and the pytest oracle under
`assistant/tests/` implements them. The areas:

| Feature file | Scenarios | Area |
|---|---|---|
| `assist-api.feature` | 4 | the modular assist endpoint |
| `chat-completions-api.feature` | 9 | the OpenAI-compatible chat completions endpoint |
| `chat-graph.feature` | 14 | the chat processing graph (six nodes, bracketed by the question answering stages, the SystemOne goal-reachability determination at invocation) |
| `configuration.feature` | 9 | application settings and container bindings |
| `health-api.feature` | 8 | health/readiness endpoints and the probe thread |
| `helm-deployment.feature` | 15 | the Helm chart |
| `local-development.feature` | 10 | the local development environment |
| `mcp-integration.feature` | 13 | MCP settings loading and client connections |
| `mcp-sampling.feature` | 13 | the MCP sampling support |
| `models-api.feature` | 5 | the OpenAI-compatible models endpoints |
| `rephraser.feature` | 10 | question/answer rephrasing |
| `repository-structure.feature` | 6 | documentation–repository consistency |
| `stages.feature` | 6 | the question answering stages |
| `subagents.feature` | 8 | subagent configuration and tool assignment |

**Total: 130 scenarios.**

**How the alignment is enforced.** Because the oracle is plain pytest (no
Gherkin runner is a dependency), the join lives in the test docstrings: a test
that implements a scenario cites it in one of the two machine forms defined by
the guard module, e.g.

```
Implements "the health check repeats on a five minute interval"
(requirements/health-api.feature)
```

or

```
requirements/health-api.feature::the health check repeats on a five minute interval
```

`assistant/tests/test_scenario_coverage.py` (introduced by step 1 of
`plans/11.md`) verifies both directions:

* every extracted `Scenario:` title is referenced by at least one test —
  parametrised per feature file, so the guard turns green per area as the
  referencing tests of the alignment plan land, and is fully green at the
  plan's gate step;
* no test references a scenario absent from `requirements/` (no dangling
  references).

Where a scenario's expected outcome does not yet hold against the current
repository, the referencing test asserts the outcome as extracted and is
marked `xfail`: it keeps the guard and the suite green, reports the gap in
chapter 11, and turns green when a later run lands the fix. The brownfield
run pinned risks 1, 7, 8, 9, 13, 14 and 15 this way (e.g.
`tests/test_helm_deployment.py::test_default_values_contain_only_consumed_keys`
and `tests/test_repository_structure.py::test_directory_structure_exists_in_repository`);
the fix run that followed landed those fixes, and the tests are plain green
assertions now.

**The gate.** The repository's own `make test` target — lint (flake8 with the
project's plugin set), then `pytest .`, both via `uv` from `assistant/` — is
the entry point of the CI test job and of the plan's gate step.

## 10.3 Cross-Cutting Concepts

* **Lint rules.** `assistant/pyproject.toml`: `max-line-length = 120`,
  `max-complexity = 8`, double quotes (`inline-quotes`/`docstring-quotes`/
  `multiline-quotes`), the flake8 plugin set (black, quotes, bandit, bugbear,
  builtins, comprehensions, eradicate, pytest-style, simplify, wot,
  tidy-imports, pep8-naming), and per-file test ignores `S101, I252, E800,
  F841` for `./tests/*`. Source docstrings follow the numpy convention.
* **The locked environment.** `assistant/uv.lock` pins the runtime and dev
  dependencies; `make format`/`lint`/`test` all run through `uv run`.
* **The scenario reference convention.** Defined by the guard module's
  docstring (chapter 7.4); it is the machine contract between the oracle and
  the requirements.

## 10.4 Quality Building Blocks

| Building block | Provides |
|---|---|
| `tests/test_scenario_coverage.py` | the coverage guard (per-area parametrised) and the dangling-reference check; the home of the reference convention |
| the per-area test modules (`test_chat_api`, `test_models_api`, `test_assistant_api`, `test_health_endpoints`, `test_helm_deployment`, `test_local_development`, `test_repository_structure`, `test_settings`, `test_mcp_client_setup`, `test_mcp_sampling`, `test_subagent_settings`, `test_stages`, `test_container`, `graph/test_chat_graph`, `rephraser/test_rephraser`, `test_integration`) | the scenario implementations, each citing the scenario it arose from |
| `conftest.py`, `fake_chat_model.py` | the shared app/client fixtures and the stub LLM |
| the `make lint` / `make test` targets and the `test-and-lint.yml` CI job | the standing validation gate on every pull request to `main` |
| the requirements oracle | the machine-actionable maintenance loop |
