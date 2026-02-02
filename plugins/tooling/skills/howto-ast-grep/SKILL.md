---
name: howto-ast-grep
description: Use when searching for or transforming code patterns structurally - provides ast-grep CLI syntax, metavariable patterns, and language-specific examples for precise AST-based code search and rewriting
---

# Using ast-grep for Structural Code Search

## Overview

ast-grep (`sg`) matches code by AST structure, not text. Use it instead of grep/ripgrep when you need to match code patterns regardless of whitespace, variable names, or formatting. Patterns must be valid, parsable code in the target language.

## When to Use

**Prefer ast-grep over grep when:**

- Finding function calls with specific argument shapes
- Matching patterns where variable names differ but structure is the same
- Rewriting code patterns across a codebase (migrations, deprecations)
- Finding anti-patterns that regex can't express (e.g. "await inside a loop")

**Use grep instead when:**

- Searching for string literals, comments, or non-code text
- Simple keyword search (import names, error messages)
- ast-grep is not installed

## CLI Quick Reference

```bash
# Search for a pattern
sg run -p 'console.log($$$ARGS)' -l javascript src/

# Search and replace (interactive)
sg run -p '$A && $A()' -r '$A?.()' -l typescript --interactive src/

# Apply all replacements without prompting
sg run -p 'var $X = $Y' -r 'const $X = $Y' -l javascript -U src/

# JSON output for programmatic use
sg run -p '$FUNC($$$)' -l python --json src/

# Read from stdin
echo 'let x = 1' | sg run -p 'let $X = $Y' -l javascript --stdin
```

## Metavariable Syntax

| Syntax | Matches | Example |
|--------|---------|---------|
| `$NAME` | Exactly one AST node | `console.log($MSG)` matches `console.log("hi")` but not `console.log("hi", 2)` |
| `$$$NAME` | Zero or more nodes | `console.log($$$ARGS)` matches any number of arguments |
| `$_NAME` | One node, non-capturing | `$_OBJ.$METHOD()` matches without binding `$_OBJ` |

**Reuse enforces equality:** `$A == $A` matches `x == x` but not `x == y`.

## Language-Specific Patterns

Always pass `-l <language>`. The language determines how patterns are parsed.

**JavaScript/TypeScript:**

```bash
# Find React hooks
sg run -p 'use$HOOK($$$)' -l typescript src/

# Optional chaining candidates
sg run -p '$A && $A.$B' -r '$A?.$B' -l typescript src/

# Async/await patterns
sg run -p 'await $PROMISE' -l javascript src/
```

**Python:**

```bash
# Find print statements
sg run -p 'print($$$)' -l python src/

# Dictionary access patterns
sg run -p '$DICT[$KEY]' -l python src/

# With statement patterns
sg run -p 'with open($$$ARGS) as $F: $$$BODY' -l python src/
```

**Go:**

```bash
# Error handling
sg run -p 'if $ERR != nil { return $$$VALS }' -l go ./

# Function calls
sg run -p '$PKG.$FUNC($$$)' -l go ./
```

**Rust:**

```bash
# Unwrap calls (potential panics)
sg run -p '$EXPR.unwrap()' -l rust src/

# Match expressions
sg run -p 'match $VAL { $$$ARMS }' -l rust src/
```

## Pattern Pitfalls

| Mistake | Why It Fails | Fix |
|---------|-------------|-----|
| Using regex in `-p` | Patterns must be valid code | Write the code structure you want to find |
| `$VAR + Name` | Parsed as `$VARN + ame` | Use constraints or transform in YAML rules |
| Single quotes in C/Rust patterns | `'x'` is a char literal, not a string | Use `"x"` for strings |
| Forgetting `-l` flag | ast-grep cannot infer language from patterns | Always specify language explicitly |
| `$A($B, $C)` for variadic calls | Only matches exactly 2 args | Use `$A($$$ARGS)` for any arity |

## YAML Rules for Complex Matching

When CLI patterns aren't expressive enough, use YAML rules:

```yaml
id: no-unwrap-in-production
language: rust
rule:
  pattern: $EXPR.unwrap()
  not:
    inside:
      kind: function_item
      has:
        field: name
        regex: '^test_'
message: "Use expect() or proper error handling instead of unwrap()"
severity: warning
```

**Key rule combinators:**

- `all`: All sub-rules must match (AND)
- `any`: Any sub-rule can match (OR)
- `not`: Sub-rule must NOT match
- `inside`: Target is inside another node
- `has`: Target contains a descendant
- `follows`/`precedes`: Sibling ordering

**Run rules:** `sg scan --rule path/to/rule.yml src/`

## Red Flags

- Using grep with complex regex when ast-grep would match the structure directly
- Forgetting `$$$` and missing variadic matches
- Writing patterns that aren't valid code in the target language
- Not specifying `-l` and getting parse failures
