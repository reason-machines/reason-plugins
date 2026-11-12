# Muse

Portal: [muse.ai/platform](https://muse.ai/platform) → **Submit a connector**. Intake then continues at
[platform.muse.ai](https://platform.muse.ai/) (guidelines: [platform.muse.ai/docs](https://platform.muse.ai/docs)).

**Owner action** (portal steps below are from the public guidelines and earlier
notes; they are unverified until the owner signs in, because the portal was
logged out when this was written):
- Sign in with a `@reasonmachines.com` work email.
- Accept the Muse developer terms and confirm authority over the brand assets.
- Business verification for Ara Software, Inc. (unverified until seen in the
  portal). The guidelines page fetched on 2026-11-12 at 04:2x UTC had a
  "Business verification and terms" section asking for "the business
  information and supporting evidence requested to verify your organization".
  An earlier fetch the same day had no such section, so the page is changing.
  It names no verification provider: do not assume Persona. Do only what the
  portal itself asks for.
- Answer the **data processing questionnaire**.
- Enter the dedicated reviewer test account.

Muse also asks for API or MCP documentation that covers setup, inputs and
outputs, read/write classification, sensitive designations, permissions, side
effects, status handling, errors and rate limits, and it checks that sensitive
writes ask for approval on every use. The public
[MCP docs](https://docs.reasonmachines.com/docs/mcp) cover setup, OAuth and
scopes; the per-tool read/write and destructive annotations come from the
server. Confirm the docs cover status handling, errors and rate limits before
submitting, and add a per-tool read/write/sensitive table if the portal's
annotation step is not live yet.

## Step 1: Overview

| Field | Value |
|---|---|
| Connector name | `Reason` |
| Company or developer | `Reason Machines` |
| Product website | `https://reasonmachines.com` |
| Example prompts | "Start a Reason session in acme/web to fix the failing date-parsing test and open a pull request." / "Show my recent Reason sessions and their pull requests." / "What is the status of my last Reason session?" / "Tell that session to also add a regression test." / "Review https://github.com/acme/web/pull/42 with Reason." |
| Icon | `plugins/reason/assets/reason-logo.png` (512×512 PNG) or `https://reasonmachines.com/favicon.svg` |
| Accepts payments | No |
| Your name / Work email | Owner (company email) |
| Support email or URL | `contact@reasonmachines.com` |
| Privacy policy | `https://reasonmachines.com/privacy-policy` |
| Terms of service | `https://reasonmachines.com/terms-of-service` |

## Step 2: Technical specs

| Field | Value |
|---|---|
| Connection type | **Existing MCP** |
| Hosted MCP endpoint | `https://mcp.reasonmachines.com/mcp` |
| API or MCP documentation | `https://docs.reasonmachines.com/docs/mcp` |
| Access requirements | Requires a Reason account. Sessions that change code need a GitHub repository connected to the Reason workspace. Each connection is bound to the workspace and permissions chosen at sign-in. |
| Authentication methods | **OAuth with PKCE** (also supports API keys for headless use) |

## Developer portal intake

- **Business verification:** the owner provides only what the portal asks for
  to verify Ara Software, Inc. (step, provider and form unverified).
- **Data processing questionnaire:**
  - Answer only from current, documented controls. The
    [security page](https://reasonmachines.com/security) and privacy policy are
    the public references.
  - The connector can read and write workspace data: session conversations,
    repository code changes through pull requests, and memory notes. Those
    outputs can include whatever users put in them, so do not answer
    "None of these" for sensitive data without checking.
  - Attach a SOC 2 report only if one exists and covers the controls you claim.
- **Technical details:**
  - Settings: OAuth; client registration through **DCR**. Reason does not
    support CIMD, so Muse falls back to DCR.
  - Scopes: leave empty or use the defaults. The server grants its default scope
    set when none is requested.
  - Enter the reviewer account (see [README](README.md), step 1).
  - Run the portal's sign-in test, then check the tool listing shows the tools
    with their annotations. (Button names are unverified.)
- Explain to reviewers what `createSession` does: it starts a real Reason
  session that runs on a cloud machine, uses the reviewer workspace's Reason
  usage allowance, and can push a branch and open a pull request in the
  connected sample repository. Its effects stay inside the reviewer workspace
  and that repository. It is a write tool (`readOnlyHint: false`), not a
  destructive one. Whether a session counts against paid usage depends on the
  reviewer workspace's plan; check that before giving reviewers access.
- The Muse portal being logged out proves nothing about whether a private
  draft exists; sign in and check before starting a new submission.
