# 9. Deployment

## 9.1 Topology

The cluster (a single k3d cluster in local development; any Kubernetes
cluster in production) hosts one Helm release (`assistant`) rendering:

| Chart template | Renders | Notes |
|---|---|---|
| `assistant-deployment.yaml` | Deployment `assistant` (1 replica) | image `ghcr.io/melvinkl/chat_assistant/assistant:latest`, `imagePullPolicy: Always`, the `pull-secret`; containerPort 8080; mounts the MCP and subagents config maps at `/config/mcp` and `/config/subagents`; `envFrom` the settings config map + the OpenAI secret; the command switches between `assistant.args` (uvicorn on 8080) and `assistant.debugArgs` (debugpy listening on 5679, `--wait-for-client`) on `assistant.debug`; followed by the assistant egress network policy |
| `assistant-service.yaml` | Service `assistant` | ClusterIP, port 8080 |
| `assistant-ingress.yaml` | Ingress `assistant` (+ cert-manager `Certificate`) | rendered only when `assistant.ingress.enabled`; nginx class, the configured host, TLS via the `cert-issuer` cluster issuer; note the secret/certificate name carries a historical typo (`assitant-tls-certificate`) |
| `pull-secret.yaml` | Secret `pull-secret` (dockerconfigjson) | base64 of the ghcr auth built from the `ghcrIo` values (username, pat, email) |
| `assistant-secret.yaml` | Secret `assistant-secret` | every value of `assistant.settings.openai` base64-encoded |
| `assistant-cm.yaml` | ConfigMap `assistant-cm` | `SETTINGS_ADDITIONAL_INFORMATION` and the four `SETTINGS_PROMPTS_*` prompt values — exactly the environment variables the application's settings models read (the dead `SETTINGS_PROMPTS_MAX_TOOLS` key of chapter 11, risk 8, is removed) |
| `assistant-mcp-cm.yaml` | ConfigMap `assistant-mcp-cm` | `SETTINGS_MCP_SERVERS` = the JSON-serialised `mcpServers` values, mounted at `/config/mcp` (the loader's default path) |
| `assistant-subagents-cm.yaml` | ConfigMap `assistant-subagents-cm` | `SETTINGS_SUBAGENTS` = the JSON-serialised `subagents` values, mounted at `/config/subagents` |
| `mcp-cm.yaml`, `mcp-secrets.yaml`, `mcp-service.yaml`, `mcp-deployment.yaml` | per MCP server deployment: config map, secret, service, deployment | each server runs its own resources (image, port, optional command, its own secrets); its egress network policy is rendered unconditionally — with the default `egress.enabled: false` the policy carries the Egress policy type without an egress rule, which kubernetes reads as deny-all egress, so the README's “egress disabled by default” holds; an enabled policy renders the allowed-host `ipBlock` rules, or an allow-all rule when enabled without hosts (chapter 11, risk 13, records the pre-fix state where the policy document was suppressed) |
| ollama subchart | the ollama deployment (+ PVC) | enabled by default (`ollama.enabled: true`); pulls `qwen3:4b` and `nomic-embed-text` |

**Local cluster topology** (`infrastructure/local/k3d-cluster-config.yaml`):
one server node, zero agents, a loadbalancer publishing `80:80`, and a local
registry at `0.0.0.0:5000` (`registry.localhost`); kubelet eviction
thresholds are set for both node classes. `create_local_env.sh` creates the
cluster (`k3d cluster create chat-assi`, traefik disabled), waits for the
nodes to be ready (120 s), adds the bitnami Helm repository and installs the
nginx-ingress-controller (chart 10.3.0) into its own namespace.

## 9.2 Infrastructure

* **Images** — published to ghcr.io: the assistant image by the release
  workflow (tag = release tag, plus a re-tagged `latest`); the MCP server
  images named in the chart values (default: the mcp-weather server); the
  ollama image from the subchart (`pullPolicy: Always`).
* **Charts** — the bitnami nginx-ingress-controller (10.3.0) for local
  ingress; the otwld ollama-helm chart (1.93.0, digest-pinned in
  `infrastructure/helm/Chart.lock`).
* **TLS** — the ingress annotations reference a `cert-issuer` cluster issuer
  and the ACME flow; the chart renders the matching `Certificate`.

## 9.3 Load Balancing

The k3d loadbalancer node publishes port 80 to the cluster's nginx ingress
controller; the ingress routes its host (default `assistant.localhost`) to the
assistant service on 8080, annotated with a source-range whitelist
(`192.168.0.1/16`) and the cert-manager ACME annotations. In local development
Tilt deploys the release with the ingress disabled and forwards the ports
directly (8080 → the API, 5679 → the debugger).

## 9.4 Provisioning

| Artefact | What it does |
|---|---|
| `infrastructure/local/create_local_env.sh` | creates the k3d cluster, waits for ready nodes, installs the bitnami nginx ingress controller |
| `Tiltfile` | reads `.env`; offers the `debug` flag; `docker_build`s the assistant image from `assistant/Dockerfile` (build arg `DEV` set in debug mode) with a live-update sync of `assistant/` into `/app/assistant`; assembles the Helm values (ingress disabled, the `GH_*` credentials, the `SETTINGS_OPENAI_*` overrides from the environment, and `ollama.enabled=false` whenever a custom `SETTINGS_OPENAI_BASE_URL` is set); deploys the `assistant` Helm release; forwards 8080 (linked as `/docs`) and 5679 |
| `Makefile` | `format` (isort + black via uv), `lint` (flake8 via uv), `test` (lint, then `pytest .` via uv) — the same entry points the CI test job uses |
| `.github/workflows/docker-image.yml` | on `release: published` (or manual dispatch): checks out, logs in to ghcr.io with `GITHUB_TOKEN`, builds `assistant/Dockerfile`, pushes the release tag and re-tags `latest` |
| `.github/workflows/test-and-lint.yml` | on pull requests to `main` (or manual dispatch): sets up Python 3.14, installs `uv`, syncs the dev extras, runs `make lint` then `make test` |
| `.devcontainer/devcontainer.json` | the development container: `mcr.microsoft.com/devcontainers/python:3.13-bookworm`, remote user `vscode`, VS Code extensions (python, helm-intellisense, tiltfile, …), and the devcontainer features `docker-outside-of-docker`, `kubectl-helm-minikube`, `tilt`; `KUBECONFIG` pointed at the workspace |

## 9.5 Monitoring

The system exposes its own liveness: the `/health` endpoint (status flipped by
the background MCP probe thread, plus the application version) and the static
`/readiness` answer (chapter 8, scenario 3). The container, the tool loading
and the health thread log through the standard `logging` module; no metrics
stack is part of the chart.

## 9.6 Backup

The assistant and the MCP servers are stateless; the only state is the ollama
models, kept on a persistent volume by the subchart (`persistentVolume.enabled: true`).
