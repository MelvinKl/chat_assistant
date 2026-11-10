# 2. Stakeholders

## 2.1 Actors

| Actor | Interest in the system |
|---|---|
| End user | Asks the assistant questions through any OpenAI-compatible client (or the modular `/assist` endpoint); expects context-aware answers, local processing, and extensible skills (weather, home control, …) |
| Developer | Builds the assistant image, live-reloads it with Tilt, attaches the debugger from the devcontainer, runs the `make` format/lint/test targets, and extends the assistant (new graph nodes, MCP servers, subagents, settings) |
| Operator | Maintains the Kubernetes cluster, the Helm release values (pull secret, egress, prompts, LLM settings, MCP servers, subagents, ollama), and reads the health/readiness probes |
| Code-weaver factory | Turns issues labeled `code-weaver` into planned, implemented and reviewed pull requests; runs on a self-hosted runner, clones its runtime tree from `main`, and is pinned to a version tag of the reusable factory workflow |
| MCP servers | Attach to the assistant; contribute tools to the main agent or to a named subagent; may use the assistant LLM through the MCP sampling capability |
| Subagents | Specialized agents (created by the deep-agent machinery) that receive a dedicated system prompt and the tools of the MCP servers assigned to them, keeping the main agent's context small |

## 2.2 Projects

| Project | Relationship |
|---|---|
| Code-weaver factory (`MelvinKl/code-weaver`) | The reusable workflow this repository invokes (`.github/workflows/code-weaver.yml`); the reference is pinned to a version tag (`factory.yml@19`), never to a moving branch |
| Ollama Helm chart (`otwld/ollama-helm`, version 1.93.0, digest-pinned in `Chart.lock`) | Subchart providing the local LLM backend the assistant's OpenAI settings point at by default |
| MCP weather server (`MelvinKl/mcp-weather`) | The default MCP server configuration: the example skill the README and the chart values ship |
| Bitnami nginx-ingress-controller (chart version 10.3.0) | Installed by `infrastructure/local/create_local_env.sh` for the local k3d cluster |
