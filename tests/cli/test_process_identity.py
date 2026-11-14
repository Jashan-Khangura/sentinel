from __future__ import annotations

import os
import sys
import types

import pytest
from typer.testing import CliRunner

from nanobot.cli.commands import app
from nanobot.cli.process_identity import (
    _set_process_title,
    set_cli_process_identity,
)


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        (["agent"], "nanobot-agent"),
        (["gateway", "--background"], "nanobot-gateway"),
        (["webui"], "nanobot-webui"),
        (["status"], "nanobot"),
        ([], "nanobot"),
    ],
)
def test_cli_process_identity_uses_product_and_role(
    monkeypatch: pytest.MonkeyPatch,
    args: list[str],
    expected: str,
) -> None:
    titles: list[str] = []
    monkeypatch.setattr("nanobot.cli.process_identity.os.name", "posix")
    monkeypatch.setattr("nanobot.cli.process_identity._set_process_title", titles.append)

    set_cli_process_identity(args)

    assert titles == [expected]


def test_cli_process_identity_keeps_windows_launcher_name(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    titles: list[str] = []
    monkeypatch.setattr("nanobot.cli.process_identity.os.name", "nt")
    monkeypatch.setattr("nanobot.cli.process_identity._set_process_title", titles.append)

    set_cli_process_identity(["agent"])

    assert titles == []


@pytest.mark.parametrize(("platform", "noenv"), [("linux", "1"), ("darwin", None)])
def test_process_title_keeps_environment_only_on_linux(
    monkeypatch: pytest.MonkeyPatch,
    platform: str,
    noenv: str | None,
) -> None:
    titles: list[str] = []
    monkeypatch.setattr("nanobot.cli.process_identity.sys.platform", platform)
    monkeypatch.delenv("SPT_NOENV", raising=False)
    monkeypatch.setitem(
        sys.modules, "setproctitle", types.SimpleNamespace(setproctitle=titles.append)
    )

    _set_process_title("nanobot-agent")

    assert os.environ.get("SPT_NOENV") == noenv
    assert titles == ["nanobot-agent"]


def test_legacy_console_entrypoint_still_sets_subcommand_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    commands: list[list[str]] = []
    monkeypatch.setattr("nanobot.cli.commands.set_cli_process_identity", commands.append)

    result = CliRunner().invoke(app, ["webui", "--help"])

    assert result.exit_code == 0
    assert commands == [["webui"]]


def test_legacy_console_entrypoint_routes_bare_command_to_agent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    identities: list[list[str]] = []
    launches: list[tuple[list[str], str]] = []
    monkeypatch.setattr("nanobot.cli.commands.set_cli_process_identity", identities.append)
    monkeypatch.setattr(
        "nanobot.cli.entry._run_agent",
        lambda args, *, prog_name: launches.append((args, prog_name)),
    )

    result = CliRunner().invoke(app, [])

    assert result.exit_code == 0
    assert identities == [["agent"]]
    assert launches == [([], "nanobot")]
