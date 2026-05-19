# house-rules (plugin instructions)

This plugin distills recurring user-correction patterns into reusable
skills and hooks. Each skill exists because the user got frustrated
enough about something to correct it multiple times.

## When you're working inside this plugin

You are editing the meta-discipline layer. The bar is high:

- Every new skill must point to a *concrete pattern* in prior sessions or
  a concrete future risk. Speculative skills bloat the discovery surface
  and dilute the strong ones. Do not add a skill "just in case".

- Use `ed3d-extending-claude:writing-claude-directives` and
  `ed3d-extending-claude:writing-skills` when modifying any SKILL.md.

- Skills must be ASCII-clean (`->`, `"`, `'` - no smart quotes, no
  Unicode arrows). The user has commented on this before.

- Skills must be third-person ("Use when..."), under 500 words ideally,
  cross-compatible with both Claude Code and Codex.

- Hooks live in `hooks/`. Each hook is a single-purpose Python script
  that reads JSON from stdin and writes a single JSON object to stdout.
  Hooks are Claude Code only; the cross-platform counterpart for each
  hook (where one exists) is a skill of the same intent.

## Adding a new rule

1. Write down the verbatim user quote(s) that motivated it.
2. Decide: hook (deterministic, no judgment) or skill (judgment
   required) or both.
3. Cite frequency in the file's "Why this skill exists" section -
   so a future reader knows it's earning its keep.
4. Bump version in `.claude-plugin/plugin.json` and
   `.codex-plugin/plugin.json`.
5. Per repo conventions: also update `.claude-plugin/marketplace.json`
   at the repo root and add a `CHANGELOG.md` entry.
