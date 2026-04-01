---
name: holistic-review
description: Use when performing a holistic code review of an implementation - routes to codex:rescue or falls back to a direct subagent
---

# Holistic Review

Perform a holistic code review by routing to the best available review backend. Prefers `codex:rescue` when available; falls back to a direct `one-shot:holistic-reviewer` subagent.

## Required Context

You must have two pieces of information before invoking this skill:

- **Implementation plan path** — absolute path to the plan file
- **Base branch** — the branch or commitish to diff against (everything between base and HEAD is in scope)

If either is missing, stop and ask.

## Detection Gate

**Before doing anything else, determine whether `codex:rescue` is available.**

Scan your available skills/commands list (shown in your system context) for `codex:rescue`. Record the result explicitly in your response:

> codex:rescue: **AVAILABLE** / **NOT AVAILABLE**

You MUST write this line before proceeding. Do not skip it.

## Routing

### If AVAILABLE: use codex:rescue

**This is the primary path. You may not skip it when codex:rescue is available. Falling through to the fallback path when codex:rescue is detected is a failure.**

1. Read the `one-shot:holistic-reviewer` agent definition file in full. Codex does not have access to your agent files — you must inline the full text.

2. Invoke SkillTool('codex:rescue') with `--fresh`. Pass a single prompt containing all three of:
   - The full text of the holistic-reviewer agent definition
   - The absolute path to the implementation plan
   - The base branch to diff against

   ```
   You are performing a holistic code review. Follow the agent definition below exactly.

   ## Agent Definition

   {paste the FULL holistic-reviewer agent definition here}

   ## Review Parameters

   Implementation plan: {absolute_plan_path}
   Base branch: {base_branch}
   ```

### If NOT AVAILABLE: fallback to subagent

Spin up the `one-shot:holistic-reviewer` agent in a new subagent with a clean context. Provide the implementation plan path and the base branch.

```
<invoke name="Agent">
<parameter name="subagent_type">one-shot:holistic-reviewer</parameter>
<parameter name="description">Holistic code review</parameter>
<parameter name="prompt">
Perform a holistic review of the implementation.

Implementation plan: {absolute_plan_path}
Base branch: {base_branch}
</parameter>
</invoke>
```

3. **MANDATORY:** Address ALL issues from the holistic code review. Do not complete until all issues have been addressed. Loop through steps 2-3 until you get a clean code review.

## Common Mistakes

| Mistake                                                                   | Fix                                                                 |
| ------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| Skipping detection and going straight to the subagent fallback            | Always record the detection result first. The gate is mandatory.    |
| Summarizing the holistic-reviewer agent definition instead of inlining it | Codex has no access to your files. Paste the full text.             |
| Forgetting `--fresh` on codex:rescue                                      | Without it, Codex may resume a stale thread. Always pass `--fresh`. |
