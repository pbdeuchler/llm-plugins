---
description: Execute implementation plan in a single agent loop
argument-hint: [absolute-plan-file-path] [seed commitish]
---

# Execute Implementation Plan

**Implementation plan file:** `$1`
**Seed Commitish:** `$2` (Optional)

This execution workflow uses:

- Per-task code review

## Before Starting

The first argument MUST be an absolute path. Verify it exists:

1. Verify we are in a git repo:

   ```bash
   git -C "$2" rev-parse --git-dir
   ```

2. If $2 (seed commitish) was provided: Verify the commitish exists and check out to it:

   ```bash
   git checkout $2
   ```

3. Verify the plan file exists:

   ```bash
   test -f "$1"
   ```

4. Checkout a new branch from the seed committish if provided, else from the current HEAD. This branch should have a randomized, human readable name:

   ```bash
   git checkout -b lazy-koala-fence
   ```

If any of these steps fail, stop and report the error to the user.

## Execute

1. **Engage the skill:** Use your Skill tool to invoke `execute-one-shot`
2. **If the skill asks for a plan path:** The user has already provided it: `$1`. Do not ask again.

The skill should execute everything in that file, no more and no less. Follow it exactly as written.

### Once the skill has completed

3. **IF YOU ARE WITHIN A GITHUB ACTIONS WORKFLOW:** Identify the git branch that triggered this workflow. Using the `gh` cli tool create a PR with the base as the git branch you just identified, and the compare the new branch that contains the implementation. Set the PR description to the output provided by the `execute-one-shot` skill. If you hit content length limits summarize appropriately.
