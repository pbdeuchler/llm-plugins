# llm-plugins

Claude Code plugins for design, implementation, and development workflows. Largely stolen from [ed3d-plugins](https://github.com/ed3dai/ed3d-plugins), [ToB](https://github.com/trailofbits/skills), [davebcn87](https://github.com/davebcn87/pi-autoresearch) and ever so slightly modified.

## Plugins

### autoresearch

Autonomous experiment loop that optimizes any measurable target. Point it at a metric and it iteratively tries ideas, benchmarks them, keeps improvements, and discards regressions -- logging everything to a structured JSONL file. Runs indefinitely or until a time/iteration limit. Each experiment executes in an isolated subagent to keep the main context clean.

```
/autoresearch:start [duration-minutes]
```

### house-style

Opinionated development guides covering coding patterns, testing strategies, database access, and technical writing. Skills are activated automatically when relevant -- functional core / imperative shell, defense in depth, property-based testing, PostgreSQL conventions, and more.

```
/plugin install house-style@llm-plugins
```

### one-shot

Executes an implementation plan end-to-end in a single session: creates a branch, implements each step with TDD, runs per-step code review (fixing all severity levels), performs a holistic final review, and opens a PR. Rejects plans too large or vague to complete in 5 steps at a high quality bar.

```
/one-shot:start <absolute-plan-file-path> [seed-commitish]
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
/plugin install house-style@llm-plugins
/plugin install one-shot@llm-plugins
/plugin install tooling@llm-plugins
```
