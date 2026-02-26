---
name: executing-one-shot
description: Use for executing implementation plans
---

# Executing an Implementation Plan

Execute an implementation plan. Split the implementation plan into _no more than 5 steps_. Flesh out each step as if you were passing it to a junior developer. The goal here is very high quality code, architecture, and design. If the plan is too big or too ill defined or vague to do so immediately exit and report why with some recommendations on how to improve the plan.

**Core principle:** Read one step → execute all tasks → review → move to next step.

**REQUIRED SKILL:** `requesting-code-review` - The review loop (dispatch, fix, re-review until zero issues)

## Overview

**When NOT to use:**

- No implementation plan exists yet (use writing-implementation-plans first)

## MANDATORY: Human Transparency

**The human cannot see what subagents return. You are their window into the work.**

After EVERY subagent completes (task-implementor, bug-fixer, code-reviewer), you MUST:

1. **Print the subagent's full response** to the user before taking any other action
2. **Do not summarize or paraphrase** - show them what the subagent actually said
3. **Include all details:** test counts, issue lists, commit hashes, error messages

**Before dispatching any subagent:**

- Briefly explain (2-3 sentences) what you're asking the agent to do
- State which step this covers

**Why this matters:** When you silently process subagent output without showing the user, they lose visibility into their own codebase. They can't catch errors, learn from the process, or intervene when needed. Transparency is not optional.

**Red flag:** If you find yourself thinking "I'll just move on to the next step" without printing the subagent's response, STOP. Print it first.

## REQUIRED: Implementation Plan Path

**DO NOT GUESS.** If the user has not provided a path to an implementation plan directory, you MUST ask for it.

Use AskUserQuestion:

```
Question: "Which implementation plan should I execute?"
Options:
  - [list the newest plan files you find in docs/plans/]
  - "Let me provide the path"
```

If `docs/implementation-plans/` doesn't exist or is empty, ask the user to provide the path directly.

**Never assume, infer, or guess which plan to execute.** The user must explicitly tell you.

## The Process

### 1. Create Phase-Level Task List

Use TaskCreate to create **three task entries per step** (or TodoWrite in older Claude Code versions). The first task entry per step should be implementation, the second should be testing and verification, the third should be code review:

```
- [ ] Step 1a: Implement base types
- [ ] Step 1b: Write tests
- [ ] Step 1c: Code review
- [ ] Step 2a: Implement hot path
- [ ] Step 2b: Write tests
- [ ] Step 2c: Code review
...
```

**Why absolute paths in task entries:** After compaction, context may be summarized. The absolute path in the task entry ensures you always know exactly which file to read.

**Why include the title:** Gives visibility into what each phase covers without loading full content.

### 2. Execute

For each step, follow this cycle:

#### 2a. Implement the task

Mark "Step Na: Implementation" as in_progress and dispatch `task-implementor` to begin.

```
<invoke name="Task">
<parameter name="subagent_type">one-shot:task-implementor-fast</parameter>
<parameter name="description">Implementing Step X, Task Y: [description]</parameter>
<parameter name="prompt">

... fleshed out prompt goes here ...

</parameter>
</invoke>
```

#### 2b. Write tests and verify correctness

Mark "Step Na: Implementation" as in_progress and dispatch `task-implementor` to begin.

```
<invoke name="Task">
<parameter name="subagent_type">one-shot:task-implementor-fast</parameter>
<parameter name="description">Implementing Step X, Task Y: [description]</parameter>
<parameter name="prompt">

... fleshed out prompt goes here ...

</parameter>
</invoke>
```

#### 2c. Code Review for Step

Mark "Step Nc: Code review" as in_progress.

**MANDATORY:** Use the `requesting-code-review` skill for the review loop.

**Context to provide:**

- WHAT_WAS_IMPLEMENTED: Summary of all tasks in this phase
- PLAN_OR_REQUIREMENTS: All tasks from this phase
- BASE_SHA: commit before phase started
- HEAD_SHA: current commit

**If code reviewer returns a context limit error:**

The phase changed too much for a single review. Chunk the review:

1. Identify the midpoint of tasks in the phase
2. Run code review for first half of tasks (commits for tasks 1 through N/2)
3. Fix any issues found
4. Run code review for second half of tasks (commits for tasks N/2+1 through N)
5. Fix any issues found

**When issues are found**, dispatch `task-implementer` with the feedback:

```
<invoke name="Task">
<parameter name="subagent_type">one-shot:task-implementer</parameter>
<parameter name="description">Fixing review issues for Step X</parameter>
<parameter name="prompt">
  Fix issues from code review for Step X.

  Original prompt: [implementation step prompt]

  Code reviewer found these issues:
  [list all issues - Critical, Important, and Minor]

  Read the phase file to understand the tasks and context.

  Your job is to:
  1. Understand root cause of each issue
  2. Apply fixes systematically (Critical → Important → Minor)
  3. Verify with tests/build/lint
  4. Commit your fixes
  5. Report back with evidence

  Fix ALL issues — including every Minor issue. The goal is ZERO issues on re-review.
  Minor issues are not optional. Do not skip them.
</parameter>
</invoke>
```

After bug-fixer completes, re-review per the `requesting-code-review` skill. Continue loop until zero issues.

**Plan execution policy (stricter than general code review):**

- ALL issues must be fixed (Critical, Important, AND Minor)
- Ignore APPROVED/BLOCKED status - count issues only
- **Three-strike rule:** If same issues persist after three review cycles, stop and report the issue

**Minor issues are NOT optional.** Do not rationalize skipping them with "they're just style issues" or "we can fix those later." The reviewer flagged them for a reason. Fix every single one.

**Exit condition:** Zero issues in all categories — including Minor.

Mark "Phase Nc: Code review" as complete.

#### 3d. Move to Next Step

### 4. Update Project Context

After all phases complete, invoke a subagent to review changes and update README.md and AGENTS.md files if needed.

```
<invoke name="Task">
<parameter name="description">Updating project context after implementation</parameter>
<parameter name="prompt">
  Review what changed during this implementation and update README.md and AGENTS.md files if contracts or structure changed.

  Base commit: <commit SHA at start of first phase>
  Current HEAD: <current commit>
  Working directory: <directory>

  1. Diff against base to see what changed
  2. Identify contract/API/structure changes
  3. Update any files that might aid in future development
  4. Commit documentation updates

  Report back with what was updated (or that no updates were needed).
</parameter>
</invoke>
```

**If subagent reports updates:** Review the changes, then proceed to final review.
**If subagent reports no updates needed:** Proceed to final review.

### 5. Final Review

After all steps complete, use the `requesting-code-review` skill for final review:

- Reviews entire implementation
- Checks all plan requirements met
- Validates overall architecture

Continue the review loop until zero issues remain.

### 6. Complete Development

After final review passes:

- Provide a report to the human operator
  - For each step:
    - How many tasks were implemented
    - How many review cycles were needed
    - Any compromises made (there should be NO compromises, but if any were made). Examples:
      - "I couldn't run the integration tests, so I continued on"
      - "I couldn't generate the client because the dev environment was down"
      - Note that these are PARTIAL FAILURE CASES and explain to the user what the user must do now.
    - Were any code-review issues left outstanding at any point?

- Push the branch to remote origin.

## Common Rationalizations - STOP

| Excuse                                              | Reality                                                     |
| --------------------------------------------------- | ----------------------------------------------------------- |
| "I'll review after each task to catch issues early" | No. Review once per step. Task-level review wastes context. |
| "Context error on review, I'll skip the review"     | No. Chunk the review into halves. Never skip review.        |
| "Minor issues can wait"                             | No. Fix ALL issues including Minor.                         |
