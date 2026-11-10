# 1. Introduction

## 1.1 Purpose of the Document

This document is the arc42 documentation of the **chat assistant**
repository. It describes the system as it exists in the tree at the point the
documentation was written: a locally deployable, privacy-focused virtual
assistant powered by a large language model. The assistant exposes an
OpenAI-compatible REST API (chat completions, models, a modular `assist`
endpoint, health and readiness), is extended through MCP servers, can delegate
work to specialized subagents, is deployed to a Kubernetes cluster through a
Helm chart, is developed locally with Tilt and a k3d cluster, and is maintained
by an automated code-weaver factory.

The target audience is threefold:

* **Developers** extending the assistant (new MCP servers, subagents, graph
  nodes, settings families) — chapters 5–8 describe the building blocks and
  their contracts.
* **Operators** deploying the assistant to a cluster — chapters 6 and 9 cover
  the system context and the deployment topology.
* **The code-weaver factory** planning, implementing and reviewing changes
  against this document and the Gherkin requirements oracle — chapter 10
  explains how the oracle is structured and machine-guarded.

## 1.2 Quality Goals

The quality goals the whole system is built around (detailed in chapter 10):

| Quality goal | Meaning |
|---|---|
| Privacy | No data leaves the local network; the LLM runs locally (ollama subchart) |
| Offline operation | The runtime performs no external calls; egress is restricted to internal ranges |
| Robustness | A failing MCP server degrades tool loading and flips the health status; it never kills the chat path |
| Extensibility | Skills are added as MCP servers and subagents via configuration, not code |
| Testability | Every requirement is a Gherkin scenario in `requirements/`; the pytest oracle references each scenario and a guard test verifies the alignment |
| Reproducibility | `uv`-locked environments, pinned CI action versions, a pinned factory workflow reference |

## 1.3 Glossary

The domain vocabulary (assistant, chat graph, rephraser, MCP server,
sampling, subagent, deep agent, oracle, scenario reference, coverage guard,
code-weaver factory, …) is collected in chapter 12.

## 1.4 Project Scope

The repository contains:

* the chat assistant application (`assistant/`: FastAPI app, dependency
  container, OpenAI-compatible APIs, health endpoints, the LangGraph chat
  processing graph, the rephrasers, the MCP sampling support, the settings
  modules, the pytest oracle);
* the Kubernetes deployment (the Helm chart in `infrastructure/helm`,
  including the ollama subchart, pull secret, egress policies, ingress);
* the local development tooling (`infrastructure/local/`, the `Tiltfile`,
  the devcontainer, the `Makefile`);
* the CI/CD and factory workflows (`.github/workflows/`);
* the Gherkin requirements oracle (`requirements/`: 14 feature files,
  128 scenarios);
* this arc42 documentation (`docs/`);
* the Apache-2.0 `LICENSE`.

Not in the tree, although referenced by the `README.md` and the `.vscode`
configuration: the `components/` directory with its `home-assistant` and
`base-component-api` components. That discrepancy is recorded in chapter 11.

## 1.5 References

* `README.md` — the primary human-facing documentation (installation,
  configuration tables, directory structure, getting started).
* `requirements/*.feature` — the executable requirements oracle.
* `plans/11.md` — the brownfield test-oracle alignment plan whose run
  established this documentation tree and the scenario coverage guard.
* [arc42](https://arc42.org) — the documentation template this tree follows.
