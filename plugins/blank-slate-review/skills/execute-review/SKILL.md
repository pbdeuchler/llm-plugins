---
name: execute-review
description: Use when performing a blank-slate codebase review -- orchestrates the scout, file sampling, fan-out decision, reviewer dispatch, and output formatting pipeline
---

# Execute Review

Orchestrate a structured codebase review. You drive a two-phase pipeline -- scout then review -- and present the output to the user. Context discipline is critical throughout: every tool call and subagent dispatch should serve the review, nothing else.

**REQUIRED:** You should have been provided with a scope (directory, file, glob, or project root). If you have not, ask and immediately exit.

## The Pipeline

### 1. Scout the Codebase

Dispatch a Haiku-powered subagent to produce a structural inventory of the codebase within the given scope. The scout maps structure without reading file contents in detail.

```
<invoke name="Agent">
<parameter name="subagent_type">ed3d-basic-agents:haiku-general-purpose</parameter>
<parameter name="description">Scout codebase structure</parameter>
<parameter name="prompt">
You are a codebase scout. Your job is to produce a compact structural inventory of a codebase without reading full file contents. Be fast and precise.

**Scope:** [INSERT SCOPE]

Use Glob and Bash (for line counts, directory listing) to map:

1. **Languages**: which programming languages are present and their relative proportion (file count per extension)
2. **Frameworks/Libraries**: identify from config files (package.json, Cargo.toml, go.mod, requirements.txt, etc.)
3. **Directory layout**: top-level structure and what each directory appears to contain (src, lib, tests, config, scripts, docs, etc.)
4. **Entry points**: main files, index files, CLI entry points, server startup files
5. **Test locations**: where tests live (test/, __tests__/, *_test.go, *_spec.ts, etc.) and rough count
6. **Configuration**: build configs, CI/CD files, environment configs
7. **File counts**: total files by type within scope

Output a compact markdown inventory. Do NOT read file contents -- only names, paths, and metadata. Keep it under 300 words.

Format:

```
## Structural Inventory

**Languages:** Go (45 files), TypeScript (23 files), ...
**Frameworks:** Echo, React, ...
**Layout:**
- src/ -- main application code
- pkg/ -- shared packages
- ...

**Entry Points:** cmd/server/main.go, src/index.ts, ...
**Test Locations:** *_test.go alongside source (38 test files), src/__tests__/ (12 files)
**Config:** Makefile, docker-compose.yml, .github/workflows/ci.yml
**Total Files:** ~150 within scope
```
</parameter>
</invoke>
```

When the scout returns, print the structural inventory to the user so they can see what was found.

### 2. Select Files to Review

Using the structural inventory, select a representative sample of files to review. The goal is to cover the most important code without exceeding what a single reviewer agent can handle effectively.

**Selection priorities (in order):**

1. **Entry points** -- main files, server startup, CLI entry points. These reveal the application's shape.
2. **Core business logic** -- the modules that do the actual work, not glue or boilerplate.
3. **Shared utilities/packages** -- code that many other files depend on. Problems here cascade.
4. **Configuration and infrastructure** -- build configs, CI, Docker. These shape reliability.
5. **Tests** -- a sample of test files, especially for core modules. Test quality reveals code quality.
6. **API boundaries** -- route definitions, handler files, API schemas. Trust boundary code.

**Selection constraints:**

- Aim for 15-30 files for a single-pass review. Fewer for small codebases, more only if fan-out is used.
- Prefer depth over breadth -- it's better to thoroughly review 15 files than to skim 40.
- If the scope is a single file or small directory, review everything in it.
- Skip generated files, vendored dependencies, lock files, and binary assets.

Use Glob and Read (first few lines only, to assess relevance) to make your selections. List the selected files.

### 3. Decide: Single Pass or Fan-out

Estimate whether the selected files fit in a single reviewer's context:

- **Single pass** (default): 30 or fewer files, codebase is cohesive (one primary language/framework). Dispatch one reviewer.
- **Fan-out**: More than 30 files after sampling, OR the codebase has clearly separate modules (e.g., frontend + backend, multiple microservices). Partition files by module/directory and dispatch multiple reviewers in parallel.

**Fan-out heuristic:** Be conservative. If in doubt, fan out. It's better to dispatch two reviewers with clean context than one reviewer with truncated context.

If fanning out, partition files into groups where each group:
- Contains files from the same module/directory
- Has its own entry points and tests where possible
- Gets a copy of the structural inventory for orientation

### 4. Dispatch Reviewer(s)

#### Single Pass

Dispatch the `blank-slate-review:codebase-reviewer` agent with the structural inventory and file list.

```
<invoke name="Agent">
<parameter name="subagent_type">blank-slate-review:codebase-reviewer</parameter>
<parameter name="description">Review codebase: [scope summary]</parameter>
<parameter name="prompt">
## Structural Inventory

[PASTE SCOUT INVENTORY HERE]

## Files to Review

[LIST ALL SELECTED FILE PATHS, ONE PER LINE]

## Scope

[SCOPE DESCRIPTION]

Read every listed file and produce your review following the output contract in your instructions.
</parameter>
</invoke>
```

#### Fan-out

Dispatch multiple `blank-slate-review:codebase-reviewer` agents in parallel, one per module partition. Each gets the full structural inventory (for orientation) but only its partition's files.

```
<invoke name="Agent">
<parameter name="subagent_type">blank-slate-review:codebase-reviewer</parameter>
<parameter name="description">Review module: [module name]</parameter>
<parameter name="prompt">
## Structural Inventory

[PASTE SCOUT INVENTORY HERE]

## Files to Review

[LIST THIS PARTITION'S FILE PATHS ONLY]

## Scope

This is a partitioned review. You are reviewing the [module name] module as part of a larger codebase review. Focus on your assigned files.

Read every listed file and produce your review following the output contract in your instructions.
</parameter>
</invoke>
```

When all reviewers return, merge the results:

1. Concatenate findings from all reviewers
2. Re-number finding IDs sequentially (C1, C2, ..., H1, H2, ..., etc.)
3. Deduplicate: if two reviewers flagged the same file:line with the same issue, keep one
4. Merge remediation themes: combine overlapping themes from different reviewers, update finding ID references
5. Recalculate metrics

### 5. Present Output

Print the complete review to stdout. Use the exact output contract format from the reviewer agent. If results were merged from fan-out, the merged output should be seamless -- the user should not need to know how many reviewers were dispatched.

After printing the review, offer to write the findings to a file:

```
<invoke name="ToolSearch">
<parameter name="query">select:AskUserQuestion</parameter>
<parameter name="max_results">1</parameter>
</invoke>
```

Then ask:

```
Would you like me to write these findings to a file?
- Yes, write to [suggest a path like docs/review-YYYY-MM-DD.md or review.md]
- No, stdout is fine
```

If the user says yes, write the review output to the specified file. Do not commit it -- let the user decide.

## Context Discipline

This skill is designed around context cleanliness. Follow these rules:

- **No extraneous tool calls.** Every Glob, Read, Grep, or Bash call should directly serve the scout or sampling phases. Do not explore out of curiosity.
- **No commentary between phases.** Move from scout to sampling to dispatch without narrating your thought process at length. Brief status updates only.
- **No redundant reads.** If the scout already told you what languages are present, do not re-scan for languages.
- **Subagent prompts are self-contained.** The reviewer agent should have everything it needs in its prompt -- structural inventory and file list. Do not assume it can see your conversation history.
- **Merged output is clean.** If fan-out was used, the final output should read as a single coherent review, not a concatenation of separate reports.

## Common Rationalizations -- STOP

| Excuse | Reality |
|--------|---------|
| "Let me read a few more files to be thorough" | No. The sampling phase selected files for a reason. Trust the sample. |
| "I should review this file too, it looks interesting" | No. Stick to the sample. Adding files mid-review wastes context. |
| "I'll skip the scout and just start reading code" | No. The scout inventory drives intelligent sampling. Never skip it. |
| "Fan-out is overkill for this" | If you're unsure, fan out. Truncated context is worse than an extra subagent. |
| "I'll add some suggestions for improvements" | No. This is observation only. Findings and remediation, not implementation. |
