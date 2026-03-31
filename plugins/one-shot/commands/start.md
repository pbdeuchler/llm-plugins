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

3. **Holistic Review:** Use your Skill tool to invoke `one-shot:holistic-review` within a subagent. The implementation plan path is `$1` and the base branch is the branch you checked out from (or the seed commitish branch if provided).

4. **MANDATORY:** Address ALL issues from the holistic code review. Do not complete until all issues have been addressed. Loop through steps 3-4 until you get a clean code review.

5. Commit the changes from the holistic code review with a detailed commit message describing what was done.

6. Create a PR using the `gh` CLI:
   - **Base branch:** If a seed commitish was provided and it is a branch, use that as the base. Otherwise, use the original branch you were on at initialization.
   - **Compare branch:** The new implementation branch.
   - **Description must include:**
     1. Summary of what the implementation plan asked for
     2. What you did to complete the task and why
     3. Any tradeoffs, design decisions, or complications that arose
     4. A summary of test changes and what a reviewer should pay attention to
     5. Anything else reviewers should pay special attention to

   IF YOU ENCOUNTER THIS ERROR: `pull request create failed: GraphQL: Head sha can't be blank, Base sha can't be blank, No commits between {base} and {compare}, Base ref must be a branch (createPullRequest)` then ensure `{base}` exists and is up to date on origin

   The success of this entire implementation relies upon it having a good PR description. It is imperative that the description is concise without being terse or lacking information. It should never be long, wordy, or overly descriptive. An engineer of any skill level should be able to use the description and immediately understand what was done, why it was done, and what they should pay attention to most in the review.
