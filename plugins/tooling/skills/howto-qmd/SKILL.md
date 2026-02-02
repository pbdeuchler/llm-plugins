---
name: howto-qmd
description: Use when searching markdown knowledge bases, documentation, or notes for relevant context - provides qmd CLI syntax for keyword, semantic, and hybrid search across indexed collections
---

# Using qmd for Knowledge Base Search

## Overview

qmd is a local search engine for markdown documents. It combines BM25 keyword search, vector semantic search, and LLM-powered hybrid re-ranking. Use it to find relevant context in documentation, notes, and knowledge bases when grep is too literal and you need conceptual matching.

## When to Use

**Prefer qmd over grep when:**

- Searching documentation or notes for conceptually related content
- You know what you're looking for but not the exact terms used
- You need to find relevant context across a large markdown knowledge base
- Building context for a task from scattered documentation

**Use grep instead when:**

- Searching code files (qmd indexes markdown only)
- Looking for exact string matches or regex patterns
- The search target is a known identifier, import, or error message

## Search Modes

| Mode | Command | Speed | Best For |
|------|---------|-------|----------|
| Keyword (BM25) | `qmd search` | Fast | Known terms, exact phrases |
| Semantic (vector) | `qmd vsearch` | Slow | Conceptual queries, fuzzy recall |
| Hybrid (re-ranked) | `qmd query` | Slowest | Highest quality, broad exploration |

**Default to `qmd search`** unless keyword results are insufficient. Escalate to `vsearch` or `query` only when needed.

## CLI Quick Reference

```bash
# Keyword search (fast, use first)
qmd search "authentication flow"

# Semantic search (finds conceptually related content)
qmd vsearch "how users log in"

# Hybrid with LLM re-ranking (most thorough)
qmd query "best practices for session management"

# Restrict to a collection
qmd search "rate limiting" -c api-docs

# More results
qmd search "error handling" -n 20

# Full document content in results
qmd search "deployment" --full

# With line numbers
qmd search "config" --full --line-numbers

# JSON output for structured processing
qmd search "auth" --json --full

# Retrieve a specific document
qmd get "docs/auth.md" --full

# Retrieve from a specific line
qmd get "docs/auth.md:45" -l 100

# Batch retrieve by glob
qmd multi-get "docs/**/*.md" --json
```

## Collection Management

```bash
# Add a collection
qmd collection add ~/projects/docs --name project-docs --mask "**/*.md"

# List collections
qmd collection list

# Remove a collection
qmd collection remove old-notes

# Rebuild keyword index
qmd update

# Generate/update vector embeddings (required for vsearch/query)
qmd embed

# Check index health
qmd status
```

## Output Formats

| Flag | Format | Use Case |
|------|--------|----------|
| (default) | Human-readable | Interactive use |
| `--json` | JSON | Programmatic processing |
| `--files` | CSV: docid,score,filepath,context | File-oriented workflows |
| `--xml` | XML | Structured integration |
| `--md` | Markdown | Documentation pipelines |

## Filtering and Scoring

```bash
# Minimum relevance threshold
qmd search "deployment" --min-score 0.5

# All results above threshold
qmd search "config" --all --min-score 0.3

# Skip large files
qmd search "setup" --max-bytes 50000
```

## Practical Patterns

**Gather context before starting a task:**

```bash
# Find all relevant docs for a feature area
qmd search "authentication" -c project-docs -n 10 --files
# Then retrieve the most relevant ones
qmd get "docs/auth-design.md" --full --line-numbers
```

**Escalation pattern when keywords miss:**

```bash
# 1. Try keyword first (fast)
qmd search "retry logic"
# 2. If too few results, try semantic
qmd vsearch "how failures are retried"
# 3. If still unclear, use hybrid
qmd query "error recovery and retry mechanisms"
```

**Bulk context loading:**

```bash
qmd multi-get "design-docs/*.md" --json
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using `qmd query` for every search | Start with `qmd search`, escalate only if needed |
| Forgetting to run `qmd embed` | Required once before `vsearch`/`query` work |
| Searching code files with qmd | qmd indexes markdown only; use grep or ast-grep for code |
| Not specifying `-c` with many collections | Restrict to relevant collection for better signal |
| Ignoring `--min-score` with `--all` | Unfiltered results include low-relevance noise |

## Red Flags

- Running `qmd query` repeatedly in a loop (expensive; cache or batch instead)
- Using qmd when a simple grep for a known string would suffice
- Forgetting `qmd update` after documents change
- Not running `qmd embed` after adding new collections
