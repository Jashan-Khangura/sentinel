from __future__ import annotations

import os
import sys
from typing import Final

_ROLES: Final = {"agent", "gateway", "webui"}


def _set_process_title(title: str) -> None:
    if sys.platform == "linux":
        os.environ.setdefault("SPT_NOENV", "1")
    from setproctitle import setproctitle

    setproctitle(title)


def set_cli_process_identity(args: list[str]) -> None:
    """Name this CLI process after the nanobot role it is running."""
    if os.name == "nt":
        # Windows process managers use the console launcher's executable name,
        # which packaging already generates as ``nanobot.exe``.
        return
    role = args[0] if args and args[0] in _ROLES else None
    _set_process_title(f"nanobot-{role}" if role else "nanobot")
