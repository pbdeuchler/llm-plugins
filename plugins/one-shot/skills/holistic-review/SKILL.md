---
name: holistic-review
description: Use when performing a holistic code review of an implementation - routes to codex:rescue or falls back to a direct subagent, both running the house-style:holistic-review skill
context: fork
allowed-tools: Bash(node *), Bash(find *), Read(*)
---

# Holistic Review

Perform a holistic code review by routing to the best available review backend. The review methodology itself lives in the `house-style:holistic-review` skill -- this skill only decides where it runs. Prefers `codex:rescue` when available; falls back to a direct subagent.

## Required Context

You should have two pieces of information before invoking this skill:

- **Implementation plan path** -- absolute path to the plan file
- **Base branch** -- the branch or commitish to diff against (everything between base and HEAD is in scope)

If the plan path is missing, stop and ask. If the base branch is missing, the reviewer will resolve it (origin/HEAD, else `main`/`master`) -- pass it through as "not provided".

## Dependency Gate

This skill requires the `house-style` plugin. Scan your available skills list for `house-style:holistic-review`. If it is not present, stop and report that the house-style plugin must be installed (`/plugin install house-style@llm-plugins`).

## Detection Gate

**Before doing anything else, determine whether `codex:rescue` is available.**

Scan your available skills/commands list (shown in your system context) for `codex:rescue`. Record the result explicitly in your response:

> codex:rescue: **AVAILABLE** / **NOT AVAILABLE**

You MUST write this line before proceeding. Do not skip it.

## Routing

### If AVAILABLE: use codex:rescue

**This is the primary path. You may not skip it when codex:rescue is available. Falling through to the fallback path when codex:rescue is detected is a failure.**

1. Resolve the fully qualified path of the house-style skill file:

   ```bash
   find ~/.claude/plugins -path '*house-style*skills/holistic-review/SKILL.md' -print -quit
   ```

   If nothing is found, fall back to the subagent path below.

2. Invoke SkillTool("/codex:rescue --fresh --foreground \"{prompt}\"). Pass a prompt (the {prompt} variable) containing all three of:
   - The resolved path of the house-style holistic-review skill file
   - The absolute path to the implementation plan
   - The base branch to diff against

   ```
   You are performing a holistic code review. Follow this skill definition exactly. READ THIS SKILL DEFINITION: {paste the FULLY QUALIFIED house-style holistic-review SKILL.md path here}

   Review Parameters:

   - Implementation plan: {absolute_plan_path}
   - Base branch: {base_branch}
   ```

### If NOT AVAILABLE: fallback to subagent

Spin up a general-purpose subagent with a clean context. It must load the house-style skill and follow it exactly.

```
<invoke name="Task">
<parameter name="subagent_type">general-purpose</parameter>
<parameter name="description">Holistic code review</parameter>
<parameter name="prompt">
You are performing a holistic code review. Invoke the Skill tool with `house-style:holistic-review` and follow that skill exactly, including its output contract. Do not fix any code; report findings only.

Review Parameters:

- Implementation plan: {absolute_plan_path}
- Base branch: {base_branch}

Return the full review report as your final message.
</parameter>
</invoke>
```

## After the Review

**MANDATORY:** Address ALL issues from the holistic code review. Do not complete until all issues have been addressed. Loop back through Routing after fixing until you get a clean (PASS) review.

## Common Mistakes

| Mistake                                                          | Fix                                                                  |
| ---------------------------------------------------------------- | -------------------------------------------------------------------- |
| Skipping detection and going straight to the subagent fallback   | Always record the detection result first. The gate is mandatory.     |
| Running the review inline in this fork instead of routing it     | This context carries implementation bias. Always route to codex or a clean subagent. |
| Forgetting `--fresh` on codex:rescue                             | Without it, Codex may resume a stale thread. Always pass `--fresh`.  |
