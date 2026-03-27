---
description: Create a simple but complete plan to execute a contained and known body of work
argument-hint: [basic prompt]
---

# Devise a Plan

**Basic Prompt:** `$1` (Optional)

If `$1` is not provided, prompt the user for a quick one to two sentence basic prompt of what they'd like to do.

## Before Starting

First we must create our branch structure and figure out where to put our plan:

1. Verify we are in a git repo:

   ```bash
   git rev-parse --git-dir
   ```

2. If we are on `main` or `master` check out to a new branch. This branch should have a name that makes sense in context. If you know the users initials, or the ticket identifier, then use those as prefixes:

   ```bash
   git checkout -b pbd/APP-312/my-fancy-feature
   ```

   ```bash
   git checkout -b APP-312/my-fancy-feature
   ```

   ```bash
   git checkout -b my-fancy-feature
   ```

3. Identify the plan document folder, some common ones are `docs/` or `prompts/` but often there are subfolders. Use the project's contextual structure to devise where things are:

   ```bash
   ls docs/
   ```

   ```bash
   ls prompts/
   ```

4. Create a new plan file. If the existing plan files use monotonically increasing values, continue the pattern. If they use more descriptive, human readable names continue the pattern:

   ````bash
   touch docs/plans/06.md

   ```bash
   touch prompts/my-fancy-feature.md
   ````

If any of these steps fail, stop and report the error to the user.

## Execute

1. **Clear Context:** Clear all context except the newly created file and the initial prompt the user passed to begin the plan.

2. **Engage the skill:** Use your Skill tool to invoke `quick-plan:devise-a-plan`. Invoke the skill with the first parameter being the newly created plan file, and the second being the initial prompt the user provided for this plan.

The skill should write a completed plan to the file provided.

### Once the skill has completed

If the user has the `one-shot:start` command installed, output a helper command to help them quickly and easily start implementation with it. Remind the user to clear their context first.

```
Plan is complete. First clear your context:

/clear

Then run the one-shot command for implementation:

/one-shot:start docs/plans/06.md pbd/APP-312/my-fancy-feature

```
