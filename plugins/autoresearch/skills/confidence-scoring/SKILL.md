---
name: confidence-scoring
description: Compute and interpret MAD-based confidence scores for experiment results. Use when logging experiment results after 3+ data points to determine if improvements are real or within noise.
user-invocable: false
---

# Confidence Scoring

Determines whether an observed improvement is real or within measurement noise using Median Absolute Deviation (MAD).

## When to Compute

- After **3+ experiment runs** in the current segment (including baseline).
- Skip if fewer than 3 runs with positive metric values — report `confidence: null`.

## Algorithm

Given all metric values in the current segment (positive values only):

1. **Sorted median**: Sort values, take middle element (or average of two middle elements for even count).
2. **MAD**: For each value, compute `|value - median|`. Take the sorted median of those absolute deviations.
3. **Baseline**: The metric value of the first experiment in the current segment.
4. **Best kept**: The best `keep`-status metric value (respecting optimization direction).
5. **Delta**: `|best_kept - baseline|`
6. **Confidence**: `delta / MAD`

### Edge Cases

- If MAD = 0 (all values identical): return `null` — no measurable noise to compare against.
- If no `keep` results exist yet: return `null`.
- If best kept equals baseline: return `null` — no improvement to score.

## Interpreting the Score

The confidence score is a multiple of the session's noise floor:

| Score | Meaning | Action |
|-------|---------|--------|
| ≥ 2.0× | Improvement likely real | Safe to trust |
| 1.0×–2.0× | Marginal — could be noise | Consider re-running to confirm |
| < 1.0× | Within noise floor | Treat as no improvement |

## How to Apply

When logging an experiment result to `autoresearch.jsonl`:

1. Collect all positive metric values from the current segment.
2. If count < 3, set `"confidence": null` in the JSONL record.
3. Otherwise, compute MAD and confidence as above.
4. Record the numeric confidence value in the JSONL entry.
5. When deciding `keep` vs `discard`: the confidence score is **advisory**. It never auto-discards. But flag improvements below 1.0× in your ASI notes as "within noise — may not be real."

## Example

```
Runs: [15200, 15400, 14800, 15100, 14600]
Median: 15100
Deviations: [100, 300, 300, 0, 500] → sorted: [0, 100, 300, 300, 500]
MAD: 300
Baseline: 15200 (first run)
Best kept: 14600
Delta: |14600 - 15200| = 600
Confidence: 600 / 300 = 2.0×  ← improvement is real
```
