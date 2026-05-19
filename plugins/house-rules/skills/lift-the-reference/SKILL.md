---
name: lift-the-reference
description: Use when the user provides a reference implementation (URL, repo path, branch, file) plus a verb like "use", "copy", "adapt", "port", "model after" - mandates fetching/reading the reference before designing, and lifting the structure rather than reimagining it.
---

# Lift the Reference, Don't Redesign

## Why this skill exists

The single most-corrected behavior across sessions (14+ incidents): the user
points at an existing implementation - "use the ripgrep impl from oh-my-pi",
"use playwright_rs instead of building your own renderer", "I told you to
copy as much as possible from those tools" - and the agent designs a
"cleaner" alternative instead. The user has to repeat the directive,
sometimes multiple times in the same thread.

## When this fires

User message contains BOTH:
1. A reference: URL (GitHub, docs site), filesystem path, branch name, or
   `@filename` mention.
2. A lift-verb: use, copy, adapt, port, mirror, model after, base on,
   follow, like X does, take from.

Also fires on phrases like "don't redesign", "don't rewrite from scratch",
"don't reinvent".

## Required behavior

1. **Fetch first.** Use Read / WebFetch / `gh` / `git show` to load the
   reference content into your context. Quote the relevant section back to
   the user in 5-15 lines.
2. **Map the structure.** State the reference's shape: file layout, key
   types, entry points, public API. One paragraph.
3. **Identify deltas.** State what (if anything) needs to differ for the
   user's use case, and why. Default to "no delta".
4. **Then implement.** Mirror the reference's naming, ordering, error
   handling, and idioms. If you are tempted to rename, reorder, or
   "improve", articulate the cost-benefit out loud before doing so.

## What "lifting" is NOT

- Reading the reference, then writing your own version from memory.
- Cherry-picking only the API surface and rebuilding internals.
- "I read it and the spirit of it is X" - the user wants the letter, not
  the spirit.
- Proposing an alternative architecture in the same turn.

## Anti-pattern to refuse

"Want me to revise the plan to use a slightly different approach that..." -
No. The user already chose the approach. Implement it.

## Override

The only valid reason to deviate from the reference is a *technical*
incompatibility with the target environment (different language, missing
dependency, breaking API change). State it explicitly; do not deviate for
aesthetic reasons.
