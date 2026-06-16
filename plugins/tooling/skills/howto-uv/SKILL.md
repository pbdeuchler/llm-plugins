---
name: howto-uv
description: Use when running Python, installing Python packages, creating virtualenvs, or executing Python CLI tools - mandates uv/uvx over direct python/pip/pipx/venv calls when uv is installed, and gives the drop-in command mappings
---

# Use uv and uvx Instead of Python Directly

## Overview

`uv` is a fast, reproducible Python package and project manager. When `uv` is
on PATH, prefer it over direct `python`, `pip`, `pipx`, and `venv` calls. It
resolves and caches dependencies deterministically, manages the interpreter,
and makes ad-hoc tool runs reproducible without polluting the global
environment.

Check availability with `command -v uv`. If `uv` is not installed, fall back to
`python`/`pip` as usual - this guidance applies only when `uv` is present.

## Command Mappings

| Instead of | Use |
| --- | --- |
| `python script.py` | `uv run script.py` |
| `python -m module` | `uv run python -m module` |
| `python -c '...'` | `uv run python -c '...'` |
| `python` (REPL) | `uv run python` |
| `pip install X` | `uv pip install X` (ad hoc) or `uv add X` (project dep) |
| `python -m pip install X` | `uv pip install X` |
| `python -m venv .venv` | `uv venv .venv` |
| `pipx run X` | `uvx X` |
| `pipx install X` | `uv tool install X` |
| `pip-compile` / freeze | `uv lock` / `uv pip compile` |

## Why uv run / uvx

- `uv run` ensures the project's locked dependencies are present and uses the
  pinned interpreter before executing - no manual activate step, no stale venv.
- `uvx TOOL` runs a CLI tool in an ephemeral, cached environment. Reach for it
  for one-off tools (`uvx ruff check`, `uvx black .`, `uvx httpie`) instead of
  globally installing them.
- For project work, prefer `uv add` (records the dep in `pyproject.toml` and the
  lockfile) over `uv pip install` (which mutates the environment without
  recording intent).

## Exceptions

- `python --version` / `python -V` capability probes are fine as-is.
- If the repo standardizes on Poetry, Conda, or plain pip and `uv` is absent,
  follow the repo. Do not introduce `uv` where the project does not use it.
- An already-activated, project-sanctioned virtualenv is acceptable; do not
  fight an established workflow.

## Quick Reference

```bash
uv run app.py                 # run a script with project deps
uv run pytest                 # run an installed dev tool
uvx ruff check .              # run a tool without installing it
uv add httpx                  # add a dependency to the project
uv pip install requests       # ad-hoc install into the active env
uv venv .venv                 # create a virtualenv
uv sync                       # install exactly what the lockfile pins
```
