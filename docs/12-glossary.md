# 12. Glossary

| Term | Meaning |
|---|---|
| **assistant** | The chat assistant application: the FastAPI app, its dependency container and the components composed by it |
| **base registry** | The `subclasses` tuple of a base API class (`BaseChatApi`, `BaseModelsApi`, `BaseAssistantApi`), filled automatically when an implementation subclass is imported; endpoints delegate to its first entry |
| **brownfield run** | A code-weaver run in which the requirements were extracted from existing code: all requirement files are new against the baseline, so the run scopes its steps to adjusting the tests to reference the extracted scenarios — no plan step implements product code |
| **chat graph** | The compiled LangGraph state graph (`ChatGraph`) that processes each request: `START` feeds `preprocessing`, which fans out to `determine_language` and `rephrase_question`, `rephrase_question` feeds `decide`, both predecessors converge into `rephrase_answer`, which feeds `postprocessing`, ending at `END` |
| **graph node** | One processing step of the chat graph, named by `GraphNodeNames` (`preprocessing`, `rephrase_question`, `determine_language`, `decide`, `rephrase_answer`, `postprocessing`) |
| **graph state** | The `GraphState` `TypedDict` carrying `question`, `history`, `raw_answer`, `processed_answer`, `question_language`, `additional_info` through the graph |
| **code-weaver factory** | The reusable GitHub workflow (`MelvinKl/code-weaver`) that turns issues labeled `code-weaver` into planned, implemented and reviewed pull requests; pinned in this repository to a version tag |
| **deep agent** | The agent created by `deepagents.create_deep_agent` and bound as `mcp_agent`: the main agent over the unassigned MCP tools, with the configured subagents attached |
| **feature file** | One Gherkin file under `requirements/`; the unit of the requirements oracle |
| **MCP** | The Model Context Protocol; the assistant connects to MCP servers to load their tools and offers its LLM back to them through sampling |
| **MCP server** | A tool provider configured in the MCP settings (name, transport, and either `command`/`args` for stdio or `url`/`headers` for remote transports, plus an optional `agent` assignment: `None` = main agent, a subagent name, or the `preprocessing`/`postprocessing` question answering stage) |
| **oracle** | The body of requirements the implementation is judged against; here, the 130 Gherkin scenarios in the 14 feature files under `requirements/` |
| **pull secret** | The Kubernetes `dockerconfigjson` secret (`pull-secret`) rendered from the `ghcrIo` chart values |
| **rephraser** | The `Rephraser` runnable: a system-plus-user prompt template rendered from a state dict, invoked sync or async against the LLM; bound as `question_rephraser` and `answer_rephraser` |
| **stage** | One of the question answering stages (`Stage`): a runnable LLM call carrying the stage's own system prompt (the preprocessing stage on the question, the postprocessing stage on the returned answer), the tools of the MCP servers available to the stage, and an optional SystemOne model; bound as `preprocessing` and `postprocessing` and wired into the chat graph |
| **scenario** | One `Scenario:` block of a feature file — the smallest unit of requirement and of oracle alignment |
| **scenario reference** | The citation a test carries in its docstring for the scenario it implements, in one of the two machine forms (`Implements "<title>" (requirements/<file>.feature)` or `requirements/<file>.feature::<title>`) |
| **coverage guard** | `tests/test_scenario_coverage.py`: verifies every extracted scenario is referenced by at least one test (parametrised per feature file) and that no test references a scenario absent from `requirements/` |
| **sampling** | The MCP capability that lets an attached server ask the assistant LLM for a completion; served by `create_sampling_callback`, hooked on the `mcp` SDK's `ClientSession` |
| **settings family** | One pydantic-settings module with an environment-variable prefix and `.env` support (OpenAI, prompts, additional information, API, MCP servers, subagents, SystemOne) |
| **subagent** | A specialized agent configured in the subagents settings (`name`, `description`, `system_prompt`); it receives the tools of the MCP servers whose `agent` field names it |
| **SystemOne** | The optional model a question answering stage may run on (`SystemOneSettings`, environment family `SETTINGS_SYSTEM_ONE_*`): when configured, the stage LLM is a `ChatOpenAI` created from it, the tools available to the stage LLM are limited to the tools of the stage's available MCP servers, and the MCP servers available to the stage are filtered by the model when the stage LLM is created (only the servers it keeps contribute their tools); the chat graph consults the model at invocation to determine whether the user's goal can be reached at all with the available MCP servers — an unreachable goal short-circuits the invocation to the answer that no MCP servers are currently available to help, skipping the stages up to the answer generation; a stage without one runs on the main LLM and the graph runs without the reachability determination |
| **tool** | An MCP server tool loaded into the agent's tool set, grouped under the server's agent key (`None` = main agent, a subagent name, or the `preprocessing`/`postprocessing` stage) |
| **arc42** | The documentation template this `docs/` tree follows: 13 chapters, one file each |
