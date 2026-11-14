from __future__ import annotations

import os
import sys
from contextlib import suppress

from nanobot.cli.process_identity import set_cli_process_identity
from nanobot.installation_lock import InstallationBusyError, installation_access

_ROOT_OPTIONS = frozenset(
    {
        "-h",
        "--help",
        "-v",
        "--version",
        "--install-completion",
        "--show-completion",
        "--home",
    }
)


def _agent_invocation_args(args: list[str]) -> list[str] | None:
    if not args:
        return []
    if args[0] == "agent":
        return args[1:]
    if args[0].startswith("-") and args[0].split("=", 1)[0] not in _ROOT_OPTIONS:
        return args
    return None


def configure_windows_console() -> None:
    """Keep multilingual output usable for CLI and protected gateway startup."""
    if sys.platform != "win32" or sys.stdout.encoding == "utf-8":
        return
    os.environ["PYTHONIOENCODING"] = "utf-8"
    with suppress(Exception):
        for stream in (sys.stdout, sys.stderr):
            reconfigure = getattr(stream, "reconfigure", None)
            if callable(reconfigure):
                reconfigure(encoding="utf-8", errors="replace")


def _run_agent(args: list[str], *, prog_name: str) -> None:
    from nanobot.utils.log_config import configure_console_logging

    configure_console_logging(sys.stderr)
    import typer

    from nanobot.cli.agent import agent

    agent_app = typer.Typer(add_completion=False)
    agent_app.command()(agent)
    command = typer.main.get_command(agent_app)
    command.main(args=args, prog_name=prog_name)


def main() -> None:
    """Acquire a runtime lease before loading application code."""
    try:
        with installation_access():
            _dispatch()
    except InstallationBusyError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc


def _dispatch() -> None:
    from nanobot.utils.rotating_output import configure_background_output_from_env

    configure_background_output_from_env()
    raw_args = sys.argv[1:]
    # Installed completion scripts call ``nanobot`` without positional arguments
    # and pass the request through this environment variable. Keep those requests
    # on the root command so subcommands remain discoverable.
    shell_completion = bool(os.environ.get("_NANOBOT_COMPLETE"))
    agent_args = None if shell_completion else _agent_invocation_args(raw_args)
    dispatch_args = ["agent", *agent_args] if agent_args is not None else raw_args
    set_cli_process_identity(dispatch_args)
    configure_windows_console()
    root_agent_alias = bool(raw_args) and agent_args is not None and raw_args[:1] != ["agent"]
    if agent_args is not None and root_agent_alias:
        prog_name = "nanobot" if root_agent_alias else "nanobot agent"
        _run_agent(agent_args, prog_name=prog_name)
        return

    from nanobot.cli.commands import app

    app()
