from __future__ import annotations

import os
import sys
from contextlib import nullcontext, suppress
from typing import Any

from loguru import logger
from prompt_toolkit.history import FileHistory
from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text

from nanobot import __logo__
from nanobot.cli.stream import StreamRenderer, ThinkingSpinner
from nanobot.utils.helpers import sanitize_surrogates as _sanitize_surrogates

__all__ = [
    "_ReasoningBuffer",
    "_ensure_interactive_tty_mode",
    "_flush_cli_reasoning",
    "_print_agent_response",
    "_print_cli_progress_line",
    "_print_cli_reasoning",
    "_sanitize_surrogates",
    "SafeFileHistory",
]

console = Console()
_REASONING_SENTENCE_ENDINGS = (".", "!", "?", "。", "！", "？")
_REASONING_FLUSH_CHARS = 60


def _ensure_interactive_tty_mode() -> None:
    """Restore interactive line input after a raw-mode TTY leak."""
    try:
        fd = sys.stdin.fileno()
        if not os.isatty(fd):
            return
    except Exception:
        return

    with suppress(Exception):
        import termios

        attrs = termios.tcgetattr(fd)
        required_lflag = termios.ISIG | termios.ICANON | termios.ECHO
        blocked_input_flags = getattr(termios, "IGNCR", 0) | getattr(termios, "INLCR", 0)
        if (
            (attrs[3] & required_lflag) == required_lflag
            and attrs[0] & termios.ICRNL
            and not attrs[0] & blocked_input_flags
        ):
            return
        attrs[0] = (attrs[0] | termios.ICRNL) & ~blocked_input_flags
        attrs[3] |= required_lflag
        termios.tcsetattr(fd, termios.TCSANOW, attrs)
        termios.tcflush(fd, termios.TCIFLUSH)
        logger.debug("Restored foreground gateway TTY mode")


class SafeFileHistory(FileHistory):
    """Sanitize surrogate characters before writing CLI input history."""

    def store_string(self, string: str) -> None:
        super().store_string(_sanitize_surrogates(string))


def _make_console() -> Console:
    return Console(file=sys.stdout)


def _print_agent_response(
    response: str,
    render_markdown: bool,
    metadata: dict[str, Any] | None = None,
    show_header: bool = True,
) -> None:
    output = _make_console()
    body = _response_renderable(response or "", render_markdown, metadata)
    if show_header:
        output.print()
        output.print(f"[cyan]{__logo__} nanobot[/cyan]")
    output.print(body)
    output.print()


def _response_renderable(
    content: str, render_markdown: bool, metadata: dict[str, Any] | None = None
) -> Text | Markdown:
    if not render_markdown or (metadata or {}).get("render_as") == "text":
        return Text(content)
    return Markdown(content)


def _print_cli_progress_line(
    text: str,
    thinking: ThinkingSpinner | None,
    renderer: StreamRenderer | None = None,
) -> None:
    if not text.strip():
        return
    target = renderer.console if renderer else console
    pause = renderer.pause_spinner() if renderer else (thinking.pause() if thinking else nullcontext())
    with pause:
        if renderer:
            renderer.ensure_header()
        target.print(f"  [dim]↳ {text}[/dim]")


class _ReasoningBuffer:
    def __init__(self) -> None:
        self._text = ""

    def add(self, text: str) -> str | None:
        if not text:
            return None
        self._text += text
        if self._should_flush(text):
            return self.flush()
        return None

    def flush(self) -> str | None:
        text = self._text.strip()
        self._text = ""
        return text or None

    def clear(self) -> None:
        self._text = ""

    def _should_flush(self, text: str) -> bool:
        stripped = text.rstrip()
        return (
            "\n" in text
            or stripped.endswith(_REASONING_SENTENCE_ENDINGS)
            or len(self._text) >= _REASONING_FLUSH_CHARS
        )


def _print_cli_reasoning(
    text: str,
    thinking: ThinkingSpinner | None,
    renderer: StreamRenderer | None = None,
) -> None:
    if not text.strip():
        return
    target = renderer.console if renderer else console
    pause = renderer.pause_spinner() if renderer else (thinking.pause() if thinking else nullcontext())
    with pause:
        if renderer:
            renderer.ensure_header()
        target.print(f"[dim italic]✻ {text}[/dim italic]")


def _flush_cli_reasoning(
    reasoning_buffer: _ReasoningBuffer,
    thinking: ThinkingSpinner | None,
    renderer: StreamRenderer | None = None,
) -> None:
    text = reasoning_buffer.flush()
    if text:
        _print_cli_reasoning(text, thinking, renderer)
