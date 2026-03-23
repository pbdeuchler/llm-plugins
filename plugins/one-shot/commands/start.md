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
   git rev-parse --git-dir
   ```

2. If $2 (seed commitish) was provided, verify the commitish exists and check out to it. If not, take note of the current branch you are on:

   ```bash
   git checkout $2
   ```

3. Verify the plan file exists:

   ```bash
   test -f "$1"
   ```

4. Checkout a new branch from the current HEAD (which should be the seed committish if provided). This branch should have a randomized, human readable name:

   ```bash
   git checkout -b lazy-koala-fence
   ```

If any of these steps fail, stop and report the error to the user.

## Execute

1. **Engage the skill:** Use your Skill tool to invoke `one-shot:execute-one-shot`
2. **If the skill asks for a plan path:** The user has already provided it: `$1`. Do not ask again.

The skill should execute everything in that file, no more and no less. Follow it exactly as written.

### Once the skill has completed

3. Spin up the `one-shot:holistic-reviewer` agent in a new subagent with a clean context. Provide this subagent with the initial implementation plan and a base branch that it can use to compare for diffs to review. Do a final code review and address ALL issues. Do not complete until all issues have been addressed.

4. Create a PR using the `gh` CLI:
   - **Base branch:** If a seed commitish was provided and it is a branch, use that as the base. Otherwise, use the original branch you were on at initialization.
   - **Compare branch:** The new implementation branch.
   - **Description must include:**
     1. Summary of what the implementation plan asked for
     2. What you did to complete the task and why
     3. Any tradeoffs, design decisions, or complications that arose
     4. A summary of test changes and what a reviewer should pay attention to
     5. Anything else reviewers should pay special attention to
