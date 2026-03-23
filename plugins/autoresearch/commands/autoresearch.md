---
description: Start or resume an autonomous experiment loop with optional time limit
argument-hint: [duration-minutes]
---

# Autoresearch

**Duration:** `$1` minutes (optional - no limit if omitted)

## Setup

1. If `$1` is provided, write or update `autoresearch.config.json` in the current directory:

   ```json
   {
     "maxDurationMinutes": $1
   }
   ```

   If the file already exists, merge `maxDurationMinutes` into it (preserve existing fields like `workingDir` and `maxIterations`).

2. If `autoresearch.md` already exists in the current directory (or `workingDir` if configured), this is a **resume**. Announce: "Resuming existing autoresearch session with a {$1}-minute time limit." and skip to step 3.

   If no `autoresearch.md` exists, this is a **new session**. Announce: "Starting new autoresearch session." and continue to step 3.

3. Invoke the skill:

   ```
   Skill: autoresearch:autoresearch-create
   ```

   The skill handles everything from here: gathering the optimization target (for new sessions), reading existing state (for resumes), and running the loop.
