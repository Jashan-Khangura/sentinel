"""Account-scoped leases for named nanobot stores shared by Python installations.

Runtimes share leases; installation maintenance requires exclusive access. Two
lease namespaces cover overlapping store roots in both directions. This coordinates
participating runtimes, not older versions, other accounts, external databases or
arbitrary project files. Each process must acquire its own lease; a parent's exit
must not unlock a pip child.
"""

from __future__ import annotations

import hashlib
import os
from collections.abc import Generator, Iterable
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass, field
from pathlib import Path

from nanobot.installation_lock import FileLease, InstallationBusyError, file_access

_DATA_STORES = (
    "sessions", "webui", "media", "auth", "pairing.json", "cron", "delivery",
    "llm_usage.sqlite3", "llm_usage.sqlite3-wal", "llm_usage.sqlite3-shm",
    "whatsapp-auth", "weixin", "matrix-store", "linear", "mochat", "cli-apps/installed.json",
)
_WORKSPACE_STORES = (
    ".nanobot", "memory", "skills", "sessions", "cron", "triggers",
    "AGENTS.md", "TOOLS.md", "SOUL.md", "USER.md", "HEARTBEAT.md",
)


@dataclass(frozen=True)
class DataLease:
    """Store leases remain owned by the enclosing data_access context."""

    roots: tuple[str, ...]
    exclusive: bool
    _files: tuple[FileLease, ...] = field(default=(), repr=False, compare=False)

    @contextmanager
    def inherit_for_exec(self) -> Generator[None]:
        """Retain all store leases in a dedicated POSIX installer's exec handoff."""
        with ExitStack() as stack:
            for lease in self._files:
                stack.enter_context(lease.inherit_for_exec())
            yield


def _canonical_roots(paths: Iterable[str | Path]) -> tuple[str, ...]:
    roots: set[str] = set()
    for raw in paths:
        path = Path(raw)
        if not path.is_absolute():
            raise ValueError("Data stores must use absolute paths")
        roots.add(str(path.resolve()).casefold())
    return tuple(sorted(roots))


def profile_data_paths(*, home: Path, data_dir: Path, config: Path, workspace: Path) -> tuple[Path, ...]:
    """Return stores that a profile runtime may read or write."""
    return tuple(path.absolute() for path in (
        config, home / "history" / "cli_history", home / "sessions",
        *(data_dir / name for name in _DATA_STORES),
        *(workspace / name for name in _WORKSPACE_STORES),
    ))


@contextmanager
def profile_data_access(*, home: Path, data_dir: Path, config: Path, workspace: Path) -> Generator[None]:
    """Lease all stores owned by a runtime profile."""
    with data_access(profile_data_paths(home=home, data_dir=data_dir, config=config, workspace=workspace)):
        yield


@contextmanager
def data_access(paths: Iterable[str | Path], *, updating: bool = False) -> Generator[DataLease]:
    """Refuse overlapping live writers or maintenance without waiting or killing them.

    Writers claim roots in one namespace and ancestors in the other; maintenance
    does the reverse, exclusively. Neither a parent nor a child store can bypass
    the other's lease. Disjoint runtime data stays available, while maintenance
    operations serialize across this account.
    """
    canonical = _canonical_roots(paths)
    roots = set(map(Path, canonical))
    leases: set[tuple[str, str]] = set()
    for path in roots:
        requested, ancestors = (path,), (path, *path.parents)
        for namespace, items in (
            ("writers", requested if updating else ancestors),
            ("maintenance", ancestors if updating else requested),
        ):
            for item in items:
                leases.add((namespace, str(item).casefold()))
    directory = Path.home() / ".nanobot" / "updates" / "data-locks"
    with ExitStack() as stack:
        held: list[FileLease] = []
        try:
            if updating:
                held.append(stack.enter_context(file_access(directory / "maintenance.lock", exclusive=True)))
            for namespace, key in sorted(leases):
                name = hashlib.sha256(os.fsencode(key)).hexdigest()
                held.append(stack.enter_context(file_access(directory / f"{namespace}-{name}.lock", exclusive=updating)))
        except BlockingIOError as exc:
            raise InstallationBusyError(
                "Nanobot data is in use by another runtime or installer. Stop its writers "
                "before retrying; no data lease was granted."
            ) from exc
        yield DataLease(canonical, updating, tuple(held))
