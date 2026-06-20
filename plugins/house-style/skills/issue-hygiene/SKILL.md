---
name: issue-hygiene
description: Use when creating, editing, triaging, or cleaning up GitHub issues - a mechanical pass that verifies the title is accurate and current, labels/assignees/milestone are correct, and the body is valid, well-formed markdown, all via the gh CLI. Does not judge content quality.
---

# GitHub Issue Hygiene

## Overview

A mechanical hygiene pass over a GitHub issue: correct title, correct
labels and metadata, valid markdown body. This is the lint layer - it does
NOT judge whether the issue is well-reasoned or complete (that is
`authoring-issues`). Run it after drafting an issue, or when asked to tidy
or triage existing ones.

All edits go through the `gh` CLI. Verify current state before changing
anything, and change only what is wrong (minimal edits).

## When to Use

- Creating or editing an issue and about to finalize it.
- User asks to "clean up", "triage", "retitle", "tag", "label", or "fix up"
  an issue.
- Immediately after `authoring-issues` produces a draft.
- Bulk triage of a backlog.

## The Checklist

**Title**

- Reflects the CURRENT body. If the scope changed, update the title to match.
- Concise and specific, imperative or noun-phrase. No trailing period.
- Follow the repo's existing prefix convention if one exists (e.g. `area:`,
  `[component]`) - check sibling issues first; do not invent one.

**Labels and metadata**

- List the repo's real labels first: `gh label list`. NEVER apply a label
  that does not exist unless explicitly asked to create one.
- Apply at least a type (bug/feature/chore/...) and an area/component label
  when those label families exist.
- Set assignee, milestone, and project only when known; do not guess.
- Link related work in the body: `Closes #N`, `Refs #N`. Mark duplicates.

**Body markdown**

- Headings nest correctly (no skipped levels); use sentence case.
- Every fenced code block is closed and language-tagged.
- Lists and task lists are well-formed (`- [ ]` / `- [x]`); tables have
  aligned header separators.
- Links and `#issue` / `@user` references resolve.
- No placeholder or broken text left behind.

## Commands

```bash
gh issue view <n> --json title,body,labels,assignees,milestone
gh label list                                   # real labels before tagging
gh issue edit <n> --title "..." \
  --add-label bug --add-label "area:api" \
  --milestone "v1.2"
gh issue create --title "..." --body-file draft.md --label bug
```

Render-check the body (`gh issue view <n> --web`, or preview the markdown)
before declaring done.

## Red Flags - Stop

- Inventing a label or milestone that does not exist in the repo.
- Rewriting the body's CONTENT to "improve" it - that is `authoring-issues`,
  not hygiene.
- Altering meaning while "fixing markdown".
- Leaving the title describing an older version of the body.
