# Sentinel

**Sentinel** is an ultra-lightweight, open-source, self-hosted personal AI agent framework written in Python. Use it in a browser or Discord to work with files, remember preferences, and schedule tasks. Connect a supported model provider or local model server to supply the AI.

This is a documentation and branding rename only: the Python package is still `nanobot-ai`, the command is still `nanobot`, data still defaults to `~/.nanobot`, and installation/release links still point to upstream nanobot. Do not treat those links as Sentinel releases.

## Start Here

| You want to... | Go to |
|---|---|
| Install Sentinel with no terminal/config background | [Start Without Technical Background](./docs/start-without-technical-background.md) |
| Install quickly and get your first reply | [Install](#-install) and [Quick Start](#-quick-start) |
| Open the bundled browser UI | [WebUI](#-webui) |
| Connect Discord | [Discord setup](./docs/guides/discord-ai-agent.md) |
| Configure providers, fallback models, Langfuse, MCP, web tools, or security | [Docs](./docs/README.md) and [Configuration](./docs/configuration.md) |
| Develop the browser UI | [Install current source](#-install), then [WebUI development](./webui/README.md) and [Development](./docs/development.md) |
| Integrate from Python | [Python SDK](./docs/python-sdk.md) |
| Understand or extend the internals | [Architecture](./docs/architecture.md), [Development](./docs/development.md), and [Provider extensions](./docs/development.md) |
| Deploy to the cloud or keep Sentinel running as a service | [Deployment](./docs/deployment.md) |

## What can Sentinel do?

Sentinel can:

- run in a browser WebUI or one-shot CLI mode
- connect to Discord
- read images, PDF, Word (`.docx`), Excel (`.xlsx`), and PowerPoint (`.pptx`) files with built-in file tools
- use shell, web search/fetch, MCP integrations, cron, image generation, and multi-agent delegation
- keep session history and use [Dream](./docs/memory.md#save-and-check-a-preference) to consolidate long-term memory
- run [long-horizon goals](./docs/guides/long-running-ai-agent.md) and [scheduled automations](./docs/automations.md)
- embed the agent with the Python SDK
- deploy as a long-running local or server-side agent gateway

## 💡 Why Sentinel

- **Persistent workflows**: keep saved conversations, long-term memory, and task results for later work.
- **Chat-native reach**: WebUI and Discord.
- **Model freedom**: OpenAI-compatible APIs, local LLMs, image generation, search, and fallbacks.
- **Small core**: readable internals with MCP, memory, deployment, and automation built in.
- **Own your stack**: inspect, customize, self-host, and extend without a giant platform.

## 📦 Install

You need **Python 3.11 or newer** and access to a [supported model provider or local model server](./docs/providers.md). Model fees or local hardware requirements depend on the service you choose; Sentinel does not supply a model account.

Choose the **stable release** for everyday use or **current source** for development and the latest features. This README describes current source; [published documentation](https://nanobot.wiki/docs/latest/getting-started/nanobot-overview) covers the released version.

New to terminals or model credentials? Follow [Start Without Technical Background](./docs/start-without-technical-background.md). For manual upgrades and data migration notes, see [Manual Updates and Data Migrations](./docs/updating.md).

| Track | Install with | Update with | What runs |
|---|---|---|---|
| Stable | installer, `uv`, or pip | original package tool or deployment workflow; see [manual update guidance](./docs/updating.md#installation-owners) | one released Python/WebUI version |
| Current source | editable Git checkout | `git pull --ff-only` + editable dependency sync | Python and WebUI from that checkout |

**Stable release: automatic setup (recommended)**

The installer chooses an isolated Python environment and opens setup for you. The two commands below are the same installation method for different operating systems; run only the one for your system.

<details>
<summary>macOS / Linux</summary>

```bash
curl -fsSL https://raw.githubusercontent.com/HKUDS/nanobot/main/scripts/install.sh | sh
```

</details>

<details>
<summary>Windows PowerShell</summary>

```powershell
irm https://raw.githubusercontent.com/HKUDS/nanobot/main/scripts/install.ps1 | iex
```

</details>

<details>
<summary>Installer details, preview, and script review</summary>

The default command installs or upgrades the stable PyPI release. Fresh installations use a dedicated environment under `~/.nanobot/venv`. On a fresh local desktop it opens the WebUI for model setup. That gateway keeps running after the browser or terminal closes; use the printed `gateway stop` command to stop it. SSH, headless, existing-config and older-release installs use terminal setup when an interactive terminal is available; otherwise the installer prints the command to run later.

The installer uses the detected installation method when safe, or stops for manual review. Check existing extras and constraints with the original package manager. An active venv remains an explicit target, not an installer-managed environment. The installer avoids system-wide pip and prints the command to reuse if `nanobot` is not on `PATH`.

To preview the plan without changing your environment, pass `--dry-run`.

```bash
curl -fsSL https://raw.githubusercontent.com/HKUDS/nanobot/main/scripts/install.sh | sh -s -- --dry-run
```

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/HKUDS/nanobot/main/scripts/install.ps1))) --dry-run
```

If you prefer to inspect the script first, open [`scripts/install.sh`](./scripts/install.sh) or [`scripts/install.ps1`](./scripts/install.ps1).

</details>

<details>
<summary>Already use uv or pip? Install the stable package yourself</summary>

Use this instead of the recommended installer when you already manage your own Python environment. These commands install the same stable `nanobot-ai` package; they do not launch setup.

**uv: isolated CLI installation**

```bash
uv tool install nanobot-ai
```

**pip: activate your virtual environment first**

```bash
python -m pip install nanobot-ai
```

Then run `nanobot webui` for browser setup, or `nanobot onboard --wizard` for guided terminal setup. For the [Python SDK](./docs/python-sdk.md), install `nanobot-ai` in your application's virtual environment so the application can import it; a separate `uv tool` environment does not make the SDK importable there.

If pip reports `externally-managed-environment`, use the recommended installer, `uv tool install nanobot-ai`, `pipx install nanobot-ai`, or an activated virtual environment. Upgrade with the same method; for uv use `uv tool upgrade nanobot-ai`, and for pip use `python -m pip install -U nanobot-ai`.

</details>

**Current source: development checkout**

<details>
<summary>Install current source with Git and Bun</summary>

Clone the repository and install it in editable mode. A source install requires Git and [Bun](https://bun.sh/) to build the WebUI assets.

```bash
git clone https://github.com/HKUDS/nanobot.git
cd nanobot
python3 -m venv .venv
```

On Windows, use `py -3 -m venv .venv` instead of `python3`. Activate it with `source .venv/bin/activate` on macOS/Linux or `.venv\Scripts\Activate.ps1` in Windows PowerShell, then run:

```bash
python -m pip install -e .
```

After that, `nanobot webui` prompts to rebuild stale frontend assets, or warns in non-interactive sessions; `--yes` builds automatically. `nanobot -m "Hello!"` runs a one-shot check, while operational commands remain available through the CLI. After stopping the old instance, `git pull --ff-only` updates the Python and WebUI source together; rerun `python -m pip install -e .` when Python dependencies change, then restart the instance. Contributors should also read [Development guide](./docs/development.md).

</details>

<details>
<summary>Supported platforms and release tracks</summary>

Published packages include the WebUI. Use the supported Python installation methods described above; source installs build WebUI assets from the checkout.

</details>

<details>
<summary>Verify the installation or locate the `nanobot` command</summary>

Verify the install:

```bash
nanobot --version
```

If `nanobot` is not on `PATH`, reuse the installer's printed command or run the Python executable from the existing installation with `-I -m nanobot`. For uv/pipx, locate that environment with the original manager. Do not use a temporary tool environment to manage an existing installation.

</details>

After installation, continue with [Quick Start](#-quick-start). Use the exact command printed by the installer if `nanobot` is not on `PATH`.

## 🚀 Quick Start

**Open Sentinel in your browser**

If the installer already opened the WebUI, continue there. Otherwise run:

```bash
nanobot webui
```

Keep the launcher terminal open while using the browser. It starts or joins the shared local gateway and binds the first-run WebUI to localhost. If the browser does not open, copy the complete login link printed in the terminal, including everything after `#`; keep this credential private. For SSH or a headless host, use the remote-browser or terminal-only instructions below.

**Your first three steps**

1. Open **Settings → Models** and save a provider/model preset with your credential or supported sign-in. See [model setup](./docs/quick-start.md#2-configure-your-model) if you need the full steps.
2. Start a new topic and send `Hello!` to verify the model connection.
3. To try file work, put a copy of `notes.txt` in a practice folder, select that folder and **Default Permission** (workspace-restricted access, not an OS sandbox), and ask: "Read notes.txt and write a short summary to summary.md." Open `summary.md` in that folder to check the result. See [Your first file task](./docs/start-without-technical-background.md#your-first-file-task).

A normal reply verifies the provider/model and browser connection. The file task separately checks the selected project and its file permissions. Attaching a file sends it to the conversation; it does not change the selected project folder.

Then describe your next goal in the same chat, for example: "I am already using the WebUI. Help me connect Discord and allow only my account." An enabled `nanobot-document` skill can consult the documentation bundled with your installation; see [Continue with Sentinel](./docs/quick-start.md#continue-with-sentinel) for examples, explicit invocation, and availability.

<details>
<summary>Open the WebUI on a remote server through SSH</summary>

After installing Sentinel on the server, start its WebUI without opening a server-side browser:

```bash
nanobot webui --no-open
```

Keep that server terminal running. In a second terminal on your own computer, forward the default WebUI port through SSH:

```bash
ssh -N -L 127.0.0.1:8765:127.0.0.1:8765 user@SERVER
```

Replace `user@SERVER` with your SSH login and leave the tunnel open. In your local browser, open the complete login link printed by the server launcher, preserving its `#` fragment. It uses `http://127.0.0.1:8765`, which now reaches the server through the tunnel. Complete **Settings → Models** and send `Hello!`. If local port `8765` is occupied, use another local port in the tunnel and change only the port in the browser link. Keep the server listener on localhost. For Docker, public endpoints, or service management, see [Deployment](./docs/deployment.md).

</details>

<details>
<summary>Terminal setup and one-shot checks</summary>

If a model is not configured yet, use the terminal wizard:

```bash
nanobot onboard --wizard
```

Check one reply without opening the browser:

```bash
nanobot -m "Hello!"
```

The CLI supports operational commands and one-shot agent execution; it does not provide an interactive terminal chat client. Use the [CLI reference](./docs/cli-reference.md) for session, workspace, and gateway options.

</details>

<details>
<summary>Save and check a preference</summary>

State a specific preference in your chat, for example: "For release notes, use concise bullet points." To consolidate it now, send `/compact` and then `/dream`, waiting for each to finish, and review `/dream-log`. Check the actual changes to `USER.md` or `memory/MEMORY.md` in the configured agent workspace, then test reuse in a new topic in the same instance. Dream may decide that no durable change is needed; a conversational acknowledgement alone does not prove the preference was saved. See [Save and Check a Preference](./docs/memory.md#save-and-check-a-preference) for file access, correction, and restoration steps.

</details>

<details>
<summary>Start and stop a sustained goal</summary>

Use a regular topic for a bounded objective with a clear completion condition, for example:

```text
/goal Review this project's tests and list the smallest missing test case.
```

An active goal keeps Sentinel working beyond the ordinary iteration limit until it records completion, cancellation, or a blocked state. This can use more model tokens; `/stop` interrupts the current work, while asking Sentinel to cancel the goal abandons the objective. Execution errors can also stop the work. A scheduled automation instead starts work at specified times. Keep the gateway running for unattended work using the background or service options below.

After a gateway restart, reopen the original topic and review saved results before explicitly continuing any interrupted work. Recovery does not blindly replay uncertain tool actions. See the [long-running agent guide](./docs/guides/long-running-ai-agent.md) for starting conditions and related automation options.

</details>

<details>
<summary>Keep the gateway running after closing interactive clients</summary>

After model setup, keep channels and automations running when interactive launchers close:

```bash
nanobot gateway --background
```

This starts or promotes the shared gateway to persistent background mode. Fresh official-installer environments already use that lifetime when you open `nanobot webui`; other Python installations can explicitly use `nanobot webui --detach`. Channels and automations remain active after local clients exit. Complete first-time model setup in the WebUI, and use the gateway commands below to manage the same instance.

Background mode does not configure startup after a machine reboot or restart after a crash; use an [OS-managed service](./docs/deployment.md#switch-an-existing-gateway-to-a-service) for that. Interrupted subagent tasks are not automatically relaunched after a restart, and missed scheduled times are not replayed; see [subagent recovery](./docs/concepts.md#subagents) and [automation delivery](./docs/automations.md#delivery-and-reliability).

Manage the background gateway with:

```bash
nanobot gateway status
nanobot gateway logs
nanobot gateway restart
nanobot gateway stop
```

To reopen the browser, run `nanobot webui` against the same instance and use its complete printed login link.

</details>

<details>
<summary>Run a configured gateway directly</summary>

Use this once a model is configured and you want to run the gateway directly in the current terminal:

```bash
nanobot gateway
```

It skips guided WebUI setup and browser opening. The WebUI remains available when its channel is configured. Use `nanobot gateway --background` for a detached process, or follow [Deployment](./docs/deployment.md) for startup and supervision by the operating system.

</details>

<details>
<summary>Read task guides or look up configuration details</summary>

- Model/provider recipes: [Provider Cookbook](./docs/provider-cookbook.md) and [Providers and Models](./docs/providers.md).
- Local models: [Ollama](./docs/providers.md#ollama), [vLLM or another OpenAI-compatible server](./docs/providers.md#vllm-or-other-local-openai-compatible-server).
- Discord: [setup guide](./docs/guides/discord-ai-agent.md) and [channel reference](./docs/chat-apps.md).
- Exact settings for web search, MCP, voice, image generation, and security: [Configuration](./docs/configuration.md).
- Manual JSON and other setup paths: [Install and Quick Start](./docs/quick-start.md).
- Failures after setup: [Troubleshooting](./docs/troubleshooting.md).

</details>

## 🌐 WebUI

The WebUI ships **inside the published wheel** with no separate frontend build. It is the browser workbench for persistent topics, temporary chats, visible agent activity, workspace controls, Apps, Skills, Automations, and settings. Start it with `nanobot webui`. WebUI access grants administration of the same agent instance; share it only with trusted operators. See [Sharing access](./docs/webui.md#sharing-access).

Use it to:

- keep separate topics for different tasks and projects;
- fork a topic from an earlier reply, or use temporary chats outside saved history and memory;
- inspect reasoning, tool calls, file edits, diffs, command output, and generated artifacts;
- switch model presets and choose a project before starting a topic;
- attach images, documents, or video, and use voice input with a configured transcription provider;
- configure models in **Settings**, connect chat platforms in **Channels**, and manage Apps, Skills, and Automations.

Videos can be played in WebUI, but the agent cannot directly analyze their contents.

### Keep related work side by side

Group up to four conversations and arrange them in columns, rows, a grid, or a main pane with supporting panes. Each topic keeps its own history. Select another topic from the `@` menu, or drag it into the composer, to let the agent read its context and coordinate work across sessions.

Choose a project, access mode, and model for each task. Topics separate conversation history; project folders select where file work happens. Neither creates separate long-term memory: one instance shares its agent profile, memory, and skills across projects. Use [separate instances](./docs/multiple-instances.md) when client data or preferences must stay isolated. [Explore topics and panes →](./docs/webui.md#conversation-groups-and-panes)

### Inspect the work and its context

Expand agent activity to see reasoning, tool calls, and file changes. Switch **Settings → Appearance → Edit preview** to **Diff** for inline patches. The composer's context indicator shows the current context size, input tokens by round, and cache reuse when the provider reports it.

Context compaction also appears in the conversation timeline. [Explore activity and context →](./docs/webui.md#activity-and-context-usage)

### Bring your tools into the conversation

Use Apps to connect MCP servers, enable Agent Plugins, and manage local CLI App adapters. Add a preset or a custom server, then attach an available tool with `@`. Skills provide reusable instructions. **Settings** holds model, voice, image, and web setup; **Channels** handles chat-platform connections.

[Explore Apps →](./docs/webui.md#apps) · [Discover Skills →](./docs/webui.md#skills) · [Connect Discord →](./docs/guides/discord-ai-agent.md)

Before connecting a personal bot to Discord, check its DM pairing/allowlist and group-access policies; see the [channel reference](./docs/chat-apps.md).

### Let recurring work run on a schedule

Ask for an automation from the topic that should receive its results. Use **Tasks** to review and manage schedules, or **Calendar** to scan completed and upcoming runs by date. Local triggers let a script start a saved task on demand.

Keep the gateway running and the host awake for scheduled delivery. Missed scheduled times are not replayed after a gateway restart. See [delivery and recovery rules](./docs/automations.md#delivery-and-reliability). [Explore Automations →](./docs/automations.md)

For a conversation that should stay out of saved topic history and long-term memory, use [Temporary chat](./docs/webui.md#temporary-chats) from the header. Temporary chats end when the connection closes and use the default workspace with workspace-only permissions. Requests still go to the configured model provider, and files created by tools remain after the chat closes.

See the [WebUI guide](./docs/webui.md) for LAN access, background operation, workspace controls, and the full feature tour. Working on the frontend itself? Use [`webui/README.md`](./webui/README.md).

## Architecture

The Python gateway owns agent execution, sessions, tools, memory, and security policy for the WebUI and Discord. The clients share that runtime; the core agent loop builds context, calls the model, executes requested tools, and returns the result. Memory, skills, channels, and MCP integrations extend that loop.

The [Python SDK](./docs/python-sdk.md) embeds the agent runtime in your application process.

See [Architecture](./docs/architecture.md) for source ownership and extension points.

## Docs

Browse the [repo docs](./docs/README.md) for current source documentation, or visit [nanobot.wiki](https://nanobot.wiki/docs/latest/getting-started/nanobot-overview) for the stable release. The [task guide index](./docs/guides/README.md) groups walkthroughs by outcome.

- Get started: [Beginner walkthrough](./docs/start-without-technical-background.md) or [Install and Quick Start](./docs/quick-start.md).
- Choose and configure a model: [Providers and Models](./docs/providers.md) and [Provider Cookbook](./docs/provider-cookbook.md).
- Connect Discord: [setup guide](./docs/guides/discord-ai-agent.md) and [channel reference](./docs/chat-apps.md).
- Schedule or deploy work: [Automations](./docs/automations.md) and [Deployment](./docs/deployment.md).
- Integrate from code: [Python SDK](./docs/python-sdk.md).
- Look up runtime concepts or exact settings: [Concepts](./docs/concepts.md) and [Configuration](./docs/configuration.md).
- Diagnose a failure: [Troubleshooting](./docs/troubleshooting.md).
- Extend the core: [Architecture](./docs/architecture.md) and [development guide](./docs/development.md).
