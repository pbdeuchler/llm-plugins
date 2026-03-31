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

3. **Holistic Review**

   **DETECTION (mandatory before proceeding):** Scan your available skills/commands list (shown in your system context) for `codex:rescue`. Record the result explicitly: "codex:rescue: AVAILABLE" or "codex:rescue: NOT AVAILABLE." You MUST do this before continuing.

   **If AVAILABLE → execute 3a. Skip 3b entirely. Proceeding to 3b when codex:rescue is available is a failure.**

   3a. Read the `one-shot:holistic-reviewer` agent definition file in full. Then use the Skill tool to invoke `codex:rescue` with `--fresh`. Pass it a single prompt that contains all three of these:
      - The full text of the holistic-reviewer agent definition you just read (Codex does not have access to your agent files — you must inline it)
      - The absolute path to the implementation plan
      - The base branch to diff against

      ```
      Skill: codex:rescue
      Args: --fresh

      You are performing a holistic code review. Follow the agent definition below exactly.

      ## Agent Definition

      {paste the FULL holistic-reviewer agent definition here}

      ## Review Parameters

      Implementation plan: {absolute_plan_path}
      Base branch: {base_branch}
      ```

   **If NOT AVAILABLE → 3b is the fallback.**

   3b. Spin up the `one-shot:holistic-reviewer` agent in a new subagent with a clean context. Provide this subagent with the initial implementation plan and a base branch that it can use to compare for diffs to review.

   ---

   3c. **MANDATORY:** Address ALL issues from the holistic code review. Do not complete until all issues have been addressed. Loop through this step (3) until you get a clean code review.

4. Commit the changes from the holistic code review with a detailed commit message describing what was done.

5. Create a PR using the `gh` CLI:
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
