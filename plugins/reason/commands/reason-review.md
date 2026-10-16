---
name: reason-review
description: Have Reason review a pull request for correctness, security, tests and breaking changes.
---

# Review a pull request with Reason

Use the `reason` skill and the Reason MCP tools. The pull request is the URL or
`owner/repo#number` the user gave with this command.

1. Resolve the repository `full_name` with `listRepositories`.
2. Call `createSession` with `body.repo`, a fresh `body.idempotency_key`, and a
   prompt such as: "Review pull request <URL>. Check correctness, security,
   test coverage, performance and breaking changes; verify claims by running
   the code or tests where useful. Post the findings as a pull request review,
   most severe first, each with file and line. Do not push commits." Add any
   focus areas the user named.
   (`triggerPrReview` requests GitHub's automated review bot, which the server
   currently refuses with 409 `pr_review_disabled`; a Session is the reliable
   path.)
3. Reply right away with the session `url`.
4. When `getSession` shows `status` is no longer `running`, summarise the
   findings from `result` with the link. If the user then wants fixes, start a
   Session with `body.pr_number` set so Reason pushes to that pull request.
