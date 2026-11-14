# CLI Reference

Use this page when you know what you want to run and need the command shape. For a guided first run, start with [`quick-start.md`](./quick-start.md).

## Choose a Command

| Goal | Command | Notes |
|---|---|---|
| Check the install | `nanobot --version` | If this fails, try `python -m nanobot --version` |
| Create or refresh config | `nanobot onboard` | Creates `~/.nanobot/config.json` and `~/.nanobot/workspace/` |
| Refresh config non-interactively | `nanobot onboard --refresh` | Preserves existing values and adds missing default fields without prompting |
| Use guided setup | `nanobot onboard --wizard` | Best when you prefer prompts over hand-editing JSON |
| Open the browser workbench | `nanobot webui` | Prepares local WebUI settings, starts the gateway, and opens the browser |
| Check readiness without calling a model | `nanobot status` | Summarizes config/workspace and validates the active provider/model configuration |
| Send one test message | `nanobot -m "Hello!"` | One-shot terminal request; `nanobot agent -m ...` is the explicit form |
| Run the gateway directly | `nanobot gateway` | Service/ops command for WebUI, Discord, cron, and heartbeat |
| Deliver a local trigger | `nanobot trigger <id> "message"` | Created first with `/trigger <name>` in the target chat/session |
| Manage optional features | `nanobot plugins list` | Shows channels and optional capabilities you can turn on |
| Check Discord setup | `nanobot channels status` | Show whether the bundled Discord channel is configured and enabled |
| Log in to OAuth model providers | `nanobot provider login <provider>` | Used by OpenAI Codex, xAI subscription, and GitHub Copilot providers |

## Global

```bash
nanobot --help
nanobot --version
nanobot --home ~/.nanobot-work onboard
python -m nanobot --help
python -m nanobot --version
```

`python -m nanobot ...` is useful when the package is installed but the `nanobot` script is not on `PATH`.

`--home <directory>` is a global option; place it before the subcommand. It selects `<directory>/config.json` and the default `<directory>/workspace/`. Explicit `--config` and workspace settings still apply. See [Multiple Instances](./multiple-instances.md) for runtime data locations and port selection. `-h` and `--help` display help.

### Coexisting with Sentinel Desktop

The Python package and Sentinel Desktop keep separate runtimes, configuration, workspaces, and state. When a running Desktop release publishes its private WebUI descriptor, an interactive `nanobot webui` asks which installation to use after authenticating a ready Desktop target. Use `Up`/`Down` to highlight an installation and `Enter` to confirm. `Ctrl+C` cancels with exit code 130 without attaching to Desktop or starting a Python backend. If Desktop is absent, busy, unavailable, or cannot be authenticated, the command reports the current Python executable and continues normally. A virtual environment's executable is shown without resolving it to its base interpreter.

Choosing Desktop for `nanobot webui` opens its already-running browser workbench and exits; closing the browser never stops the Desktop gateway. After Desktop is selected, a disconnect or incompatible reply ends that invocation with an error; it never silently switches to Python or launches a replacement. On macOS, browser URLs are delivered through native Launch Services rather than command-line arguments. A failed native handoff does not fall back to `open` or a `BROWSER` command, keeping bootstrap credentials out of launcher arguments.

On Windows, the shared browser launcher uses a private HTML redirect rather than passing a credential-bearing URL to a browser command. A short-lived, windowless Python helper receives the URL over an anonymous pipe, opens the redirect through the system's HTTP association, and attempts file cleanup after two minutes. The calling CLI can exit immediately after the launch acknowledgement; this helper does not start, stop, or keep a gateway alive. It does not honor `BROWSER` overrides. Redirects are stored in the current user's Windows Local AppData known folder, under `NanobotBrowserHandoff-v1`, with an explicit current-user-only protected ACL. An ACL-enforcing local filesystem and a non-reparse storage path are required; unsafe existing storage or failed browser handoff fails without raw-URL fallback. Abnormal termination can leave a private redirect behind. Later invocations retry cleanup of verified redirect files older than ten minutes, excluding active files; cleanup is not a guarantee of physical erasure or secrecy from same-user programs or administrators. No Python/Desktop settings, credentials, or history are imported between installations.

Other commands, including `nanobot agent`, config/workspace selectors, help, version, completion, and gateway lifecycle commands, keep their Python meaning. Target choices are not remembered, and Desktop settings are not copied into the Python installation.

## Common Patterns

### Manual Updates

Nanobot does not include an in-app package updater. Stop the gateway, back up configuration and data, then update through the tool that owns the installation. Keep the same environment, extras and launcher. See [Manual Updates and Data Migrations](./updating.md#installation-owners) for package, source and deployment guidance.

Most day-to-day commands use the default config and workspace. Advanced or multi-instance runs usually pass both paths explicitly:

```bash
nanobot agent --config ./bot-a/config.json --workspace ./bot-a/workspace -m "Hello"
nanobot gateway --config ./bot-a/config.json --workspace ./bot-a/workspace
```

Use `--verbose` on long-running processes when you need startup or runtime logs:

```bash
nanobot gateway --verbose
```

Long-running commands keep working until you stop them. Press `Ctrl+C` in that terminal to stop a foreground `nanobot gateway`. If you started the gateway with `--background`, use `nanobot gateway stop`.

## Setup

| Command | Description |
|---|---|
| `nanobot onboard` | Initialize or refresh the default config and workspace |
| `nanobot onboard --refresh` | Refresh an existing config without prompting, preserving existing values |
| `nanobot onboard --wizard` | Use the interactive setup wizard |
| `nanobot onboard --config <path> --workspace <path>` | Initialize or refresh a specific instance |

Default paths:

| Path | Default |
|---|---|
| Config | `~/.nanobot/config.json` |
| Workspace | `~/.nanobot/workspace/` |

## Status

| Command | Description |
|---|---|
| `nanobot status` | Summarize the default config/workspace and check Agent provider/model readiness |
| `nanobot status --config <path>` | Check a specific config file |
| `nanobot status --workspace <path>` | Show status with a workspace override |

Status does not send a model request. On success, run the printed `nanobot agent -m "Hello!"` command to verify network access and credentials. On failure, follow the printed WebUI **Settings → Models** or `nanobot onboard --wizard` route.

## Agent CLI

| Command | Description |
|---|---|
| `nanobot -m "Hello!"` | Send one message and exit |
| `nanobot agent -m "Hello!"` | Explicit one-shot agent command |
| `nanobot --workspace <path>` | Override workspace |
| `nanobot --config <path>` | Use a specific config file |
| `nanobot agent -m "Hello!" --session <id>` | Send a one-shot message in an existing session |
| `nanobot agent -m "Hello!" --workspace <path>` | Select a workspace for the one-shot request |
| `nanobot agent -m "Hello!" --config <path>` | Use a specific config file |

## Session Storage

Session state lives in `<config-dir>/sessions/<workspace-id>/sessions.sqlite3`, outside the agent-readable workspace. Existing JSONL conversations are imported on the first startup. JSONL migration is available from 0.3.6 through 0.4.x and is removed in **0.5.0**; installations with only JSONL data must upgrade through that window before using 0.5.0.

After a successful import, JSONL files and their checkpoints from `<workspace>/sessions/` move to `<config-dir>/sessions/<workspace-id>/jsonl-backup/`, preserving their contents outside the agent-readable workspace. JSONL files already in the private session directory remain there. An interrupted migration resumes on startup before Sentinel serves conversations; failed imports leave their source files unchanged.

WebUI chat history is saved in the same session database. The gateway automatically imports old `<config-dir>/webui/*.jsonl` files and numbered JSONL files inside `<config-dir>/webui/*.segments/` directories. If old history is damaged or cannot be matched to one conversation, startup stops with an error; resolve the reported problem before restarting.

The old WebUI history files remain unchanged as backups. Imported chats deleted after the upgrade stay deleted on restart. Keep the `webui` directory: it still contains sidebar preferences and other saved WebUI state.

Before changing versions, stop all Sentinel instances using the same config directory and back up that entire directory and the workspace together. Copying only `sessions.sqlite3` while Sentinel is running can miss recent messages. To downgrade, restore a complete pre-upgrade backup compatible with the older release. Older releases cannot read newly saved WebUI history; do not combine the current session database with old WebUI history files.

The CLI agent command is one-shot. It does not start an interactive terminal conversation; use the WebUI or Discord for ongoing chats.

## WebUI

| Command | Description |
|---|---|
| `nanobot webui` | Prepare local WebUI settings and open the browser; installer-managed environments launch persistently, other installations remain attached and follow gateway logs |
| `nanobot webui --detach` | Explicitly start or join a persistent gateway, open the browser and return control to the terminal |
| `nanobot webui --background` | Deprecated; prints the equivalent explicit `nanobot gateway --background` command and exits |
| `nanobot webui --dev` | Start the gateway and Vite together at `http://127.0.0.1:5173`, with live frontend updates |
| `nanobot webui --no-open` | Prepare and start the WebUI without opening a browser |
| `nanobot webui --no-dock` | Suppress the macOS Dock icon; detached mode remembers this choice until the next WebUI launch |
| `nanobot webui --port <port>` | Set the WebUI/WebSocket port |
| `nanobot webui --gateway-port <port>` | Override the gateway health port |
| `nanobot webui --yes` | Apply safe localhost WebUI defaults without confirmation; configure provider credentials in **Settings → Models** |

First-run WebUI setup binds to `127.0.0.1` by default. Use manual configuration and a WebUI password before exposing the WebSocket channel beyond localhost.

`--dev` is a foreground source-checkout workflow and cannot be combined with `--detach`. It installs frontend dependencies when `webui/node_modules` is missing, proxies to the configured WebSocket channel port, and stops Vite when the launcher exits. The shared on-demand gateway stops only when no other interactive client still holds it. Installer-managed normal WebUI launches and explicit `--detach` use the gateway's persistent lifecycle; manage that same instance with the `gateway` commands below. The old `webui --background` spelling remains deprecated and prints migration guidance.

## Gateway

`nanobot gateway` starts enabled chat channels, WebUI/WebSocket when configured, cron-backed system jobs, Dream, heartbeat, and the health endpoint. Most local browser users should start with `nanobot webui`; use `gateway` directly for service management, chat app operation, and advanced deployment. By default it runs in the foreground, which keeps existing scripts and terminal workflows unchanged. Use `--background` when you want a local macOS, Linux, or Windows process that you can manage from the CLI.

| Command | Description |
|---|---|
| `nanobot gateway` | Start the gateway in the foreground with config defaults |
| `nanobot gateway --verbose` | Show verbose runtime output |
| `nanobot gateway --port <port>` | Override `gateway.port` for the health endpoint |
| `nanobot gateway --workspace <path>` | Override workspace |
| `nanobot gateway --config <path>` | Use a specific config file |
| `nanobot gateway --background` | Start the gateway as a background process |
| `nanobot gateway status` | Show PID, foreground/background launch mode, explicit/on-demand lifetime, live client count, state, and logs |
| `nanobot gateway logs --no-follow` | Print recent background gateway logs and exit |
| `nanobot gateway logs` | Follow background gateway logs |
| `nanobot gateway restart` | Restart the recorded background gateway with the current config |
| `nanobot gateway stop` | Stop the recorded background gateway |
| `nanobot gateway install-service` | Install a systemd user service or macOS LaunchAgent |
| `nanobot gateway install-service --dry-run` | Preview the generated service file and system commands |
| `nanobot gateway uninstall-service` | Remove the installed system service |

On Windows, `gateway stop` waits up to `--timeout` seconds (default: 20) for the gateway to stop normally. If a forced stop is needed, the command displays a warning. Forced stops can interrupt active work.

For custom instances, pass the same selector flags after the management subcommand, as shown below. `--config` and `--workspace` before a management subcommand are rejected with a usage error; they are not inherited.

```bash
nanobot gateway --background --config ./bot-a/config.json --workspace ./bot-a/workspace
nanobot gateway status --config ./bot-a/config.json --workspace ./bot-a/workspace
nanobot gateway stop --config ./bot-a/config.json --workspace ./bot-a/workspace
nanobot gateway install-service --config ./bot-a/config.json --workspace ./bot-a/workspace --name bot-a
```

`--background` is a lightweight detached process. `install-service` is for login/startup integration: Linux uses a systemd user service; macOS uses a LaunchAgent plist. System services run the foreground gateway under the OS supervisor rather than nesting another background process.

Default health endpoint:

```text
http://127.0.0.1:18790/health
```

The bundled WebUI is served by the WebSocket channel, usually on port `8765`, not by the gateway health endpoint.

## Local Triggers

`nanobot trigger` delivers one local message to a trigger that was created from a chat/session with `/trigger <name>`.

```bash
nanobot trigger trg_8K4P2Q9X "Review PR #4502"
```

Keep `nanobot gateway` running so the message can be delivered to the linked chat/session. The message is recorded as an automation turn in that session, not as a normal chat message typed by the user.

The command writes to a workspace-local durable queue. If `nanobot gateway` is not running yet, the message waits in that workspace. If the target session is already running a turn, the trigger waits for that session to become idle. If the gateway exits after claiming a delivery but before the linked turn completes, the next gateway start requeues that delivery. The queue is at-least-once, not exactly-once, so the same message can be delivered again after an interrupted process. If the agent receives the delivery and the turn fails, the delivery is marked failed instead of retried indefinitely. Each delivery also writes an audit record under `<workspace>/triggers/runs`. Run one gateway consumer per workspace; this local queue is not a distributed multi-consumer queue.

Use stdin when another local process generates the message:

```bash
generate-report | nanobot trigger trg_8K4P2Q9X
```

Options:

| Command | Description |
|---|---|
| `nanobot trigger <id> "message"` | Deliver one message through a trigger |
| `nanobot trigger <id>` | Read the message from stdin |
| `nanobot trigger --config <path> <id> "message"` | Use the workspace from a specific config |
| `nanobot trigger --workspace <path> <id> "message"` | Use a specific workspace |

Triggers are managed in the WebUI Automations view instead of through separate `list`, `revoke`, or `delete` CLI subcommands. From there you can pause/resume, rename, delete, search, and copy the command for each trigger.

For webhooks or other external systems, run your own small service and have it call this CLI after it decides what message Sentinel should receive.

See [Automations](./automations.md) for the broader automation model, WebUI management, and delivery behavior.

## Status

```bash
nanobot status
```

Shows the config path, workspace path, active model, and provider summary without calling a model.

| Command | Description |
|---|---|
| `nanobot status` | Inspect the default instance |
| `nanobot status --config <path>` | Inspect a specific config |
| `nanobot status --config <path> --workspace <path>` | Inspect a specific config with a workspace override |

## Channels

| Command | Description |
|---|---|
| `nanobot channels status` | Show whether Discord is configured and enabled |
| `nanobot channels status --config <path>` | Show Discord status for a specific config |
| `nanobot plugins list --config <path>` | Show plugin/channel enabled state for a specific config |

See [`chat-apps.md`](./chat-apps.md) for Discord setup.

## Optional Features

Use these commands when you want Sentinel to add or remove a built-in capability without hand-editing JSON. Enabling may install the support package first. Disabling Discord keeps its saved settings and turns the channel off.

The `plugins` command name is retained for compatibility, but these entries are Sentinel runtime support packages, not the user-invokable tools shown in WebUI Apps. They cannot be attached to a chat turn with `@`.

| Feature name | What it enables |
|---|---|
| `azure` | Azure identity support for Azure-hosted models |
| `bedrock` | AWS Bedrock model provider support |
| `langfuse` | Langfuse tracing support for OpenAI-compatible providers and the Codex OAuth provider |
| `olostep` | Olostep web search provider support |
| `discord` | The Discord connector package and saved channel enablement |

| Command | Description |
|---|---|
| `nanobot plugins list` | Show available channels and optional capabilities |
| `nanobot plugins enable <name>` | Install missing support and enable the feature or channel |
| `nanobot plugins enable <name> --logs` | Show package install logs while enabling |
| `nanobot plugins disable <channel>` | Turn off a channel without deleting its saved settings |
| `nanobot plugins list --config <path>` | Read a specific config file |
| `nanobot plugins enable <name> --config <path>` | Update a specific config file |
| `nanobot plugins disable <channel> --config <path>` | Turn off a channel in a specific config file |

Document and PDF reading are included in the standard installation. The old `nanobot plugins enable documents` and `nanobot plugins enable pdf` commands remain accepted as no-op compatibility aliases.

## Provider OAuth

| Command | Description |
|---|---|
| `nanobot provider login openai-codex --set-main` | Authenticate Codex and select its current default model |
| `nanobot provider login xai-grok --set-main` | Authenticate an eligible X Premium / Grok subscription and select Grok 4.6; hosted X Search is enabled for models that advertise support |
| `nanobot provider login github-copilot --set-main` | Authenticate GitHub Copilot and select its current default model |
| `nanobot provider logout openai-codex` | Remove OpenAI Codex OAuth state |
| `nanobot provider logout xai-grok --config <path>` | Remove the selected Sentinel instance's xAI OAuth state |
| `nanobot provider logout github-copilot` | Remove GitHub Copilot OAuth state |

See [`providers.md`](./providers.md#oauth-providers) for when OAuth providers need explicit provider/model selection.

## Useful First Checks

```bash
nanobot --version
nanobot status
nanobot agent -m "Hello!"
```

If these fail, use [`troubleshooting.md`](./troubleshooting.md) before debugging WebUI, chat apps, Docker, systemd, or SDK integrations.
