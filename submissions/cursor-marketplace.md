# Cursor Marketplace and Grok Bot

The plugin is ready in this repository and validated by
`python3 -m unittest tests.test_cursor_plugin`.

- `.cursor-plugin/marketplace.json`: marketplace `reason`, owner Reason Machines
- `plugins/reason/.cursor-plugin/plugin.json`: plugin `reason`, display name `Reason`, homepage `https://reasonmachines.com`, logo `assets/reason-logo.png`
- `plugins/reason/.cursor-plugin/mcp.json`: `{"mcpServers":{"reason":{"url":"https://mcp.reasonmachines.com/mcp"}}}`, OAuth only, no variables or secrets
- Skill `reason`, six commands (`/reason-fix`, `/reason-build`, `/reason-review`, `/reason-fix-ci`, `/reason-ask`, `/reason-status`) and rule `reason-handoff`
- README with install, usage, privacy, terms and support

**Owner action:** both forms need a sign-in. Publishing is free and Cursor
reviews each plugin by hand ([plugin reference](https://cursor.com/docs/reference/plugins)).
The owner gives the legal assent to the Cursor Marketplace Publisher Terms.

## Cursor

1. Sign in at [cursor.com/marketplace/publish](https://cursor.com/marketplace/publish).
2. Repository: `https://github.com/reason-machines/reason-plugins`
3. Accept the [Cursor Marketplace Publisher Terms](https://cursor.com/marketplace-publisher-terms) and submit.
   Cursor reviews the plugin and emails the submitter.

## Grok Bot

1. Open [x.ai/bot/marketplace/submit-a-plugin](https://x.ai/bot/marketplace/submit-a-plugin) and choose **Grok Bot** and **Cursor**.
2. Organization: `Reason Machines`; website `https://reasonmachines.com`.
3. Logotype URL: `https://raw.githubusercontent.com/reason-machines/reason-plugins/main/plugins/reason/assets/reason-logo.png`
4. MCP Server URL or Public GitHub Repository: `https://github.com/reason-machines/reason-plugins`
5. Brief description: the `description` in `plugins/reason/.cursor-plugin/plugin.json`.

## Before submitting

Install the plugin locally in Cursor from this repository, sign in, and run
`/reason-status` and "Which Reason workspace am I connected to?". This
confirms the OAuth flow and that tools are listed. Cursor shows the
server as `plugin-reason-reason` in approval prompts.
