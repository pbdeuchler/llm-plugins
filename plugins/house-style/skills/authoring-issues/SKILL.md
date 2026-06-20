---
name: authoring-issues
description: Use when asked to write, draft, file, or open a GitHub issue - mandates exploring the relevant code to understand the whole problem space, reasoning any proposed solution, and structuring the issue with summary, what/why, references, nuances, open questions, and acceptance criteria. Adds professionalism and no-sensitive-info discipline for public repos.
---

# Authoring GitHub Issues

## Overview

A good issue is a self-contained unit of work: a reader with the relevant
domain experience - junior or senior - can pick it up without a verbal
briefing. Getting there takes two things the prompt alone cannot give you:
an understanding of the actual code, and a reasoned view of the fix.
Explore first, reason second, write third.

This skill governs CONTENT and structure. Pair it with `issue-hygiene` for
the mechanical pass (labels, title, valid markdown).

## When to Use

- User asks to "write / create / open / draft / file" a GitHub issue.
- Turning a bug report, idea, or chat discussion into a tracked issue.

## Required Behavior

**1. Explore before writing.** Read the relevant code paths. Trace the
problem (or a feature's touch points) to its source. Cite concrete
`file:line` references. Do not write from the prompt alone - a request you
cannot locate in the code is one you do not yet understand. Fan out with
read-only search agents if the surface is large.

**2. Reason any solution.** If you propose a fix or design, weigh the
alternatives and state the tradeoff. A shallow first-thing-that-works
prescription is worse than none. When genuinely unsure, surface the choice
as an open question rather than feigning confidence.

**3. Structure for a stranger.** Include MOST of the following - this is
judgment, not a template to pad. Omit a section only when it genuinely does
not apply; include more often than not.

- **Summary** - 1-3 sentence TL;DR.
- **What and why** - the problem or goal, and its motivation or impact.
- **References** - `file:line`, related issues/PRs, docs, external links.
- **Nuances** - edge cases, constraints, gotchas, prior attempts.
- **Open questions** - unknowns and decisions still to be made.
- **Definition of done / acceptance criteria** - observable outcomes as a
  task list.

Calibrate depth so a junior with the domain background can act without
hand-holding, and a senior is not buried in the obvious. If specialized
domain experience is genuinely required, say so explicitly.

## Public Repositories

Assume a broad, anonymous audience. Before posting:

- No secrets, internal hostnames/URLs, customer data, employee names, or
  unreleased plans.
- No exploit detail that arms an attacker; report security issues through
  the proper private channel, not a public issue.
- Professional, respectful tone throughout.

Breadth of audience NEVER lowers the bar. Depth, rigor, and thoughtfulness
stay the same - you simply define terms and link prerequisites instead of
assuming shared context.

## Output

Produce the issue body as markdown and present it for review. Create it with
`gh issue create` only when the user asked to file or open it; otherwise
hand back the draft. Then run `issue-hygiene`.

## Template

```markdown
## Summary
<one to three sentences>

## What & why
<the problem or goal, and the motivation / impact>

## References
- `path/to/file.rs:120` - <what lives here>
- #123, related docs or links

## Nuances & considerations
- <edge cases, constraints, prior attempts>

## Open questions
- <decisions still to make>

## Definition of done
- [ ] <observable, checkable outcome>
```

## Red Flags - Stop

- Writing the issue without having opened the code it concerns.
- A proposed solution with no rationale or alternatives considered.
- Padding every section to fill the template when some do not apply.
- Pasting internal URLs, secrets, or names into a public repo.
