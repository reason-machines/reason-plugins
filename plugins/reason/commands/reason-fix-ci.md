---
name: reason-fix-ci
description: Have Reason make failing CI checks pass on a pull request or branch without skipping tests.
---

# Fix CI with Reason

Use the `reason` skill and the Reason MCP tools. The target is the pull request,
branch or repository the user named with this command.

1. Resolve the repository with `listRepositories`.
2. Call `createSession` with `body.repo`, a fresh `body.idempotency_key`, and
   `body.pr_number` when it is a pull request (so commits land on it), or
   `body.branch` for a named branch. Prompt: the failing check names and log
   excerpts the user gave, and "Read the failing checks, reproduce the failure
   locally, fix the cause, and push until required checks are green. Never
   skip, disable or weaken a test. Report each check's final state."
3. Reply right away with the session `url`.
4. Follow with `getSession` and report the `outcome`, the `pr_url` and which
   checks now pass.
