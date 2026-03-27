# quick-plan

Tightly scoped implementation planning with a panel of specialist engineer subagents. Creates high-quality plans of 5 steps or fewer, each roughly one story point, ready to hand off to an implementer (or to `one-shot:start`).

## Usage

```
/quick-plan:start [basic prompt]
```

If no prompt is provided you'll be asked for one. The command creates a branch, picks a plan file location, and launches the planning skill.

## How it works

The planning session is framed as a meeting of staff engineers, each with a distinct specialty:

| Agent | Focus |
|-------|-------|
| `systems-performance` | Hot paths, allocation pressure, cache behavior, resource usage |
| `distributed-systems` | Module boundaries, contracts, cross-service interactions, consistency |
| `security-engineer` | Trust boundaries, input surfaces, credential handling, escalation paths |
| `infra-operations` | Deployability, rollback safety, observability, debuggability |
| `product-lead` | Strategic fit, scope assessment, future flexibility, extensibility |

Agents are dispatched at specific process steps where their expertise matters, with parallel dispatch where concerns are independent.

## Process

1. **Context Gathering** -- `distributed-systems` investigates the codebase
2. **Data Models & Boundaries** -- identify types, API shapes, and architecture decisions
3. **Broader Context** -- `product-lead` and `infra-operations` evaluate strategic and operational fit
4. **Clarification** -- structured questions to the user (decisions, unknowns, references)
5. **Multiple Approaches** -- `systems-performance` and `security-engineer` evaluate tradeoffs
6. **Pick a Path** -- present annotated approaches, user decides
7. **Split into Steps** -- discrete, independently shippable, dependency-ordered steps
8. **Acceptance Criteria** -- observable outcomes per step and overall definition of done
9. **Final Review** -- interactive walkthrough with the user

## Output

A plan file written to the project's docs/plans directory, ready for implementation. If `one-shot` is installed, a helper command is printed for immediate execution.

## Installation

```bash
/plugin install quick-plan@llm-plugins
```
