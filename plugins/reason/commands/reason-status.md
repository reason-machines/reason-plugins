---
name: reason-status
description: Show the status, result and pull request of recent or named Reason sessions.
---

# Check Reason sessions

Use the `reason` skill and the Reason MCP tools.

1. If the user named a session (a link, an id, or words from its title), find
   it: an id or `.../agents/<id>` link goes straight to `getSession`; words go
   to `listSessions` with `search`. Otherwise call `listSessions` with
   `first: 10`.
2. For each relevant Session, report the title, `status`, `outcome`,
   `pr_url` (if any), the session `url`, and a one-line summary of `result`.
3. For a Session that ended `action_required`, say exactly what it needs. Offer
   to reply with `sendSessionMessage`, retry with `retrySession`, or stop a
   running one with `cancelSession`, but don't do these without the user's
   go-ahead.
