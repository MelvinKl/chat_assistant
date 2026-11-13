# 8. Runtime Behavior

## 8.1 Key Scenarios

### Scenario 1 — A chat completion request

```
client ──POST /chat/completions {model, messages}──► chat router
  1. registry check: BaseChatApi.subclasses empty? → 500 "Not implemented"
  2. ChatApi (first registered implementation):
     history = [(role, content) for each request message, in order]
     result = await chat_graph.ainvoke(history)
  3. ChatGraph.ainvoke:
     - input empty  → "No question has been found."
     - question  = last message;  history = "role: content" of the earlier ones
     - state = GraphState.create(history, question, additional_info)
     - system one configured?  → the SystemOne model determines if the
       user's goal can be reached at all with the available MCP servers
       (consulted with the question and the names of the configured
       servers); an unreachable goal short-circuits to
       "No MCP servers are currently available to help." — the stages up to
       the answer generation are skipped and the compiled graph is not run;
       a reachable goal continues below
     - run the compiled LangGraph:
         START ─► preprocessing   (preprocessing stage: an LLM call on the
                                     question with the preprocessing system
                                     prompt; its output is the question)
         preprocessing ─► determine_language  (langdetect on the question)
         preprocessing ─► rephrase_question   (question rephraser runnable)
         rephrase_question ─► decide  (deep agent invoked with
                                      {"messages": <rephrased question>};
                                      raw_answer = last agent message)
         [determine_language, decide] ─► rephrase_answer  (answer rephraser,
                                                       in {question_language})
         rephrase_answer ─► postprocessing  (postprocessing stage: an LLM
                                             call on the rephrased answer
                                             with the postprocessing system
                                             prompt; its output is the
                                             processed_answer)
         postprocessing ─► END
  4. response: model = requested model, object = "chat.completion",
     single choice (index 0, finish_reason "stop", role "assistant",
     content = processed_answer), usage = zeros, id/created stamped
```

Validation rejections happen before any of this: a request without `model`
or without `messages` is answered 422 by FastAPI.

### Scenario 2 — Container configuration at startup (MCP tool loading)

On import of `assistant.main`, `configure()` runs: the seven settings families
are read (environment + `.env`); the `ChatOpenAI` LLM is created from the
OpenAI settings; for every configured MCP server a `MultiServerMCPClient` is
built — stdio servers with `command`/`args`, remote servers with
`url`/`transport` (plus `headers` when set, and — in each connection's
`session_kwargs` — the LLM's sampling callback, the registration the
mcp-sampling oracle pins) — and `get_tools()` is awaited
through `asyncio.run` (which is why the module patches `nest_asyncio` at
import). A server that fails is logged (`Could not load MCP Tools from
server …`) and skipped; the others still contribute. Tools are grouped under
the server's `agent` key — `None` for the main agent, a subagent name for
that subagent, `preprocessing`/`postprocessing` for the respective question
answering stage. The preprocessing and postprocessing stages are composed
(each with its system prompt from the prompt settings, the tools of the
servers assigned to it — with the loaded tools of those servers kept per
server — and the `SystemOneSettings` model), the deep agent is
created with the LLM, the main tool set and the configured subagents (each
subagent carries its system prompt plus the tools of the servers that name
it), the chat graph is handed the `SystemOneSettings` model and the
`MCPSettings` (for the goal-reachability determination at invocation),
and all of it is bound into the `inject` container.

**Sampling.** `create_sampling_callback(llm)` in `impl/mcp_sampling.py` is
the assistant's MCP sampling handler: it converts the MCP sampling messages
(`user` → `HumanMessage`, otherwise `AI`-message), extracts text from the
content blocks (non-text blocks yield nothing; several blocks are joined with
newlines), prepends a system message from `systemPrompt`, maps
`maxTokens`/`temperature` (including a zero temperature)/`stopSequences` onto
the LLM call, and answers with a `CreateMessageResult` carrying role
`assistant`, the LLM's model name (falling back `model_name` → `model` →
`unknown`) — or an `ErrorData` when the LLM call fails. The oracle
(`requirements/mcp-sampling.feature`) requires that this callback is
registered with every connected MCP server, and that is what happens: the
sampling hook lives on the `mcp` SDK's `ClientSession` (`sampling_callback`,
with a default handler that answers sampling requests with an error), and the
installed langchain-mcp-adapters takes no callback at the client level — its
`create_session` forwards only logging and elicitation callbacks — so both
MCP client call sites (the container's tool loading and the health probe) put
the callback under `session_kwargs` of each server's connection dict, which
the adapter's session creators forward to the `ClientSession` (chapter 11,
risk 9, records the pre-fix state where the default error-answering handler
applied).

### Scenario 3 — The health probe thread

The first `GET /health` starts a background thread targeting
`health_check`. Each round, the thread walks every configured MCP server,
builds the same client dict the tool loading uses (stdio: `command`/`args`;
remote: `url`/`transport`/`headers`), opens a `MultiServerMCPClient` and
attempts `get_tools()`: success appends the server's tools to the container's
`tools` group again; **any failure flips the lock-guarded status global to
`unhealthy`**. The round ends with `time.sleep(300)` — the five-minute
interval. `GET /health` always answers `{status, version: "2.3.0"}` read
under the lock; `GET /readiness` answers a static
`{status: "ready", version: "2.3.0"}`.

### Scenario 4 — A code-weaver factory run

An issue receives a label (or a maintainer dispatches the workflow manually
with an optional `issue_number`) → `code-weaver.yml` starts → its single job
`uses` the pinned reusable factory workflow
(`MelvinKl/code-weaver/.github/workflows/factory.yml` — an owner plus a
version tag, never a moving branch ref), declares no `runs-on` of its own
(reusable-workflow jobs may only carry `uses`/`with`/`secrets`; the runner is
the `runner` input, the dedicated `code-weaver` self-hosted runner, whose
environment has `pi` pre-installed and configured) → the factory clones its
runtime tree at `factory-ref: main`, works the issue within `max-loops: 25` and a 2000-minute job timeout
on the `Qwen3.8` model, acting only on issues carrying the
`code-weaver` label (`ai-requirements-label`) → the stage jobs produce
planned, implemented and reviewed pull requests, authenticated through the
`GH_TOKEN` secret (the pi configuration variables are passed as secrets
too — no credential ever travels as a plain input).

## 8.2 MCP Tool Loading and Sampling — Internal Contract

`MultiServerMCPClient` (langchain-mcp-adapters) is constructed per server
with that server's connection dict and used for `get_tools()`; sessions are
created internally by the adapter (`create_session`), which forwards callback
configuration through `session_kwargs` (logging, elicitation) and passes the
connection's own `session_kwargs` to the transport session creators. The
sampling hook is a parameter of the `mcp` SDK's `ClientSession`; every
connection the assistant opens carries that callback under `session_kwargs`,
so the SDK's default sampling handler never applies. Tool names are not
prefixed with the server name by default.

## 8.3 Runtime Building Blocks

| Block | Lifetime | Notes |
|---|---|---|
| The uvicorn process | cluster lifetime | serves the FastAPI app on 8080; the container is configured once at import |
| The health probe thread | started on first `/health`, runs until the process dies | unjoinable by design; re-probes on a 300 s cadence; a failed round flips the status global |
| The factory runner | one workflow run | the pinned factory workflow, budgeted in loops and wall-clock |

## 8.4 Event Handling

| Trigger | Effect |
|---|---|
| Pull request to `main` | `test-and-lint.yml`: sets up Python 3.14 + uv, installs the dev extras, runs `make lint` then `make test` |
| `release: published` | `docker-image.yml`: builds `assistant/Dockerfile` and pushes it to ghcr.io tagged with the release tag, re-tagged `latest` |
| An issue is labeled (or manual dispatch) | `code-weaver.yml`: the factory run of scenario 4 |
| First `GET /health` | the background probe thread starts |

## 8.5 Performance

* The health probe repeats on a 300 s interval and re-opens a client per
  server per round.
* Each chat request costs one `langdetect` classification, two stage LLM
  calls (the preprocessing stage on the question, the postprocessing stage
  on the answer), two LLM rephrasing calls (question, answer) and one
  deep-agent round that may fan out into MCP tool calls; language detection
  and question rephrasing run in parallel graph branches behind the
  preprocessing node.
* The HTTP layer reports zero token usage by design; no per-request token
  accounting exists.
