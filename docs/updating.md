# Manual Updates and Data Migrations

Nanobot does not install package updates or recover interrupted installations. Stop the gateway and other processes using the environment, back up configuration and data, and update through the tool that owns the installation. Do not switch package managers or overwrite a managed environment with pip. After updating, restart the same profile and verify the running version, configuration and conversations.

## Upgrade older JSONL installations

The 0.4.x releases retain automatic import of legacy model JSONL history, WebUI JSONL / segments and per-feature proxy settings. You can upgrade an older installation directly to 0.4.1 through its original installation method; an intermediate 0.4.0 installation is not required. These importers are scheduled for removal in 0.5.0.

1. Stop all writers and back up the complete instance, including the configuration directory and workspace.
2. Upgrade through the original installation method, preserving existing extras, constraints and installation ownership.
3. Start the updated instance with the same configuration and workspace selectors. Open existing conversations and verify both messages and displayed history. Check proxy settings and save the migrated shared-proxy configuration.
4. Verify the running version, a new message and another restart before considering the upgrade complete.

Keep the original backup and retained JSONL import backups. Do not delete or overwrite old data to resolve a missing-history problem. Complete and verify the migration on a 0.4.x release before upgrading to 0.5.0.

## Installation owners

Run package commands **on the gateway computer, as the original installation account**. For containers, use the deployment host rather than treating a container path as a host path.

| Installation | Update route |
| --- | --- |
| Installer-managed environment | Use the same installer and preserve its existing configuration and data. |
| uv registry tool | Run `uv tool upgrade nanobot-ai` in its original environment. Preserve existing extras, constraints and additional packages. |
| pipx | Run `pipx upgrade nanobot-ai` with the original package requirement and options. Preserve injected packages and custom indexes. |
| Ordinary pip venv | Use that environment's Python with `-m pip install --upgrade 'nanobot-ai[<your existing extras>]'`; omit brackets for the base package. Do not guess optional extras. |
| Source checkout | Preserve local changes, update the selected ref and environment, and follow the [development instructions](./development.md). |
| Docker / Compose | Pull or build the selected image and recreate the service with its existing data volumes. Do not pip-install into a running container. |
| OS package, service manager or Desktop | Use the distributor or deployment's package and launcher workflow. |

After the package operation, restart the same profiles through their original launcher. New versions may migrate stored data. Verify the **running** version in **About** and check that configuration and conversations remain available. Package-manager success alone does not verify the gateway.

## Standalone API service removal

`nanobot serve` and its OpenAI-compatible `/v1` endpoints have been removed. This also removes the API server controls in Settings and the `nanobot-api` Compose service. The Gateway, WebUI, Python SDK, and OpenAI-compatible model connections are separate and still supported. The Python SDK embeds Sentinel in a Python application; it is not an HTTP-compatible replacement. The `api` install extra is now empty so upgrades can preserve an existing installation's recorded extras. New installations do not need it.

Before updating, stop any existing standalone API process through the launcher that started it. For a process started from Settings, use **Settings → System → Stop** in the old version. For Compose, use `docker compose stop nanobot-api` and `docker compose rm -f nanobot-api` with the old Compose file before switching to the new file. If you already switched, confirm which container belongs to your deployment and stop that old container explicitly; removing a service from the Compose file does not stop an existing container. Keep your bind mounts and volumes.

Back up the configuration and data before updating. The old top-level `api` block is ignored on read and is omitted the next time Sentinel saves the configuration. Session data and workspaces are not deleted or moved. If you must roll back, use the previous version and its matching deployment files, and recover the old service settings from your backup if necessary. Do not overwrite current configuration or conversations with a stale backup.

To read old API conversations after updating, open the same configuration and workspace with [the Python SDK](./python-sdk.md#botsessions). Use `await bot.sessions.list()` to find keys such as `api:default` and `api:<session_id>`, then use `await bot.sessions.get(key)` to read their messages. If the old launcher used a separate API workspace, pass that workspace to `Nanobot.from_config(config_path, workspace=workspace)` instead of using the Gateway's workspace.

## Shared sessions removal

The shared sessions feature has been removed. The old `agents.defaults.unifiedSession` or `unified_session` setting is ignored.

Session and task recovery remain separate runtime features; this guide covers package installation only.
