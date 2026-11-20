# Chat Assistant — arc42 Documentation

This tree is the arc42 documentation for the chat assistant repository. Every
chapter is its own file:

| Chapter | File | Contents |
|---|---|---|
| 1. Introduction | [01-introduction.md](01-introduction.md) | Purpose, quality goals, scope, references |
| 2. Stakeholders | [02-stakeholders.md](02-stakeholders.md) | Actors and related projects |
| 3. Goals | [03-goals.md](03-goals.md) | Project goals, quality goals, out-of-scope items |
| 4. Constraints | [04-constraints.md](04-constraints.md) | Technical and organisational constraints |
| 5. Solution Strategy | [05-solution-strategy.md](05-solution-strategy.md) | Key forces and key decisions |
| 6. System Context | [06-system-context.md](06-system-context.md) | Technical context: cluster, MCP servers, code-weaver factory |
| 7. Solution Strategy (structure) | [07-solution-structure.md](07-solution-structure.md) | Building blocks, allocation, interfaces, cross-cutting concepts |
| 8. Runtime Behavior | [08-runtime-behavior.md](08-runtime-behavior.md) | Key scenarios: chat flow, MCP loading and sampling, health probes, factory run |
| 9. Deployment | [09-deployment.md](09-deployment.md) | Topology, infrastructure, load balancing, provisioning, monitoring |
| 10. Quality | [10-quality.md](10-quality.md) | Quality requirements, the executable Gherkin oracle, quality scenarios |
| 11. Technical Risks | [11-technical-risks.md](11-technical-risks.md) | Known technical risks and recorded inconsistencies |
| 12. Glossary | [12-glossary.md](12-glossary.md) | Domain terms |
| 13. References | [13-references.md](13-references.md) | Source documents and external projects |

**Note on provenance.** This documentation tree was established during the
brownfield test-oracle alignment run of issue 11 (see `plans/11.md`): before
that run, this repository carried no arc42 documentation. The content
describes the code as it exists at that point — including the scenario
coverage guard `assistant/tests/test_scenario_coverage.py` introduced by the
first step of that run — and treats the Gherkin files under `requirements/`
(14 feature files, 131 scenarios) as the executable requirements oracle.
Where the `README.md` and the repository tree disagree (for example the
`components/` directory the README lists that is not present in the tree),
this documentation follows the tree and records the discrepancy in chapter 11.
