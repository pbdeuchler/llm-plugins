---
name: metric-extraction
description: Parse METRIC output lines, infer units, and track primary vs secondary metrics. Use when processing experiment output from autoresearch.sh.
user-invocable: false
---

# Metric Extraction

Parses structured output from `autoresearch.sh` to extract primary and secondary metrics.

## Output Format

Each metric is a single line matching:

```
METRIC <name>=<value>
```

- **Name**: word characters (`a-z`, `A-Z`, `0-9`, `_`), dots (`.`), or `µ`. Examples: `total_µs`, `compile_ms`, `cache.hits`
- **Value**: any token parseable as a finite number. `NaN`, `Infinity`, and non-numeric values are silently ignored.
- One metric per line. Lines not starting with `METRIC` are ignored (but may contain useful diagnostics).
- If a name appears multiple times, the **last occurrence wins**.

## Primary vs Secondary

- **Primary metric**: The one whose name matches what was declared at session init (the optimization target). This is what determines `keep` vs `discard`.
- **Secondary metrics**: All other `METRIC` lines. Tracked for tradeoff monitoring but don't affect keep/discard decisions.

If the primary metric is missing from output, treat the run as a **crash** — the benchmark didn't produce the expected data.

## Unit Inference

Infer units from metric name suffixes for display and context:

| Suffix | Unit |
|--------|------|
| `µs` | µs (microseconds) |
| `_ms` | ms (milliseconds) |
| `_s` or `_sec` | s (seconds) |
| `_kb` | kb (kilobytes) |
| `_mb` | mb (megabytes) |
| (none matched) | (unitless) |

Units are informational — they don't affect computation.

## Tracking Across Runs

Maintain a list of known secondary metrics discovered across the session. When a new metric name appears in output that hasn't been seen before, register it with its inferred unit. This allows consistent reporting even when scripts evolve during the loop.

## Recording in JSONL

When logging an experiment, record metrics as:

```json
{
  "metric": 14600,
  "metrics": {
    "compile_µs": 4100,
    "render_µs": 9500,
    "cache.hits": 42
  }
}
```

- `metric`: the primary metric's numeric value (top-level for easy querying)
- `metrics`: object of all secondary metric name→value pairs

## Designing Informative Output

The `autoresearch.sh` script should output whatever helps the agent make better decisions:

- **Phase timings** when the workload has distinct stages
- **Error counts or categories** when correctness can fail in different ways
- **Memory/cache diagnostics** when relevant to the optimization
- **Domain-specific signals** that help localize regressions

The script can be updated during the loop as you learn what signal matters. Add instrumentation when you need more data to decide where to focus next.
