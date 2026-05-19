---
name: tests-or-not-done
description: Use when adding or modifying non-trivial code - requires happy-path AND sad-path tests covering every return permutation, blocks declaring "done" if production code grew without matching test additions.
---

# Tests Or Not Done

## Why this skill exists

User's global CLAUDE.md, verbatim: "Every function worth testing should
have both success and error cases. Ensure tests cover every return... for
ex if a Rust function returns an Option ensure that both the Some and None
cases are covered. ... Use table driven tests when possible."

This rule is in his global config and does not propagate reliably to
Codex sessions. ~14 prior corrections of the form "Did you write tests to
comprehensively cover this? With both success and error cases?"

## When this fires

You added or significantly modified a function, method, or pure
transformation. Excludes:
- Pure comment / doc edits
- Dependency bumps
- Configuration-only changes
- One-line typo fixes

## Required behavior

For each function changed, identify:

1. **Return type permutations.** `Option<T>` -> `Some` and `None`.
   `Result<T, E>` -> `Ok` and each `E` variant worth distinguishing.
   `(T, error)` (Go) -> both permutations. `bool` -> true and false branches.
2. **Happy path.** At least one test demonstrating the typical use.
3. **Sad path(s).** One test per error/edge variant: invalid input,
   missing data, out-of-range, race condition, partial failure.
4. **Table-driven where applicable.** Multiple permutations of the same
   shape -> table-driven, one test function with a case list.

Before declaring done, run the tests and report the count by file. If
the test count did not grow alongside the production diff, surface this
explicitly and explain why (e.g., "this is a pure refactor with full
existing coverage").

## Anti-patterns

- "Tests pass" without saying which tests, or which were added.
- One happy-path assertion per function.
- Testing the framework instead of the logic (`assert mock.called`).
- Mocking the database in integration tests when the user's stack supports
  a real one (per his recurring "don't mock what you can run" preference).

## Override

If the change is genuinely untestable in isolation (e.g., a hardware
driver, a UI render verified separately by `verify-ui-changes`), say so
and propose the alternative verification.
