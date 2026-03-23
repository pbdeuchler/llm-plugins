# Changelog

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
