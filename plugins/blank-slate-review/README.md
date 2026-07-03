# blank-slate-review

Multi-perspective engineering review of any codebase -- or a scoped subset -- from a single command. A scout maps the structure, then an Opus-powered panel of staff engineers reviews sampled files across seven dimensions and returns severity-classified findings with holistic remediation prose.

## Usage

```
/blank-slate-review:start [scope]
```

- `scope` -- (Optional) Directory path, file glob, or single file to review. Defaults to the project root.

The command validates the scope, dispatches a scout to map codebase structure, samples representative files, and runs one or more reviewer agents. Findings print to stdout; you're offered the option to write them to a file.

## How it works

### Scout Phase

A Haiku-powered scout subagent maps the codebase without reading every file: languages, frameworks, entry points, test locations, file counts by type. This structural inventory drives file sampling and the fan-out decision.

### Review Phase

An Opus-powered agent embodies a panel of staff engineers who discuss findings from different perspectives before converging on structured output. The panel reviews sampled files across seven dimensions:

| Dimension | Focus |
|-----------|-------|
| Correctness | Logic errors, race conditions, error handling, edge cases |
| Consistency | Naming, patterns, conventions, style uniformity |
| Simplicity | Over-engineering, unnecessary abstractions, dead code |
| Design Principles | State management, side effects, modularity, dependency direction |
| Idiomatic Usage | Language/framework conventions, deprecated APIs, anti-patterns |
| Security | Input validation, injection vectors, credential handling, trust boundaries |
| Test Quality | Coverage, assertion quality, happy/sad paths, isolation |

### Fan-out

For large codebases, the skill partitions files by module and dispatches multiple reviewer agents in parallel. Results are deduplicated and merged.

### Output

Findings are severity-classified:

| Severity | Criteria |
|----------|----------|
| **CRITICAL** | Broken correctness, data loss, security vulnerability |
| **HIGH** | Meaningful quality issue, design violation, missing edge case handling |
| **MEDIUM** | Inconsistency, moderate complexity concern, test gap |
| **LOW** | Style, naming, minor readability improvements |

Findings are followed by holistic remediation prose that groups related issues into cross-cutting themes rather than per-issue prescriptions.

## Design Decisions

- **Observation only** -- No code is written, no PRs created, no plans generated. Pure review.
- **Four severity levels** -- Finer granularity than house-style holistic-review's three levels, appropriate for a standalone review with no fix-and-re-review loop.
- **Holistic remediation** -- Groups findings into systemic themes rather than prescribing individual fixes, helping engineers see the forest not just the trees.
- **Scout before review** -- Structural mapping avoids wasting reviewer context on irrelevant files and enables intelligent sampling.
- **Fan-out for scale** -- Large codebases are partitioned by module so each reviewer operates within effective context limits.

## Installation

```bash
/plugin install blank-slate-review@llm-plugins
```
