# Reason directory submissions

Submission packages for listing the Reason MCP server in the four directories
that external MCP indexes check: the Claude Connectors Directory, the ChatGPT
plugin directory, the Cursor Marketplace (which Grok Bot also reads) and Muse.

Every listing must use the same identity so that indexes match it to the
server:

| Field | Value |
|---|---|
| Name | `Reason` |
| Website | `https://reasonmachines.com` |
| MCP endpoint | `https://mcp.reasonmachines.com/mcp` (Streamable HTTP) |
| MCP `serverInfo` | name `reason`, title `Reason`, websiteUrl `https://reasonmachines.com` |
| Documentation | `https://docs.reasonmachines.com/docs/mcp` |
| Privacy policy | `https://reasonmachines.com/privacy-policy` |
| Terms of service | `https://reasonmachines.com/terms-of-service` |
| Security page | `https://reasonmachines.com/security` |
| Support contact | `contact@reasonmachines.com` |
| Legal entity (as named in the policies) | Ara Software, Inc. |
| Publisher name shown to users | Reason Machines |
| Icon | [`plugins/reason/assets/reason-logo.png`](../plugins/reason/assets/reason-logo.png) (512×512 PNG, opaque plate); vector: `https://reasonmachines.com/favicon.svg` |
| MCP Registry entry | `io.github.reason-machines/reason`, active since 2026-10-11 |

| Directory | Package | Status on 2026-11-12 |
|---|---|---|
| Claude Connectors Directory | [claude-connectors-directory.md](claude-connectors-directory.md) | Not listed; no submission on record |
| ChatGPT plugin directory | [chatgpt-plugin-directory.md](chatgpt-plugin-directory.md) | Draft exists (v1.1.1, not submitted, not published); reuse it |
| Cursor Marketplace and Grok Bot | [cursor-marketplace.md](cursor-marketplace.md) | Plugin ready in this repository; not listed; no submission on record |
| Muse | [muse.md](muse.md) | Not listed; no submission on record |

"No submission on record" means no Reason session, pull request or issue
records a submission. A submission made directly in a portal would not appear
there, so check each portal first (step 0 below). A logged-out portal proves
nothing either way.

ChatGPT already has a draft in the OpenAI "Reason Machines" organization:
plugin version 1.1.1, MCP `https://mcp.reasonmachines.com/mcp` configured,
authorized and domain-verified, with five positive and three negative review
cases saved from its ZIP. Update that draft; do not create a second plugin.

## Server facts the forms ask for

- **Transport:** Streamable HTTP at one fixed URL. Every user connects to the same URL.
- **Authentication:** OAuth 2.1 authorization code with PKCE (S256), discovered
  through `https://mcp.reasonmachines.com/.well-known/oauth-protected-resource/mcp`.
  - Authorization server: `https://api.reasonmachines.com`
  - Authorize: `https://api.reasonmachines.com/mcp/oauth/authorize`
  - Token: `https://api.reasonmachines.com/mcp/oauth/token`
  - Dynamic Client Registration: `https://api.reasonmachines.com/mcp/oauth/register` (public clients, `token_endpoint_auth_method: none`)
  - Refresh tokens: yes (`offline_access`)
  - Client ID Metadata Documents (CIMD): not supported; clients fall back to DCR
  - A Reason API key also works as `Authorization: Bearer <key>` for headless clients.
    Directory submissions use OAuth.
- **Consent:** the user signs in to Reason, chooses a workspace and reviews
  the requested permissions. Every tool call is bounded by that workspace
  membership, role and the granted scopes.
- **Tools:** a standard workspace with all scopes sees 171 tools. Every tool has
  a `title` and explicit `readOnlyHint`, `destructiveHint` and `openWorldHint`
  booleans: 78 are read-only and 27 are destructive. `openWorldHint` is `true`
  on all 171, although most tools stay inside the connected workspace; OpenAI's
  guidelines allow `false` for tools bounded to a private workspace, so this is
  a server-side decision to make before review. No tool name mentions billing,
  plans, checkout, credits or payments. That is a name-only check: whether any
  tool's description or behaviour offers a purchase, upsell or checkout link is
  still being audited (see the ChatGPT guide's guideline check). The list
  shrinks to the scopes the user grants.
- **Data handling:** the API is Reason's own (first-party). The connector does
  not process payments or handle health data. It reads and writes the user's
  Reason workspace data: sessions and their conversations, repositories
  connected to the workspace, Loops, memory notes and devices.

## Example prompts (real tools)

| Prompt | Tools |
|---|---|
| "Which Reason workspace am I connected to?" | `getSelf` |
| "List the repositories Reason can work on." | `listRepositories` |
| "Show my recent Reason sessions and which ones opened pull requests." | `listSessions` |
| "Start a Reason session in acme/web to fix the failing date-parsing test and open a pull request." | `createSession` |
| "What is the status of that session? Give me the pull request link." | `getSession` |
| "Tell that session to also add a regression test." | `sendSessionMessage` |
| "Review https://github.com/acme/web/pull/42 with Reason." | `triggerPrReview` |
| "Every weekday at 9am, have Reason triage new issues in acme/web." | `createReasonLoop` |

## Owner checklist

These steps need an owner of the Reason Machines accounts: a portal sign-in,
publisher or business verification, legal attestations, or a reviewer account.
Nothing here costs money, except where a portal needs a plan that Reason does
not already have. Do not buy a plan for this; record the gap instead.

0. **Check for earlier submissions.** Open each portal and look for an existing
   draft or a submission under review before starting a new one:
   [claude.ai/directory/manage](https://claude.ai/directory/manage),
   [platform.openai.com/plugins](https://platform.openai.com/plugins),
   [cursor.com/marketplace/publish](https://cursor.com/marketplace/publish) (and the
   publisher's email for review mail), and [platform.muse.ai](https://platform.muse.ai/).
1. **Create one reviewer test account** (all four directories use it):
   - A dedicated Reason account in its own workspace, for example
     `reviewer@reasonmachines.com`. Use no real customer data.
   - Connect one public sample GitHub repository to that workspace and run two or
     three sessions in it, so that `listSessions` and `getSession` return data.
   - ChatGPT requires a sign-in that works without email or SMS codes, magic
     links or MFA approval. Check which Reason sign-in method meets that before
     sharing the account.
   - Enter the credentials only in each portal's private reviewer fields. Never
     put them in this repository, a pull request or chat.
2. **Cursor and Grok Bot** ([cursor-marketplace.md](cursor-marketplace.md)):
   sign in at cursor.com, submit `https://github.com/reason-machines/reason-plugins`
   at [cursor.com/marketplace/publish](https://cursor.com/marketplace/publish), and accept the
   Cursor Marketplace Publisher Terms. Then submit the Grok Bot form. No test
   account is needed.
3. **Claude** ([claude-connectors-directory.md](claude-connectors-directory.md)):
   sign in to [claude.ai/directory/manage](https://claude.ai/directory/manage).
   Any paid personal Claude account (Pro, Max or Ultra) can submit. On Team,
   an Owner submits. On Enterprise, an Owner submits or grants the Directory
   permission to a member through a custom role.
   Nothing needs to be bought. Enter the listing fields, the reviewer account
   (in the portal's private fields only) and the seven compliance acknowledgments. It publishes as
   a Community listing. Anthropic decides on its own whether to escalate it to
   Verified; there is no application.
4. **ChatGPT** ([chatgpt-plugin-directory.md](chatgpt-plugin-directory.md)):
   - Open the existing v1.1.1 draft. Do not create a new plugin.
   - An OpenAI organization owner (or a member with Apps Management Write)
     confirms the verified developer identity shows "Reason Machines".
   - Upload the 1.3.0 ZIP to that draft with **Upload plugin to make changes**.
     Domain verification is already done: keep the existing challenge token,
     host and saved OAuth client.
   - Enter the reviewer account in **Review details**, add the walkthrough video
     and submit with the policy attestations. Approval does not publish: the
     owner selects **Publish plugin** separately.
5. **Muse** ([muse.md](muse.md)):
   - Submit at [muse.ai/platform](https://muse.ai/platform) from a
     `@reasonmachines.com` work email.
   - Complete business verification for Ara Software, Inc. if the portal asks
     for it (the public guidelines describe business verification; check the
     portal for the exact step).
   - Answer the data processing questionnaire from current evidence only.
   - Enter the reviewer account in Technical details and run the sign-in test.
6. **Record each submission** below: date, who submitted, portal URL and the
   endpoint version submitted.

## Submission log

| Directory | Submitted | By | Portal reference | Result |
|---|---|---|---|---|
| Claude | | | | |
| ChatGPT | | | | |
| Cursor | | | | |
| Grok Bot | | | | |
| Muse | | | | |
