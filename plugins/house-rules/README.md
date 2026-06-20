# house-rules

Behavioral guardrails distilled from a corpus of past corrections.

`house-rules` is the sister plugin to `house-style`. Where `house-style`
covers how code should be written, `house-rules` covers how the agent
should behave: when to commit, when to verify, when not to redesign, when
to stay in analysis mode, when to write tests.

The skills and hooks here are not invented from priors - each one maps to
a specific, recurring user-correction pattern mined from ~566 prior
Claude Code and Codex sessions.

## What it ships

### Hooks (Claude Code only)

| Hook | Event | What it does |
|---|---|---|
| `strip-claude-coauthor` | PreToolUse / Bash | Denies any `git commit` carrying a `Co-Authored-By: Claude/Anthropic/Codex` trailer. |
| `gate-git-write-ops` | PreToolUse / Bash | Asks for approval before `git commit`/`git push` if the latest user message contains no commit/push verb. |
| `flag-pattern-comments` | PostToolUse / Write\|Edit | Warns when an edit adds leading `// pattern:`, `// note:`, `// added:` annotation comments. |

### Skills (Claude Code + Codex)

| Skill | Triggers on |
|---|---|
| `no-claude-coauthor` | Drafting any commit message. Cross-platform companion to the hook. |
| `lift-the-reference` | User gives URL/path + use/copy/adapt verb. |
| `minimal-edit-scope` | About to Write/Edit/MultiEdit/apply_patch. |
| `verify-ui-changes` | Editing rendered UI / chart / dashboard / plot output. |
| `tests-or-not-done` | Modifying non-trivial code. |
| `respect-analysis-mode` | User asks to investigate/analyze/spec/plan without an implement verb. |
| `respect-output-mode` | User asks for "the markdown / for me to copy / paste-able". |
| `root-cause-not-symptom` | About to add defensive code / retry / try-catch swallow. |
| `domain-checkpoint` | About to write code touching API/protocol/financial semantics. |
| `checkpoint-plan-frequently` | Multi-step work. |

## Installation

### Claude Code

```
/plugin install house-rules@llm-plugins
```

Hooks activate automatically. Skills become discoverable.

### Codex

```
codex plugin install house-rules@llm-plugins
```

Skills become discoverable; hooks are not supported by Codex.

For Codex you should ALSO take two manual steps to close the structural
gap that Claude Code closes via hooks and settings:

1. **Mirror your global CLAUDE.md into AGENTS.md.** Copy
   `templates/AGENTS.md` from this plugin into `~/.codex/AGENTS.md`
   (or merge into your existing one). This propagates your behavioral
   defaults (no co-author, minimal edits, test coverage, etc.) into every
   Codex session.

2. **Expand `~/.codex/rules/default.rules`.** See `templates/codex-rules.md`
   for the recommended `prefix_rule` additions. The current default
   allows essentially only `cargo test`, which forces Codex to ask before
   running `cargo build` / `cargo check` - a frequent cause of the
   "patch applied but didn't compile" failure mode.

## Versioning

Versions follow semver. Adding new skills or hooks is a minor bump;
breaking changes to existing skill/hook contracts are a major bump.

## How to extend

When you notice yourself giving the same feedback twice, add the
corresponding skill or hook here rather than restating it. The point of
the plugin is to make corrections accumulate.
