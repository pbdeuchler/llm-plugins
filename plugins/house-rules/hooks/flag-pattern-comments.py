#!/usr/bin/env python3
"""PostToolUse hook: warn when newly-written code contains explanatory
'pattern:' / 'note:' / 'added:' comment annotations.

Mined pattern: "Remove all '// pattern: ...' comments", "Remove the //pattern
comments you added", "Make the render code more functional with less ... cruft".

The model often inserts taxonomy/note comments (`// pattern: FCIS - Functional
Core`, `// note: added for X`, etc.) that the user finds noisy. This hook
flags them after the fact and asks the model to remove them.
"""

from __future__ import annotations

import json
import re
import sys

# Matches // pattern:, # pattern:, /* pattern:, also note:, added:, removed:,
# but ONLY when the line LEADS with the comment (not inline trailing comments,
# which are usually legitimate).
PATTERN_COMMENT = re.compile(
    r"^\s*(?://|#|/\*|\*)\s*(pattern|note|added|removed|added by|fix(?:ed)?|"
    r"new|todo\(added\)|claude|llm|copilot)\s*[:\-]",
    re.IGNORECASE | re.MULTILINE,
)


def reminder(reason: str) -> None:
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": reason,
            }
        },
        sys.stdout,
    )
    sys.exit(0)


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    if data.get("tool_name") not in ("Write", "Edit", "MultiEdit"):
        sys.exit(0)

    tool_input = data.get("tool_input", {}) or {}
    candidates: list[str] = []
    for key in ("content", "new_string"):
        v = tool_input.get(key)
        if isinstance(v, str):
            candidates.append(v)
    for edit in tool_input.get("edits", []) or []:
        if isinstance(edit, dict):
            v = edit.get("new_string")
            if isinstance(v, str):
                candidates.append(v)

    blob = "\n".join(candidates)
    matches = PATTERN_COMMENT.findall(blob)
    if not matches:
        sys.exit(0)

    sample = ", ".join(sorted({m.lower() for m in matches}))
    reminder(
        f"house-rules: this edit added leading 'pattern:/note:/added:/etc.' "
        f"annotation comments ({sample}). Philip has repeatedly asked these be "
        f"removed. Default to no comments; only annotate when the WHY is "
        f"genuinely non-obvious. Strip them before declaring the task done."
    )


if __name__ == "__main__":
    main()
