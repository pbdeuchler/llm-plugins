# llm-plugins

Claude Code plugins for design, implementation, and development workflows. Largely stolen from [ed3d-plugins](https://github.com/ed3dai/ed3d-plugins), [ToB](https://github.com/trailofbits/skills), [davebcn87](https://github.com/davebcn87/pi-autoresearch) and ever so slightly modified.

## Plugins

### autoresearch

Autonomous experiment loop that optimizes any measurable target. Point it at a metric and it iteratively tries ideas, benchmarks them, keeps improvements, and discards regressions -- logging everything to a structured JSONL file. Runs indefinitely or until a time/iteration limit. Each experiment executes in an isolated subagent to keep the main context clean.

```
/autoresearch:start [duration-minutes]
```

### blank-slate-review

Multi-perspective engineering review of any codebase -- or a scoped subset -- from a single command. A Haiku-powered scout maps the structure, then an Opus-powered panel of staff engineers reviews sampled files across seven dimensions (correctness, consistency, simplicity, design principles, idiomatic usage, security, test quality) and returns severity-classified findings with holistic remediation prose. For large codebases, files are partitioned by module and reviewed in parallel.

```
/blank-slate-review:start [scope]
```

### quick-plan

Tightly scoped implementation planning with a panel of specialist engineer subagents. Creates plans of 5 steps or fewer, each roughly one story point, ready to hand off to an implementer. Five specialist agents (systems performance, distributed systems, security, infra ops, product lead) evaluate approaches from their domain at specific process steps.

```
/quick-plan:start [basic prompt]
```

### one-shot

Executes an implementation plan end-to-end in a single session: creates a branch, implements each step with TDD, runs per-step code review (fixing all severity levels), performs a holistic final review via a multi-persona staff engineer panel (with optional dueling-model review via Codex), and opens a PR. Rejects plans too large or vague to complete in 5 steps at a high quality bar.

```
/one-shot:start <absolute-plan-file-path> [seed-commitish]
```

### house-style

Opinionated development guides covering coding patterns, testing strategies, database access, and technical writing. Skills activate automatically when relevant -- functional core / imperative shell, defense in depth, property-based testing, PostgreSQL conventions, and more.

```
/plugin install house-style@llm-plugins
```

### tooling

Reference skills for developer tools: `ast-grep` for structural code search and transformation, and `qmd` for searching markdown knowledge bases. Loaded automatically when relevant tool usage is detected.

```
/plugin install tooling@llm-plugins
```

## Installation

### Add the marketplace

```bash
/plugin marketplace add https://github.com/pbdeuchler/llm-plugins.git
```

### Install plugins

All plugins are available from the `llm-plugins` marketplace:

```bash
/plugin install autoresearch@llm-plugins
/plugin install blank-slate-review@llm-plugins
/plugin install house-style@llm-plugins
/plugin install one-shot@llm-plugins
/plugin install quick-plan@llm-plugins
/plugin install tooling@llm-plugins
```
