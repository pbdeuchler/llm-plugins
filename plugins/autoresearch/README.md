# autoresearch

Autonomous experiment loop that optimizes any measurable target. Point it at a metric, and it will iteratively try ideas, benchmark them, keep improvements, discard regressions, and log everything -- indefinitely or until a time/iteration limit is reached.

## Usage

```
/autoresearch:start [duration-minutes]
```

- `duration-minutes` -- (Optional) Stop after this many minutes. Omit for no limit.

New sessions prompt for an optimization target, benchmark command, metric name, direction (lower/higher is better), files in scope, and constraints. The plugin creates a branch, writes a benchmark script (`autoresearch.sh`), and begins looping.

Resumed sessions (when `autoresearch.md` already exists) pick up where they left off.

## How It Works

The main thread acts as a strategy controller. Each experiment runs in an isolated `experiment-runner` subagent to keep the main context clean:

1. **Setup** -- Gather parameters, create branch, write session files, run baseline.
2. **Loop** -- Decide hypothesis, dispatch subagent, parse result (`keep`/`discard`/`crash`/`checks_failed`), update strategy. Repeat.
3. **Shutdown** -- Commit final state, print summary with best result and commit hash.

Kept experiments are committed with structured metadata. Discarded experiments are reverted from the working tree but preserved in the JSONL log with descriptions and learnings (ASI).

## Session Files

| File | Purpose |
|------|---------|
| `autoresearch.md` | Session context: objective, metrics, files in scope, constraints, history |
| `autoresearch.sh` | Benchmark script outputting `METRIC name=value` lines |
| `autoresearch.checks.sh` | (Optional) Correctness validation run after each benchmark |
| `autoresearch.jsonl` | Canonical log of every experiment (survives reverts) |
| `autoresearch.ideas.md` | Backlog of ideas to try |
| `autoresearch.config.json` | (Optional) Runtime config: `maxIterations`, `maxDurationMinutes`, `workingDir` |

## Components

### Command: `start`

Entry point. Handles duration config, detects new vs resume, invokes the `autoresearch-create` skill.

### Skill: `autoresearch-create`

Orchestrates the full lifecycle: setup, loop control, subagent dispatch, strategy decisions, and graceful shutdown.

### Agent: `experiment-runner`

Sonnet-powered subagent that executes a single iteration. Reads files, implements changes, runs the benchmark, evaluates metrics, computes confidence, logs to JSONL, manages git state, and returns a structured result block.

### Sub-Skills (internal)

- **`confidence-scoring`** -- MAD-based statistical confidence to distinguish real improvements from noise.
- **`experiment-git-ops`** -- Git commit/revert patterns with protected session files.
- **`metric-extraction`** -- Parses `METRIC name=value` output lines, infers units, tracks primary vs secondary metrics.
- **`session-persistence`** -- JSONL logging, segment tracking, session init/resume/recovery.
