# Reason plugin

Hand coding tasks to Reason agents through MCP: fix bugs, build features, review
pull requests, and fix CI. Follow each task through its session link and retrieve
the result or pull request.

## Install in Cursor

Once the Reason listing is live in the Cursor Marketplace, open it and choose
**Add to Cursor**.

Until then, [add the Reason MCP server to Cursor](https://cursor.com/link/mcp/install?name=reason&config=eyJ1cmwiOiJodHRwczovL21jcC5yZWFzb25tYWNoaW5lcy5jb20vbWNwIn0%3D).
This connects the server only, without the plugin's skill, commands, or rule.

## Install in Claude Code

```sh
claude plugin marketplace add reason-machines/reason-plugins
claude plugin install reason@reason
```

Open `/mcp` in Claude Code and authenticate Reason when prompted.

## Sign in and configure

The plugin connects to `https://mcp.reasonmachines.com/mcp`. Complete the browser
OAuth sign-in, choose your Reason workspace, review the permissions, and connect.
No API key, environment variables, or plugin variables are required.

## Use the plugin

Ask "Show my recent Reason sessions" or run `/reason-status`. To hand off a coding
task, ask "Fix the login bug in my repository and open a pull request" or use
`/reason-fix` followed by the task and repository name.

See the [repository README](../../README.md) for the full command list, other
clients, migration instructions, and support. The [Reason MCP documentation](https://docs.reasonmachines.com/docs/mcp)
explains authentication, permissions, and the available tools.
