---
name: reason-ask
description: Ask Reason a question about a codebase and get an answer that cites files, without code changes.
---

# Ask Reason about a codebase

Use the `reason` skill and the Reason MCP tools. The question is whatever the
user wrote with this command.

1. Resolve the repository with `listRepositories`.
2. Call `createSession` with `body.repo`, a fresh `body.idempotency_key`, and the
   prompt: "Answer only; make no code changes and open no pull request:
   <question>. Cite the files and line numbers you relied on."
3. Reply right away with the session `url`, then follow it with `getSession`
   and relay `result` once `status` leaves `running`. Send follow-up questions
   to the same Session with `sendSessionMessage`.
