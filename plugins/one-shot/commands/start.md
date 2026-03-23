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

2. If $2 (seed commitish) was provided verify the committish exists and check out to it. If not, take note of the current branch you are in:

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

3. Spin up the one-shot:holistic-reviewer agent in a new subagent with a clean context. Provide this subagent with the initial implementation plan and a base branch that it can use to compare for diffs to review. Do a final code review and address ALL issues. Do not complete until all issues have been addressed.

4. If a seed committish was provided and it is a branch create a PR with that branch as the base and the new implementation branch as the compare. If a seed committish was NOT provided then use the original branch you were initialized in as the base. Create a thoughtful description, summarizing what you were initially asked to do in the implementation plan, what you did to complete the task, and why. Make sure to include any tradeoffs, design decisions, or complications that arose. Finally include a quick summary of anything a reviewer should care about when looking at test changes. Ensure throughout the PR description to emphasize anything that reviewers should pay special attention to. Use the `gh` cli tool to interact with GitHub.
