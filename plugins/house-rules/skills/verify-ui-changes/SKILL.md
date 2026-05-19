---
name: verify-ui-changes
description: Use when editing rendered UI, dashboard, chart, or any visual artifact (Grafana, Terraform-generated panels, frontend components, plot output) - blocks declaring "done" without an external verification artifact.
---

# Verify UI Changes Before Declaring Done

## Why this skill exists

In prior sessions the same pattern repeated 20+ times: agent edited a chart /
dashboard / orderbook view, declared it fixed, the user came back with
"still not displaying / now shows No Data / repeated columns / still wrong".
The agent could not see the rendered output, so it kept guessing.

## When this fires

- File path matches `*.tsx`, `*.jsx`, `*.vue`, `*.svelte`, `dashboard*.tf`,
  `panel*.tf`, plot/chart code, `index.html`, or any file that produces a
  visual artifact.
- User uses words like "render", "display", "chart", "dashboard", "panel",
  "orderbook", "table", "plot", "screenshot", "preview", "looks like".

## Required behavior

Before declaring a visual change done, produce a verification artifact and
attach or describe it. Pick the cheapest applicable option:

| Stack | Verification |
|-------|--------------|
| Web frontend | `npm run dev`, hit the page, screenshot OR DOM snapshot (`document.querySelector(...).outerHTML`) |
| Rust plots (plotters/charming) | Run the example, list the output PNG, describe what it should contain |
| Terraform/Grafana | `terraform plan` then describe the resulting panel JSON or take a screenshot from the Grafana URL |
| TUI/CLI | Run with sample input, capture the rendered output |
| Tests pre-existing | Run the visual-regression / snapshot test |

If no artifact is achievable in the current environment, say so explicitly:
"I edited X but cannot verify the render from here - please confirm the
visual is correct before merging." Do not declare the task done.

## What "done" is NOT

- Code compiles -> not done.
- Tests pass -> not done (unless those tests cover the visual).
- "The change should produce the desired output" -> not done.
- A confident summary of what the diff does -> not done.

## Red flag

If you are about to write "this should now display correctly" without having
seen the actual output: stop, run the thing, capture the artifact, then
report.
