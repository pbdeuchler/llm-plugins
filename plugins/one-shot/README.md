# one-shot

Execute an implementation plan end-to-end in a single session: implement, test, review, and open a PR.

## Usage

```
/one-shot:start <absolute-plan-file-path> [seed-commitish]
```

- `plan-file-path` — Absolute path to an implementation plan file.
- `seed-commitish` — (Optional) Branch or SHA to check out before starting. Used as the PR base branch if it is a branch name.

The command creates a new branch, executes the plan step-by-step with per-step code review, runs a holistic final review, and opens a PR against the appropriate base.

## Components

### Command: `start`

Entry point. Validates inputs, checks out the seed commitish (if provided), creates a working branch, invokes the `execute-one-shot` skill, runs a holistic review via the `holistic-review` skill, and creates a PR.

### Skill: `execute-one-shot`

Orchestrates the implementation loop:

1. Splits the plan into at most 5 steps, ordered for optimal context management (foundational building blocks first, independent pieces early so they can be summarized later)
2. For each step: implement → write tests → code review (via `requesting-code-review`)
3. Fixes all review findings (Critical, Important, and Minor) before moving on
4. Mandatory context compaction after each step's code review completes — prunes context that is no longer needed for remaining work
5. Updates project context (README, AGENTS.md) if contracts changed

Rejects plans that are too large or too vague to complete in 5 steps at a high quality bar.

### Skill: `holistic-review`

Routes the final holistic code review to the best available backend. Prefers `codex:rescue` for a true clean-room dueling-model review; falls back to a direct `holistic-reviewer` subagent when Codex is unavailable.

### Agent: `task-implementer`

Sonnet-powered subagent that implements individual tasks. Follows TDD (test first, then implement), applies relevant coding skills, runs verification (tests/build/lint), commits work, and reports back with evidence.

### Agent: `holistic-reviewer`

Opus-powered multi-persona panel of staff engineers that evaluates the full diff against the original plan. The panel includes specialists in systems performance, distributed systems, security, infrastructure operations, and product strategy. Reviews across seven dimensions: correctness, elegance, simplicity, design principles, idiomatic usage, plan adherence, and test coverage. Uses a tests-first methodology — reviewing tests before implementation to validate coverage and falsify assumptions. Produces a structured report with severity-classified findings. PASS requires zero issues at all severity levels.

## Design Decisions

- **Single-session execution** — The entire plan runs in one conversation rather than being broken across multiple sessions. This keeps context coherent and avoids handoff overhead.
- **Per-step review, not per-task** — Code review happens once per step (which may contain multiple tasks), not after every individual task. This balances quality assurance against context usage.
- **Mandatory context compaction** — After each step's code review, context is pruned to keep the session efficient for remaining work. Skipping compaction is treated as a failure.
- **Three-strike rule** — If the same review issues persist after three fix-and-review cycles, execution stops rather than looping indefinitely.
- **Minor issues are not optional** — All severity levels must be resolved before a step is considered complete.
- **Tests-first review** — The holistic reviewer reads tests before implementation code, using them as a guide to assess coverage adequacy and identify untested critical paths.
- **Dueling-model review** — When Codex is available, the holistic review runs on a separate model for a true clean-room perspective, preventing in-context bias from the implementation session.
