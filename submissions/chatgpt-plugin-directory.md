# ChatGPT plugin directory

> **Not ready to submit.** The 1.3.0 package builds and validates, but
> submission still needs real runs of all eight existing cases with the reviewer
> account, the walkthrough video and the dedicated reviewer account. The package
> omits `review.test_cases` to preserve the saved cases; recovering their six
> unavailable historical texts is not required to build this update. Nothing has
> been uploaded, saved or submitted in the portal.

Portal: [platform.openai.com/plugins](https://platform.openai.com/plugins). One plugin ZIP lists Reason in both
ChatGPT and Codex.
Guide: [Upload and submit your plugin](https://developers.openai.com/plugins/deploy/submission) and
[Plugin guidelines](https://developers.openai.com/plugins/plugin-guidelines).

## Existing draft: reuse it

The OpenAI organization "Reason Machines" already has a Reason plugin draft:

- Package version 1.1.1, status **Not submitted** / **Not published**.
- MCP tab: `https://mcp.reasonmachines.com/mcp` is **Configured**, authentication
  is **Authorized** and the domain is **Verified**. The tool scan is old, so the
  tab shows **Needs attention**.
- Five positive and three negative review cases are saved. The draft's earlier
  ZIP manages them, so they are read-only in the portal. The draft also has
  release notes.

Update this draft. Do not create a second plugin. Keep the existing domain
challenge token, host and saved OAuth client: do not replace or reconnect them.

**Owner action:**
- An organization owner, or a member with **Apps Management Write**, uploads and
  submits. The developer identity shown is the verified individual or business
  identity selected at upload.
- Enter reviewer credentials in **Review details**. Never put them in this
  repository, the ZIP or chat.
- Add the walkthrough video URL.
- Accept the policy attestations at **Submit for review**.
- After approval, select **Publish plugin**. Approval does not publish it.

## Package

The ZIP is the portable Agent Plugins package in `plugins/reason/`. Its root
`plugin.json` carries the listing (`extensions.com.openai.interface`). The
package leaves out the Cursor, Claude and Codex compatibility files, because
ZIPs with hooks or app references are rejected. Build it from the repository
root:

```sh
python3 -m pip install --user -r scripts/requirements.txt
python3 scripts/build_chatgpt_zip.py            # writes reason-chatgpt.zip
python3 -m unittest tests.test_chatgpt_package  # validates it
```

The ZIP contains only `plugin.json`, `mcp.json`, `skills/` and `assets/`.
`tests/test_chatgpt_package.py` checks it against the Agent Plugins 1.0.0
schemas kept in `tests/schemas/` and against the portal's public-submission
limits. Build only with this script: it runs the same `check_review` guard the
tests use, which refuses any non-null `review.test_cases` (including `{}`). It
also refuses listing URLs that are not https, lack a host, embed credentials or
exceed 1,024 characters; empty required listing text; icons that are not
complete, square PNGs of 48 to 4,096 pixels a side; icon paths outside the
package; and symlinks in the package. PNG validation uses Pillow to verify and
fully decode each image, plus checks for exact raster length and chunk structure. A hand-made `zip -r` skips all of these checks.

`mcp.json` declares exactly one server, `reason`, at
`https://mcp.reasonmachines.com/mcp` with no headers. Authentication comes
from OAuth discovery.

Upload it to the existing draft with **Upload plugin to make changes**. Its
version is 1.3.0, above the draft's 1.1.1. Raise `version` in every
`plugin.json` (and `.cursor-plugin/marketplace.json`) for each later upload.
The tests check that they agree.

## Listing fields (from `plugin.json`)

| Field | Value |
|---|---|
| displayName | `Reason` |
| developerName | `Reason Machines` (must match the verified identity) |
| shortDescription | `Hand off code to cloud agents` (portal limit: 30 characters) |
| longDescription | See `plugin.json` |
| category | `Productivity` (use Developer Tools if the portal offers it) |
| websiteURL | `https://reasonmachines.com` |
| privacyPolicyURL | `https://reasonmachines.com/privacy-policy` |
| termsOfServiceURL | `https://reasonmachines.com/terms-of-service` |
| supportURL | `https://github.com/reason-machines/reason-plugins/issues` |
| logo / logoDark | `assets/reason-logo.png` / `assets/reason-logo-dark.png` |

## MCP connection

The draft's connection is already set up: OAuth with **Dynamic Client
Registration (`dcr`)**, no client secret, and a verified domain. Two hosts
matter here:

- **Product domain, `reasonmachines.com`:** the parent domain whose challenge
  verifies the existing draft (as relayed from the supervisor's read-only
  portal check). Keep that token as it is.
- **MCP host, `mcp.reasonmachines.com`:** where the MCP endpoint lives. Its
  challenge route is optional and not in use.

The portal accepts a challenge on the MCP host or an eligible parent domain. The
draft is already verified, so configure nothing on either host.

The monorepo's MCP host can also serve
`https://mcp.reasonmachines.com/.well-known/openai-apps-challenge` from an
environment variable. That route is optional. It returns 404 while the variable
is unset, and the variable stays unset. Do not set it, and do not replace the
challenge that verifies the current draft. Only if OpenAI later asks for a new
challenge on that host would the owner store the token as a deployment secret
(never in chat or a file) and redeploy.

The tool scan says **Needs attention** because it is old. The owner decides when
to rescan. Do not rescan or reconnect as part of preparing this package.

API-key authentication cannot be configured in the portal, so the submission
uses OAuth only.

## Guideline check

From the [plugin guidelines](https://developers.openai.com/plugins/plugin-guidelines),
checked against the live server's `tools/list` on 2026-11-12:

- 171 tools. Every tool has a title and explicit `readOnlyHint`,
  `destructiveHint` and `openWorldHint` booleans (78 read-only, 27 destructive).
- `openWorldHint` is `true` on all 171. The guidelines allow `false` for tools
  confined to a private account or workspace, which describes most Reason tools.
  The value is not wrong for safety, but the server team should decide it before
  review. It is a server change, not a package change.
- No tool name mentions billing, plans, checkout, subscriptions, credits or
  payments, and the listing text advertises no pricing or upgrades. A full
  description-level audit of every tool for upsell links is being done
  separately.
- The display name has no "MCP" or "Plugin" suffix.

## Review information

The draft's eight review cases stay as they are. This package's `plugin.json`
has no `review.test_cases`. The
[submission guide](https://developers.openai.com/plugins/deploy/submission#configure-onboarding-review-and-publication)
says:

> Imported test cases are read-only in the dashboard: edit the package and
> upload it again to change them. Omitting `test_cases`, or setting it to null,
> preserves existing cases; `test_cases`: {} clears both lists.

The build script refuses to write `test_cases: {}`, and
`tests/test_chatgpt_package.py` fails if `plugin.json` declares non-null test cases.
Only two of the saved cases are on record outside the portal:

- Positive 1: "Identify the connected reviewer workspace", tool `getSelf`,
  expected "Returns the authenticated reviewer identity and connected workspace.
  Only claims permissions actually returned; no bearer token or secret appears."
- Negative 1: "Do not launch workspace work for a general programming question".

The other six are not in this repository's history or in any Reason session
found, so a package built from the original v1.1.1 source cannot be rebuilt
yet. This does not block an update that omits `review.test_cases`: omission
preserves all eight saved cases. Recover the original texts before changing
those cases or claiming to have run them all. Do not write replacements from
memory.

Negative cases are prompts where the plugin should **not** trigger. They are not
tool calls that are expected to fail.

Still needed from the owner:
- Reviewer credentials in **Review details**, with a sign-in that needs no
  email or SMS codes, magic links or MFA (see [README](README.md), step 1).
- A walkthrough video URL showing the five positive cases.
- Release notes for 1.3.0 if the saved ones no longer fit, for example: "Updates
  the Reason plugin to 1.3.0: new hexagon logo and listing text that matches the
  current tools (sessions, pull requests, reviews and Loops)."

Then select **Submit for review** and complete the attestations. After
approval, the owner chooses when to select **Publish plugin**.
