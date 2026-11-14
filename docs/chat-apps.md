# Discord

Discord is the only bundled chat channel. It shares the Python gateway, configured model, sessions, tools, and workspace with the WebUI.

Start with the [Discord setup guide](./guides/discord-ai-agent.md) to create a Discord bot, configure channel access, and verify a message. The WebUI can save the bot token and channel settings; the CLI remains available for setup, status, and gateway operations.

For manual configuration and the full Discord option reference, see [Discord channel configuration](./configuration.md#discord).

To add another built-in channel, a future change should include its Python package, focused tests, documentation, and an explicit maintenance decision. Third-party channel packages can use the [channel package guide](./channel-package-guide.md).
