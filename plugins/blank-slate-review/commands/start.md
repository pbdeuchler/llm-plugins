---
description: Run a structured multi-perspective codebase review with severity-classified findings
argument-hint: "[scope: directory, glob, or file]"
---

# Blank-Slate Codebase Review

**Scope:** `$ARGUMENTS`

## Before Starting

Validate the review scope. If no scope was provided, the review covers the entire project root.

1. Verify we are in a git repo:

   ```bash
   git rev-parse --git-dir
   ```

2. If a scope argument was provided, validate it exists:

   - If it looks like a directory path, verify it exists:
     ```bash
     test -d "$1"
     ```
   - If it looks like a file path, verify it exists:
     ```bash
     test -f "$1"
     ```
   - If it looks like a glob pattern (contains `*`, `?`, or `[`), verify it matches at least one file:
     ```bash
     ls $1 2>/dev/null | head -1
     ```

   If validation fails, stop and tell the user the scope does not match anything.

3. If no scope was provided, set the scope to the current working directory (project root).

## Execute

**Engage the skill:** Use your Skill tool to invoke `blank-slate-review:execute-review`.

The skill handles everything from here: scout dispatch, file sampling, review, and output. Pass it the validated scope.

Do not add context, commentary, or additional prompts beyond what the skill requests. The review pipeline manages its own context to keep the reviewer agents focused.
