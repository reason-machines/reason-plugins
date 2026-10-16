---
name: reason-fix
description: Hand a bug to Reason - reproduce it, fix the root cause, add a regression test and open a pull request.
---

# Fix a bug with Reason

Use the `reason` skill and the Reason MCP tools. The bug is whatever the user
wrote with this command (plus anything relevant earlier in the conversation).

1. Find the repository with `listRepositories` (match a name or URL the user
   gave; ask once only if it is genuinely ambiguous). If the bug is on an open
   pull request, note its number.
2. Call `createSession` with `body.repo`, a fresh `body.idempotency_key`, and a
   self-contained `body.prompt` that contains: the symptom in the user's words,
   exact error text or stack traces, reproduction steps, expected behaviour,
   and: "Reproduce the bug first, fix the root cause, add a regression test,
   and open a pull request whose body shows the check failing before the fix
   and passing after." Add `body.pr_number` only to push the fix onto that
   existing PR.
3. Reply right away with the session `url` and one line on what Reason is
   doing.
4. Follow the Session with `getSession` (fields
   `status,outcome,result,pr_url,url`). When `status` leaves `running`, report
   the `outcome`, the `pr_url`, and a short summary of `result`. If `outcome`
   is `action_required`, relay exactly what Reason needs.
