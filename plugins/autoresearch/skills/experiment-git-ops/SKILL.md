---
name: experiment-git-ops
description: Git commit and revert patterns for autoresearch experiments. Use when keeping or discarding experiment results to manage git state correctly.
user-invocable: false
---

# Experiment Git Operations

Manages git state during the autoresearch loop. Successful experiments are committed with structured metadata. Failed experiments are reverted while preserving autoresearch state files.

## Protected Files

These files are **never reverted**, regardless of experiment outcome:

- `autoresearch.jsonl`
- `autoresearch.md`
- `autoresearch.ideas.md`
- `autoresearch.sh`
- `autoresearch.checks.sh`

## On `keep` — Commit

When an experiment improves the primary metric:

1. Stage all changes: `git add -A`
2. Check if there are staged changes: `git diff --cached --quiet` (exit code 1 = changes exist)
3. If changes exist, commit with structured message:

```
<description>

Result: {"status":"keep","<metric_name>":<value>,<secondary_metrics>}
```

The `Result:` trailer is a JSON object containing:
- `status`: always `"keep"`
- Primary metric: key is the metric name, value is the numeric result
- Secondary metrics: each as key-value pairs

**Example commit message:**
```
Inline hot loop in render phase

Result: {"status":"keep","total_µs":14600,"compile_µs":4100,"render_µs":9500}
```

4. If no changes to commit (pure measurement variation), skip the commit but still log to JSONL.

## On `discard`, `crash`, or `checks_failed` — Revert

When an experiment fails or doesn't improve:

1. **Stage protected files first** (so they survive the revert):

```bash
git add autoresearch.jsonl autoresearch.md autoresearch.ideas.md autoresearch.sh autoresearch.checks.sh 2>/dev/null || true
```

2. **Stash protected files, revert everything, restore them:**

```bash
git stash push -- autoresearch.jsonl autoresearch.md autoresearch.ideas.md autoresearch.sh autoresearch.checks.sh 2>/dev/null || true
git checkout -- .
git clean -fd 2>/dev/null
git stash pop 2>/dev/null || true
```

This restores the working tree to the last committed state while keeping all autoresearch state files intact.

## Branch Management

- **New session**: Create branch `autoresearch/<goal>-<YYYY-MM-DD>` from current HEAD.
- **Resume**: Stay on the existing autoresearch branch.
- **Graceful shutdown**: Commit all autoresearch files before stopping.

## Why This Matters

Discarded and crashed experiments are **completely erased** from the working tree. The only surviving record is the description and ASI in `autoresearch.jsonl`. This is why heavy annotation of failures is critical — without it, future iterations will re-discover the same dead ends.
