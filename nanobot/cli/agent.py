import asyncio
import importlib
from collections.abc import Awaitable, Callable
from typing import Any

import typer

from nanobot.cli.log_control import _set_nanobot_logs
from nanobot.cli.runtime_config import (
    _load_runtime_config,
    _migrate_cron_store,
    _print_agent_start_error,
)
from nanobot.config.schema import Config

_AGENT_DEPENDENCIES = {
    "AgentLoop": ("nanobot.agent.loop", "AgentLoop"),
    "StreamRenderer": ("nanobot.cli.stream", "StreamRenderer"),
    "consume_restart_notice_from_env": (
        "nanobot.utils.restart",
        "consume_restart_notice_from_env",
    ),
    "is_default_workspace": ("nanobot.config.paths", "is_default_workspace"),
    "sync_workspace_templates": ("nanobot.utils.helpers", "sync_workspace_templates"),
}


def __getattr__(name: str) -> Any:
    dependency = _AGENT_DEPENDENCIES.get(name)
    if dependency is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attribute = dependency
    value = getattr(importlib.import_module(module_name), attribute)
    globals()[name] = value
    return value


def _agent_dependency(name: str) -> Any:
    if name in globals():
        return globals()[name]
    return __getattr__(name)


def agent(
    message: str | None = typer.Option(None, "--message", "-m", help="Message to send to the agent"),
    session_id: str | None = typer.Option(None, "--session", "-s", help="Session ID"),
    workspace: str | None = typer.Option(None, "--workspace", "-w", help="Workspace directory"),
    config: str | None = typer.Option(None, "--config", "-c", help="Path to config file"),
    markdown: bool = typer.Option(
        True,
        "--markdown/--no-markdown",
        help="Render assistant output as Markdown",
    ),
    logs: bool = typer.Option(
        False,
        "--logs/--no-logs",
        help="Show nanobot runtime logs during the request",
    ),
) -> None:
    """Send a one-shot message to the agent."""
    if message is None:
        raise typer.BadParameter("provide a message with --message/-m; interactive chat is unavailable")

    runtime_config = _load_runtime_config(config, workspace)
    from nanobot.config.home import get_home_path
    from nanobot.config.loader import get_config_path
    from nanobot.config.paths import get_data_dir
    from nanobot.data_access import data_access, profile_data_paths

    paths = profile_data_paths(
        home=get_home_path(),
        data_dir=get_data_dir(),
        config=get_config_path(),
        workspace=runtime_config.workspace_path,
    )
    with data_access(paths):
        _run_one_shot(
            runtime_config,
            message=message,
            session_id=session_id,
            markdown=markdown,
            logs=logs,
        )


def _run_one_shot(
    runtime_config: Config,
    *,
    message: str,
    session_id: str | None,
    markdown: bool,
    logs: bool,
) -> None:
    from nanobot.agent.hooks import create_file_edit_activity_hook
    from nanobot.agent.tools.image_generation import register_image_generation_tool
    from nanobot.agent.tools.mcp import MCPProvider
    from nanobot.agent.tools.registry import ToolRegistry
    from nanobot.bus.queue import MessageBus
    from nanobot.cli import terminal as cli_terminal
    from nanobot.cron.service import CronService
    from nanobot.providers.factory import make_provider
    from nanobot.utils.restart import (
        format_restart_completed_message,
        should_show_cli_restart_notice,
    )
    from nanobot.utils.tool_hints import format_tool_event_hints

    agent_loop_class = _agent_dependency("AgentLoop")
    stream_renderer_class = _agent_dependency("StreamRenderer")
    consume_restart_notice_from_env = _agent_dependency("consume_restart_notice_from_env")
    is_default_workspace = _agent_dependency("is_default_workspace")
    sync_workspace_templates = _agent_dependency("sync_workspace_templates")

    session_id = session_id or "cli:direct"

    try:
        provider = make_provider(runtime_config)
    except ValueError as exc:
        _print_agent_start_error(exc)
        raise typer.Exit(1) from exc

    sync_workspace_templates(runtime_config.workspace_path)
    bus = MessageBus()
    if is_default_workspace(runtime_config.workspace_path):
        _migrate_cron_store(runtime_config)

    cron_store_path = runtime_config.workspace_path / "cron" / "jobs.json"
    cron = CronService(cron_store_path)
    tools = ToolRegistry()
    register_image_generation_tool(runtime_config, tools, workspace=runtime_config.workspace_path)
    mcp_provider = MCPProvider.from_config(runtime_config, tools)
    _set_nanobot_logs(logs)

    from nanobot.goal.assembly import install_goal

    try:
        agent_loop = agent_loop_class.from_config(
            runtime_config,
            bus,
            provider=provider,
            cron_service=cron,
            hook_factories=[create_file_edit_activity_hook],
            tool_registry=tools,
            builtin_assembly=install_goal,
        )
    except ValueError as exc:
        _print_agent_start_error(exc)
        raise typer.Exit(1) from exc

    restart_notice = consume_restart_notice_from_env()
    if restart_notice and should_show_cli_restart_notice(restart_notice, session_id):
        cli_terminal._print_agent_response(
            format_restart_completed_message(restart_notice.started_at_raw),
            render_markdown=False,
        )

    async def close_runtime() -> None:
        try:
            await agent_loop.aclose()
        finally:
            await mcp_provider.aclose()

    def make_progress(renderer: Any) -> Callable[..., Awaitable[None]]:
        reasoning_buffer = cli_terminal._ReasoningBuffer()

        async def cli_progress(
            content: str,
            *,
            tool_hint: bool = False,
            tool_events: list[dict[str, Any]] | None = None,
            reasoning: bool = False,
            **kwargs: Any,
        ) -> None:
            channels_config = agent_loop.channels_config
            if kwargs.get("reasoning_end"):
                if channels_config and not channels_config.show_reasoning:
                    reasoning_buffer.clear()
                else:
                    cli_terminal._flush_cli_reasoning(reasoning_buffer, None, renderer)
                return
            if reasoning:
                if channels_config and not channels_config.show_reasoning:
                    reasoning_buffer.clear()
                    return
                text = reasoning_buffer.add(content)
                if text:
                    cli_terminal._print_cli_reasoning(text, None, renderer)
                return
            if channels_config and tool_hint and not channels_config.send_tool_hints:
                return
            if channels_config and not tool_hint and not channels_config.send_progress:
                return
            if tool_hint and tool_events:
                content = format_tool_event_hints(
                    tool_events,
                    max_length=runtime_config.agents.defaults.tool_hint_max_length,
                )
            cli_terminal._print_cli_progress_line(content, None, renderer)

        return cli_progress

    async def run_once() -> None:
        try:
            await mcp_provider.connect()
            renderer = stream_renderer_class(
                render_markdown=markdown,
                bot_name=runtime_config.agents.defaults.bot_name,
                bot_icon=runtime_config.agents.defaults.bot_icon,
            )
            response = await agent_loop.process_direct(
                message,
                session_id,
                on_progress=make_progress(renderer),
                on_stream=renderer.on_delta,
                on_stream_end=renderer.on_end,
            )
            if not renderer.streamed:
                await renderer.close()
                print_kwargs: dict[str, Any] = {}
                if renderer.header_printed:
                    print_kwargs["show_header"] = False
                cli_terminal._print_agent_response(
                    response.content if response else "",
                    render_markdown=markdown,
                    metadata=response.metadata if response else None,
                    **print_kwargs,
                )
        finally:
            await close_runtime()

    asyncio.run(run_once())
