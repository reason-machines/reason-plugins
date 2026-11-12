# Claude Connectors Directory

Portal: [claude.ai/directory/manage](https://claude.ai/directory/manage) → **Submit new** → **MCP connector**.
Requirements: [Submit a connector](https://claude.com/docs/connectors/building/submission).

**Owner action:** the portal needs a paid Claude account. Any personal Pro,
Max or Ultra account can submit. On Team, an Owner submits. On Enterprise, an
Owner submits or grants the Directory permission to a member through a custom
role ([Publish to the directory](https://claude.com/docs/directory/publish)). No
purchase is needed. It also needs a reviewer test account, whose credentials go
only in the portal's private fields (see [README](README.md), step 1), and
seven compliance acknowledgments. The listing belongs to the organization you
submit from, so submit from the account that should own it long term. The listing then
publishes as **Community** after an automated policy scan. There is no
application for **Verified**: Anthropic escalates listings it judges highly
useful to a Verified review, in which reviewers test every tool, and that is
assessed automatically ([Connector verification](https://claude.com/docs/connectors/verification)).
Manufact counts a Community listing as half a check and a Verified listing as a
full one. A reviewer account that works and seeded data give the Verified
review the best chance.

## Readiness against the checklist

| Requirement | State |
|---|---|
| Remote HTTPS server | Yes: `https://mcp.reasonmachines.com/mcp` |
| OAuth 2.0 for user data | Yes: OAuth 2.1 with PKCE and DCR; no client secret to hand over |
| Every tool has a title and readOnlyHint/destructiveHint | Yes, all 171 tools (explicit booleans) |
| Tested in Claude as a custom connector | Owner confirms in **Test & launch**: add the URL under Settings → Connectors → Add custom connector, sign in, and run the example prompts |
| Documentation URL, privacy policy, support contact, icon | Yes (see below) |
| Reviewer test account | Owner creates it ([README](README.md), step 1) |

## Step 1: Connection

- URL: `https://mcp.reasonmachines.com/mcp`
- Users connect to different URLs: **No** (one URL for everyone)

## Step 2: Tools

These sync from the server. No tools are flagged for missing titles or annotations.

## Step 3: Listing

- **Server name** (≤100): `Reason`
- **One-liner** (≤200): `Hand coding work to Reason cloud agents: fix bugs, build features, review pull requests and fix CI in your GitHub repositories, then follow each session to its pull request.`
- **Description** (≤2,000):

  > Reason is an autonomous software engineer. Connect it to Claude to start and follow Reason sessions without leaving the conversation.
  >
  > Describe a task, such as fixing a bug, building a feature, reviewing a pull request, making failing CI pass, refactoring or answering a question about a codebase, and Reason runs it on its own cloud machine in your connected GitHub repository. Each session returns a live link, and when it changes code it opens a pull request with its checks and proof.
  >
  > From Claude you can:
  > - start a session in any repository connected to your Reason workspace;
  > - list your recent sessions and check their status, result and pull request;
  > - send a follow-up or correction to a running session;
  > - request a pull request review;
  > - schedule recurring engineering work as a Loop, such as a daily issue triage;
  > - read your workspace's memory notes, repositories and connected devices.
  >
  > Sign in with your Reason account and choose a workspace. Every action uses that workspace's permissions and the scopes you approve, and you can disconnect at any time. Reason sessions run asynchronously, so Claude reports the session link right away and can check back for the result.

- **Categories** (1-5): Developer tools; Productivity. Pick the closest names the portal offers.
- **Documentation URL:** `https://docs.reasonmachines.com/docs/mcp`
- **Privacy policy URL:** `https://reasonmachines.com/privacy-policy`
- **Support contact:** `contact@reasonmachines.com`
- **Icon:** `plugins/reason/assets/reason-logo.png` (512×512 PNG)
- **URL slug** (permanent once published): `reason`

## Step 4: Use cases

- **Primary use cases:** delegate coding tasks to cloud agents; follow sessions to their pull request; review pull requests; schedule recurring engineering work.
- **What users need first:** a Reason account (sign up at reasonmachines.com) with
  at least one GitHub repository connected to the workspace, which sessions that
  change code need.
- **Reads or writes:** both.

## Step 5: Company

- Company name: `Reason Machines` (legal entity in the policies: Ara Software, Inc.)
- Website: `https://reasonmachines.com`
- Primary contact: owner's `@reasonmachines.com` email (owner supplies)

## Step 6: Authentication

- Authentication requirement: **Required**
- Method: OAuth. Claude registers its own client through Dynamic Client
  Registration, so leave the Anthropic-held client ID and secret fields empty.

## Step 7: Data handling

- Underlying API: **our own** (first-party Reason API)
- Personal health data: **No**
- Sponsored content: **No**. The MCP tool results contain none.

## Step 8: Test & launch (reviewer access)

Paste into the reviewer instructions, then put the credentials in the portal's
private fields:

> 1. In Claude, add the connector and select Connect. A Reason sign-in page opens.
> 2. Sign in with the test account provided, choose the workspace "Reason MCP Directory Review", and approve the permissions.
> 3. Try these scratch-session prompts. They do not need a connected repository:
>    - "Which Reason account and workspace am I connected to, and what can this connection do?" (getSelf)
>    - "List my Reasons, my recent sessions, and any devices or machines I can run work on." (listReasons, listSessions, listDevices, listMachines)
>    - "Create a scratch Reason and start a cloud coding session in it that writes a small function with tests, under $1 and 5 minutes, and tell me whether the tests passed." (createReason, createSession, then getSession and listSessionEvents)
>    - "Run two separate cloud coding sessions at the same time, one writing a slugify function with tests and one a word-count function with tests, and report each result separately." (createSession twice, then getSession and listSessionEvents for each session)
>    - "In the scratch session you just ran, add a test for empty input and tell me if it passes." (sendSessionMessage to the same session, then getSession, listSessionMessages, and listSessionEvents)
> 4. Sessions run asynchronously. Wait for each session to finish and read its outcome before reporting whether its tests passed. Use only the scratch sessions created for this review.

These prompts describe five positive workflows verified through direct MCP calls
with mcpdo. The prompt wording has not been tested in Claude. This is not evidence
that every tool was exercised, and the parallel workflow verifies two cloud
sessions, not two Machines or physical computers. The three negative review cases
have not been run. Complete the remaining testing through Claude as a custom
connector or MCP Inspector before confirming the portal's every-tool requirement.

## Step 9: Compliance

The owner reads and accepts the seven acknowledgments, along with the
[Anthropic Software Directory Terms](https://support.claude.com/en/articles/13145338-anthropic-software-directory-terms)
and [Policy](https://support.claude.com/en/articles/13145358-anthropic-software-directory-policy).

## After submission

Track status at claude.ai/directory/manage. Escalations: `mcp-review@anthropic.com`.
Contacting Anthropic needs Adi's approval first.
