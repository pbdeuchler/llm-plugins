#!/usr/bin/env python3
"""UserPromptSubmit hook: inject context when the user's prompt contains:
  (a) URLs/paths that ought to be fetched/read before acting, or
  (b) signals that the user is re-correcting a prior mistake.

Both are mined from the session corpus:
  - "Here are the docs: https://...", "use these docs for reference: ...",
    "Please review these two documentation pages: ..." (12 incidents in Codex)
  - "THERE IS NO DATASOURCE UID" / "That is incorrect" / "I told you" /
    "for the third time" — ALL-CAPS or correction-verb signals (~10+ incidents)

Single hook, single injection — keeps the reminder budget tight.
"""

from __future__ import annotations

import json
import re
import sys

URL = re.compile(r"https?://\S+")

# Repeat / correction signal patterns.
REPEAT_VERB = re.compile(
    r"\b("
    r"i (told|asked|said|already told) you|"
    r"that is (wrong|incorrect|not (?:right|correct))|"
    r"for the (third|second|fourth|nth) time|"
    r"again,?|"
    r"i'?ve told you|"
    r"please stop|"
    r"as i (said|mentioned|told you)|"
    r"like i said|"
    r"i already (said|told)"
    r")\b",
    re.IGNORECASE,
)

# Run of >=3 consecutive uppercase letters (>=2 chars, not e.g. a function name).
SHOUTING = re.compile(r"\b[A-Z]{3,}(?:\s+[A-Z]{2,}){1,}\b")


def inject(message: str) -> None:
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": message,
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

    prompt = data.get("prompt") or data.get("user_prompt") or ""
    if not isinstance(prompt, str) or not prompt.strip():
        sys.exit(0)

    notes: list[str] = []

    urls = URL.findall(prompt)
    if urls:
        # Only inject if the user used a "use this" verb (in the prose, not
        # in the URL itself). Strip URLs out of the search text so that a
        # bare https://docs.example.com link doesn't auto-trigger.
        prose = URL.sub("", prompt)
        looks_referency = re.search(
            r"\b(docs?|reference|spec|see|read|review|use|api|guide|example)\b",
            prose,
            re.IGNORECASE,
        )
        if looks_referency:
            urls_short = ", ".join(urls[:3]) + ("..." if len(urls) > 3 else "")
            notes.append(
                f"User provided reference URL(s) ({urls_short}). "
                f"Fetch and quote the relevant section BEFORE writing code "
                f"or proposing a design. Past sessions show repeat corrections "
                f"when this step is skipped."
            )

    if REPEAT_VERB.search(prompt) or SHOUTING.search(prompt):
        notes.append(
            "Signal detected: the user appears to be re-correcting a prior "
            "mistake (repeat-verb or shouting). STOP. Before any tool call, "
            "re-read the last 3 user messages and the most recent assistant "
            "actions. State (in 1-2 sentences) what you misunderstood, then "
            "act on the corrected understanding. Do not rationalize the prior "
            "behavior."
        )

    if notes:
        inject("\n\n".join(f"<house-rules>{n}</house-rules>" for n in notes))

    sys.exit(0)


if __name__ == "__main__":
    main()
