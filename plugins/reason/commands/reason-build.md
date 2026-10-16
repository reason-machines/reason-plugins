---
name: reason-build
description: Hand a feature or new app to Reason - implement it with tests and deliver a pull request with proof.
---

# Build with Reason

Use the `reason` skill and the Reason MCP tools. The feature is whatever the
user wrote with this command (plus relevant context from the conversation).

1. Pick the repository with `listRepositories`. For a brand-new app with no
   repository, omit `repo` and say in the prompt where the result should be
   delivered.
2. Call `createSession` with `body.repo` (if any), a fresh
   `body.idempotency_key`, and a self-contained `body.prompt`: the user story
   in the user's words, acceptance criteria ("done when ..."), design or API
   references, areas to touch or avoid, and "Add tests, run them, and open a
   pull request with the proof in its body; include screenshots for UI
   changes."
3. Reply right away with the session `url`.
4. Follow it with `getSession` until `status` leaves `running`, then report the
   `outcome`, `pr_url` and a summary of `result`. Send follow-up requirements
   with `sendSessionMessage` instead of starting a new Session.
