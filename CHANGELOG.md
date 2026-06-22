# Changelog

## [tooling] 0.3.1

Add a Codex (`.codex-plugin`) manifest so the plugin installs on Codex as well as Claude Code.

## [one-shot] 0.4.15

Add a Codex (`.codex-plugin`) manifest so the plugin installs on Codex as well as Claude Code.

## [autoresearch] 0.3.2

Add a Codex (`.codex-plugin`) manifest so the plugin installs on Codex as well as Claude Code.

## [quick-plan] 0.1.2

Add a Codex (`.codex-plugin`) manifest so the plugin installs on Codex as well as Claude Code.

## [blank-slate-review] 0.1.2

Add a Codex (`.codex-plugin`) manifest so the plugin installs on Codex as well as Claude Code.

## [house-style] 1.1.0

Two paired GitHub-issue skills, plus a Codex manifest so the plugin installs on Codex as well as Claude Code.

**New:**

- Skill `authoring-issues` - mandates exploring the relevant code before writing, reasoning any proposed solution, and structuring the issue (summary, what/why, references, nuances, open questions, acceptance criteria). Adds professionalism and no-sensitive-info discipline for public repos.
- Skill `issue-hygiene` - mechanical pass over title accuracy, labels/assignees/milestone, and valid markdown via the `gh` CLI; does not judge content quality.
- `.codex-plugin/plugin.json` exposing `./skills/` to Codex (previously Claude Code only).

## [house-rules] 0.2.0

**Removed:**

- Hook (Claude Code) `correction-and-reference-signal` and its `UserPromptSubmit` registration.

## [tooling] 0.3.0

Enforce uv/uvx over direct python/pip/pipx/venv calls when uv is installed.

**New:**

- Skill `howto-uv` - command mappings from `python`/`pip`/`pipx`/`venv` to `uv run`/`uv pip`/`uvx`/`uv venv`, with rationale and exceptions
- Hook (Claude Code) `prefer-uv` - PreToolUse on Bash; denies direct python/pip/pipx/venv invocations and returns the uv equivalent, but only when `uv` is on PATH. Allows `python --version` probes, `uv run`/`uvx` calls, and incidental "python" mentions in arguments or strings

## [house-rules] 0.1.0

Initial release of the house-rules plugin. Distills recurring user-correction patterns mined from ~566 prior Claude Code and Codex sessions into reusable skills and Claude Code hooks.

**New:**

- Plugin scaffold (`plugins/house-rules/`) with cross-compatible `.claude-plugin/` and `.codex-plugin/` manifests
- Hooks (Claude Code): `strip-claude-coauthor` (deny commits crediting Claude/Anthropic/Codex as co-author), `gate-git-write-ops` (ask before commit/push unless the latest user message contains a commit/push verb), `flag-pattern-comments` (warn when edits add leading `// pattern:` / `// note:` annotations), `correction-and-reference-signal` (inject reminder when user shares a URL near "use/see/read" or shouts/repeats a correction)
- Skills (Claude Code + Codex): `no-claude-coauthor`, `lift-the-reference`, `minimal-edit-scope`, `verify-ui-changes`, `tests-or-not-done`, `respect-analysis-mode`, `respect-output-mode`, `root-cause-not-symptom`, `domain-checkpoint`, `checkpoint-plan-frequently`
- `templates/AGENTS.md` - drop-in for `~/.codex/AGENTS.md` so Codex sessions get the same defaults Claude Code gets from `~/.claude/CLAUDE.md`
- `templates/codex-rules.md` + `codex-rules.snippet` - recommended `prefix_rule(...)` additions for `~/.codex/rules/default.rules`, closing the structural gap (currently the file allows essentially only `cargo test`)

## [one-shot] 0.4.8

Holistic reviewer overhaul and context management improvements.

**New:**

- `holistic-review` skill that routes to `codex:rescue` for dueling-model review when available, falling back to a direct subagent
- Multi-persona holistic reviewer: panel of staff engineers (systems, distributed systems, security, infra ops, product) that discuss findings from different perspectives
- Tests-first review methodology: reviewer reads tests before implementation code to assess coverage and falsify assumptions
- Mandatory context compaction after each step's code review — prunes context no longer needed for remaining work

**Changed:**

- Implementation steps are now ordered for optimal context management (foundational pieces first, independent work early)
- Holistic reviewer now reviews across seven dimensions (added test coverage) instead of six
- Removed redundant final review from `execute-one-shot` skill — holistic review is now handled by the `holistic-review` skill invoked from the command
- PR description quality is now explicitly enforced with troubleshooting guidance for common errors

## [autoresearch] 0.3.1

**Fixed:**

- Formatting cleanup in `autoresearch-create` skill (whitespace, JSON readability)

## [blank-slate-review] 0.1.1

**Fixed:**

- Minor post-release fixes

## [quick-plan] 0.1.1

**Fixed:**

- Minor post-release fixes

## [one-shot] 0.4.0

Use codex for holistic reviewer

**New:**

- Uses the `/codex:rescue` command along with the `holistic-reviewer` agent to get a true clean room review via dueling models

## [blank-slate-review] 0.1.0

Initial release of the blank-slate-review plugin.

**New:**

- `/blank-slate-review:start` command -- validates optional scope and launches the review pipeline
- `execute-review` skill -- orchestrates scout, file sampling, fan-out decision, and reviewer dispatch
- `codebase-reviewer` agent -- Opus-powered multi-persona panel with seven analysis dimensions, four severity levels, and holistic remediation synthesis

## [quick-plan] 0.1.0

Initial release of the quick-plan plugin.

**New:**

- `/quick-plan:start` command -- creates a branch, picks a plan file location, and launches the planning skill
- `devise-a-plan` skill -- structured 9-step planning process with specialist subagent dispatch
- `systems-performance` agent -- evaluates approaches for hot path efficiency, allocation pressure, and resource usage
- `distributed-systems` agent -- investigates codebase structure and evaluates cross-boundary interactions
- `security-engineer` agent -- evaluates threat surface changes, trust boundaries, and escalation paths
- `infra-operations` agent -- evaluates deployment impact, rollback safety, and observability gaps
- `product-lead` agent -- evaluates strategic fit, scope, and future flexibility

## [autoresearch] 0.2.0

**New:**

- `/autoresearch` command - start or resume experiment sessions with optional duration limit (`/autoresearch 60` for a 60-minute session)
- `maxDurationMinutes` config field - wall clock time limit for sessions, useful as a plan quota budget proxy
- Graceful shutdown procedure - clean state commit and summary when time/iteration limits are reached
- `plugin.json` for proper plugin registration

**Changed:**

- Loop rules now check stop conditions (time, iterations) before each experiment
- "What's Been Tried" section in autoresearch.md gets updated on shutdown

## [tooling] 0.2.0

**New:**

- `howto-qmd` skill - local semantic search for markdown knowledge bases with keyword, vector, and hybrid search modes

## [tooling] 0.1.0

Initial release of the tooling plugin.

**New:**

- `howto-ast-grep` skill - structural code search and rewriting with ast-grep CLI patterns, metavariable syntax, and language-specific examples

## [house-style] 2.0.0

**Changed:**

- Completely rewrite `coding-effectively`
- Remove `howto-function-core-imperative-shell`
