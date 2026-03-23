---
name: autoresearch-create
description: Set up and run an autonomous experiment loop for any optimization target. Gathers what to optimize, then starts the loop immediately. Use when asked to "run autoresearch", "optimize X in a loop", "set up autoresearch for X", or "start experiments".
---

# Autoresearch

Autonomous experiment loop: try ideas, keep what works, discard what doesn't, never stop.

**Architecture:** The main thread is a lightweight loop controller. Each experiment iteration runs in an `experiment-runner` subagent to keep the main context clean and unbounded.

## Sub-Skills (Reference)

These skills contain detailed protocols. The `experiment-runner` subagent follows them directly. The main thread references them only when needed for setup or recovery:

- **`autoresearch:confidence-scoring`** — MAD-based confidence computation and interpretation.
- **`autoresearch:experiment-git-ops`** — Git commit/revert patterns with protected files.
- **`autoresearch:metric-extraction`** — METRIC line parsing, unit inference, tracking.
- **`autoresearch:session-persistence`** — JSONL logging, session init/resume, segment tracking.

## Phase 1: Setup (Main Thread)

Run once at session start. This is the only phase where the main thread does heavy file work.

1. **Gather parameters.** Ask (or infer): Goal, Command, Metric (+ direction), Files in scope, Constraints.
2. **Branch.** `git checkout -b autoresearch/<goal>-<YYYY-MM-DD>`
3. **Read source files.** Understand the workload deeply before writing anything.
4. **Write `autoresearch.md`.** The heart of the session (see template below).
5. **Write `autoresearch.sh`.** Benchmark script outputting `METRIC name=value` lines.
6. **Write `autoresearch.checks.sh`** (only if constraints require correctness validation).
7. **Commit** all autoresearch files.
8. **Write config header** to `autoresearch.jsonl`:
   ```json
   {"type":"config","name":"<session>","metricName":"<name>","metricUnit":"<unit>","bestDirection":"<lower|higher>"}
   ```
9. **Record start timestamp**: `date +%s` — store for duration limit checks.
10. **Run baseline** via the first subagent dispatch (see Phase 2). The baseline description should be "Baseline measurement".

### `autoresearch.md` Template

```markdown
# Autoresearch: <goal>

## Objective
<Specific description of what we're optimizing and the workload.>

## Metrics
- **Primary**: <name> (<unit>, lower/higher is better) — the optimization target
- **Secondary**: <name>, <name>, ... — independent tradeoff monitors

## How to Run
`./autoresearch.sh` — outputs `METRIC name=number` lines.

## Files in Scope
<Every file the agent may modify, with a brief note on what it does.>

## Off Limits
<What must NOT be touched.>

## Constraints
<Hard rules: tests must pass, no new deps, etc.>

## What's Been Tried
<Update as experiments accumulate — key wins, dead ends, architectural insights.>
```

### `autoresearch.sh`

Bash script (`set -euo pipefail`) that pre-checks fast, runs the benchmark, and outputs structured `METRIC name=value` lines. For fast noisy benchmarks (<5s), run multiple times and report median.

### `autoresearch.config.json` (optional)

```json
{
  "workingDir": "/path/to/project",
  "maxIterations": 50,
  "maxDurationMinutes": 120
}
```

## Phase 2: Loop (Main Thread as Controller)

The main thread is a **strategy controller**. It decides what to try, dispatches a subagent to execute it, and processes the result. The main thread NEVER modifies source files or runs benchmarks directly.

**CONTINUE LOOPING UNTIL EITHER USER INTERRUPT OR TIME/ITERATION LIMIT.** Never ask "should I continue?"

### Loop Iteration

```
┌─────────────────────────────────────────────┐
│  MAIN THREAD (controller)                   │
│                                             │
│  1. Check stop conditions                   │
│  2. Read recent state (JSONL tail + ideas)  │
│  3. Decide hypothesis for next experiment   │
│  4. Dispatch experiment-runner subagent      │
│  5. Parse result block from subagent        │
│  6. Update strategy based on result         │
│  7. Every 5 runs: update autoresearch.md    │
│  8. Go to 1                                 │
└─────────────────────────────────────────────┘
         │
         ▼  (dispatch)
┌─────────────────────────────────────────────┐
│  SUBAGENT: experiment-runner                │
│                                             │
│  - Reads files, implements changes          │
│  - Runs benchmark + checks                  │
│  - Evaluates metrics, computes confidence   │
│  - Logs to JSONL                            │
│  - Commits or reverts git state             │
│  - Returns structured result block          │
└─────────────────────────────────────────────┘
```

### Step 1: Check Stop Conditions

Before each iteration:
- If `maxIterations` is set and reached → graceful shutdown.
- Run `date +%s`, compare to start timestamp. If `maxDurationMinutes` exceeded → graceful shutdown.

### Step 2: Read Recent State

Read the **last 10 lines** of `autoresearch.jsonl` to understand recent results. Also check `autoresearch.ideas.md` for queued ideas. This is lightweight — do NOT re-read the entire file each iteration.

### Step 3: Decide Hypothesis

Based on accumulated results, decide what to try next. This is where the main thread's strategic value lives:

- **After a `keep`:** Build on the improvement. What's the next bottleneck?
- **After a `discard`:** Try a structurally different approach. Don't thrash on the same idea.
- **After a `crash`:** Fix if trivial, otherwise skip and try something else.
- **After 3+ consecutive discards:** Step back. Re-read source files. Think about what the CPU/runtime is actually doing.
- **Confidence < 1.0×:** Recent "improvements" may be noise. Try larger, more impactful changes.
- **Ideas backlog:** Pull from `autoresearch.ideas.md` when you need fresh directions.

### Step 4: Dispatch Subagent

Spawn `autoresearch:experiment-runner` with a prompt containing all context needed for one iteration:

<invoke name="Agent">
<parameter name="subagent_type">autoresearch:experiment-runner</parameter>
<parameter name="description">Run #N: brief hypothesis</parameter>
<parameter name="prompt">
## Experiment Context

- **Run number**: {N}
- **Working directory**: {working_dir}
- **Primary metric**: {metric_name} ({unit}, {direction} is better)
- **Baseline**: {baseline_value}
- **Best so far**: {best_value} (run #{best_run})
- **Current segment**: {segment}

## Hypothesis

{What to try and why — be specific about which files to change and what changes to make.}

## Files in Scope

{Copy from autoresearch.md — every file the agent may modify.}

## Off Limits

{Copy from autoresearch.md.}

## Constraints

{Copy from autoresearch.md.}

## Recent History (last 5 runs)

{Formatted summary: run#, status, metric, description, asi — from JSONL tail.}
</parameter>
</invoke>

**Keep the prompt concise.** The subagent doesn't need the full session history — just enough to execute one iteration well.

### Step 5: Parse Result

The subagent ends with a `result` block:

```
status: keep|discard|crash|checks_failed
metric: <value>
confidence: <score_or_null>
commit: <hash_or_empty>
description: <what was tried>
asi: <what was learned>
secondary: key1=val1 key2=val2
```

Parse these fields to update your running state.

### Step 6: Update Strategy

Print a one-line summary to the user:

```
Run #5: keep | total_µs: 14,600 (-3.8%) | confidence: 2.3× | "Inline hot loop"
```

Adjust your internal strategy:
- Track consecutive discards/crashes.
- Note patterns in ASI across runs.
- Add deferred ideas to `autoresearch.ideas.md`.

### Step 7: Periodic Maintenance

Every **5 runs**, update `autoresearch.md`:
- Refresh "What's Been Tried" with key wins, dead ends, and architectural insights.
- Commit the updated file.

This ensures a fresh agent (or context recovery) has current state.

## Phase 3: Graceful Shutdown (Main Thread)

When a stop condition is reached:

1. **Wait for current subagent** to finish — don't abandon a running experiment.
2. **Update `autoresearch.md`** with final state, total iterations, best result, promising unexplored ideas.
3. **Commit** all autoresearch files.
4. **Print summary:**
   - Iterations completed
   - Best result (metric value + description + commit hash)
   - Elapsed time
   - Reason for stopping

## Resuming a Session

When `autoresearch.md` exists (resume scenario):

1. Read `autoresearch.md` for session context.
2. Read `autoresearch.jsonl` to reconstruct state (see `session-persistence` skill):
   - Find current segment, baseline, best kept, run count.
3. Read `autoresearch.ideas.md` for queued ideas.
4. Check git log for recent commits.
5. Record new start timestamp for duration tracking.
6. **Resume looping** from Phase 2.

## Strategy Guidelines

- **Primary metric is king.** Improved → keep. Worse/equal → discard. Secondary metrics are informational.
- **Simpler is better.** Removing code for equal perf = keep. Ugly complexity for tiny gain = probably discard.
- **Don't thrash.** Same idea failing repeatedly → try something structurally different.
- **Think longer when stuck.** Re-read source files, study profiling data, reason about what the workload actually does. The best ideas come from deep understanding, not random variation.
- **Annotate heavily.** The main thread accumulates ASI across runs — this is your institutional memory. Use it to avoid repeating dead ends.

## User Messages During Experiments

If the user sends a message while a subagent is running, wait for the subagent to finish, then incorporate their feedback into the next hypothesis.
