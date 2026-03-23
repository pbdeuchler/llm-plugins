---
name: session-persistence
description: Manage autoresearch.jsonl logging, session initialization, segment tracking, and session recovery. Use when starting, resuming, or recording experiments.
user-invocable: false
---

# Session Persistence

All experiment data is persisted to `autoresearch.jsonl` in JSONL format (one JSON object per line). This file survives across discards, crashes, and context resets — it is the canonical record of everything tried.

## JSONL Record Types

### Config Header

Written once at session init (and again on re-initialization when the optimization target changes):

```json
{"type":"config","name":"<session name>","metricName":"<primary metric>","metricUnit":"<unit>","bestDirection":"<lower|higher>"}
```

| Field | Type | Description |
|-------|------|-------------|
| `type` | `"config"` | Distinguishes from experiment records |
| `name` | string | Human-readable session name |
| `metricName` | string | Primary metric name (must match METRIC output) |
| `metricUnit` | string | Display unit (inferred or explicit) |
| `bestDirection` | `"lower"` or `"higher"` | Optimization direction |

### Experiment Record

Written after every experiment (keep, discard, crash, or checks_failed):

```json
{"run":5,"commit":"a1b2c3d","metric":14600,"metrics":{"compile_µs":4100},"status":"keep","description":"Inline hot loop","timestamp":1699564800000,"segment":0,"confidence":2.3,"asi":{"hypothesis":"inlining reduces call overhead"}}
```

| Field | Type | Description |
|-------|------|-------------|
| `run` | number | Sequential experiment number (1-indexed) |
| `commit` | string | Git short hash (7 chars) for `keep`; empty string for others |
| `metric` | number | Primary metric value (0 for crashes) |
| `metrics` | object | Secondary metric name→value pairs |
| `status` | string | `"keep"`, `"discard"`, `"crash"`, or `"checks_failed"` |
| `description` | string | What was tried this run |
| `timestamp` | number | Milliseconds since epoch (`date +%s000` in bash) |
| `segment` | number | Current segment index (0-indexed) |
| `confidence` | number or null | Confidence score (null if < 3 runs) |
| `asi` | object or null | Agent-supplied intelligence (free-form key-value) |

## Segments

A **segment** groups experiments under a single baseline and config. Segments increment when `init_experiment` is called again (e.g., when the optimization target changes mid-session).

- Segment 0: experiments from initial setup
- Segment 1+: experiments after re-initialization

Confidence scoring and baseline comparisons only consider experiments within the current segment.

## Session Recovery

When resuming (context reset, crash, or explicit resume):

1. **Read `autoresearch.jsonl`** line by line.
2. **Parse config headers**: Each `"type":"config"` line starts a new segment. Extract `metricName`, `metricUnit`, `bestDirection`.
3. **Parse experiment records**: Reconstruct the results list with all fields. Track which segment each belongs to.
4. **Rebuild secondary metrics**: Collect all unique keys from `metrics` objects across the current segment.
5. **Find baseline**: First experiment record in the current segment.
6. **Find best kept**: Best `keep`-status metric in the current segment (respecting direction).
7. **Compute run count**: Total experiment records (to set the next `run` number).
8. **Resume looping** from where the session left off.

Also read `autoresearch.md` and `autoresearch.ideas.md` for context on what was tried and what ideas remain.

## Writing Records

When logging an experiment:

1. Compute all fields (including confidence via the confidence-scoring skill).
2. Serialize as a single JSON line (no pretty-printing, no trailing newline between records).
3. **Append** to `autoresearch.jsonl` — never overwrite the file.
4. The JSONL file is the only record that survives discarded/crashed experiments. Every run must be logged before any git revert happens.

## Reporting

After logging, print a one-line summary:

```
Run #5: keep | total_µs: 14,600 (-3.8%) | confidence: 2.3× | "Inline hot loop"
```

Components:
- Run number and status
- Primary metric with delta % vs baseline
- Confidence score (if available)
- Description (truncated if long)

After every 5 runs or on shutdown, print an expanded summary showing all runs in the current segment with their status, metrics, and descriptions.
