#!/usr/bin/env python3
"""PreToolUse hook: block direct python/pip/pipx/venv invocations when uv is
available, and tell the agent the uv/uvx equivalent.

Requirement: "require agents to use uv and uvx when it is available instead of
calling python directly".

If `uv` is not on PATH, the hook does nothing - the requirement is conditional
on uv being installed. Pure interpreter probes (`python --version`) are allowed.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import shlex
import sys

PYTHON_RE = re.compile(r"^python(\d+(\.\d+)?)?$")
PIP_RE = re.compile(r"^pip(\d+(\.\d+)?)?$")
PIPX_RE = re.compile(r"^pipx$")

# Command prefixes that wrap the real executable; skip them to find the target.
WRAPPERS = {"sudo", "env", "time", "nice", "command", "exec", "stdbuf", "nohup"}

# Splits a compound command into sub-commands on shell control operators.
SEGMENT_SPLIT = re.compile(r"&&|\|\||;|\||\n")


def allow() -> None:
    sys.exit(0)


def deny(reason: str) -> None:
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        },
        sys.stdout,
    )
    sys.exit(0)


def target_tokens(segment: str) -> list[str]:
    """Tokenize a segment and strip leading VAR=val assignments and wrappers,
    returning the tokens starting at the real executable (or [])."""
    try:
        tokens = shlex.split(segment)
    except ValueError:
        return []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if "=" in tok and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tok):
            i += 1
            continue
        if os.path.basename(tok) in WRAPPERS:
            i += 1
            continue
        break
    return tokens[i:]


def suggest(tokens: list[str]) -> str | None:
    """Return a remediation message if these tokens invoke python/pip/pipx in a
    way uv should handle, else None."""
    if not tokens:
        return None
    exe = os.path.basename(tokens[0])
    args = tokens[1:]

    if PIP_RE.match(exe):
        rest = (" " + " ".join(args)).rstrip()
        return (
            f"`{exe}` -> use `uv pip{rest}` for ad-hoc installs, or "
            "`uv add <pkg>` to record a project dependency."
        )

    if PIPX_RE.match(exe):
        if args and args[0] == "run":
            return f"`pipx run` -> use `uvx {' '.join(args[1:])}`."
        if args and args[0] == "install":
            return f"`pipx install` -> use `uv tool install {' '.join(args[1:])}`."
        return "`pipx` -> use `uvx <tool>` (ephemeral) or `uv tool install <tool>`."

    if PYTHON_RE.match(exe):
        # Allow pure capability probes.
        if args and args[0] in ("--version", "-V") and len(args) == 1:
            return None
        if args[:2] == ["-m", "pip"]:
            return f"`{exe} -m pip` -> use `uv pip {' '.join(args[2:])}`."
        if args[:2] == ["-m", "venv"]:
            return f"`{exe} -m venv` -> use `uv venv {' '.join(args[2:])}`."
        rest = " ".join(args)
        invoked = f"{exe} {rest}".rstrip()
        return (
            f"`{invoked}` -> use `uv run {rest}` (or `uv run python ...` for "
            "module/REPL/-c forms). uv resolves locked deps and the pinned "
            "interpreter automatically."
        )

    return None


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        allow()

    if data.get("tool_name") != "Bash":
        allow()

    command = (data.get("tool_input", {}) or {}).get("command")
    if not isinstance(command, str) or not command.strip():
        allow()

    if not shutil.which("uv"):
        allow()  # requirement only applies when uv is installed

    for segment in SEGMENT_SPLIT.split(command):
        segment = segment.strip()
        if not segment:
            continue
        msg = suggest(target_tokens(segment))
        if msg:
            deny(
                "tooling: uv is installed - prefer it over calling python "
                f"directly. {msg} See the tooling:howto-uv skill. If this case "
                "genuinely needs raw python (activated venv, repo not on uv), "
                "say so and proceed."
            )

    allow()


if __name__ == "__main__":
    main()
