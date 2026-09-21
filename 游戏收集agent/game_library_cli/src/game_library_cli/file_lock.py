"""Small cross-process advisory locks for local library files."""

from __future__ import annotations

import os
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

if os.name == "nt":  # pragma: no cover - exercised only on Windows
    import msvcrt
else:  # pragma: no cover - the POSIX branch is covered on macOS/Linux
    import fcntl


class LockTimeoutError(TimeoutError):
    """Raised when a file lock cannot be acquired within the timeout."""


@contextmanager
def file_lock(target: str | Path, timeout: float = 30.0) -> Iterator[None]:
    """Hold an exclusive lock for the lifetime of a read-modify-write transaction.

    The lock lives in a sidecar file because the CSV itself is atomically replaced
    after each write. The sidecar must not be removed after unlocking: another
    process may already be waiting on that inode.
    """

    target_path = Path(target)
    lock_path = target_path.with_name(f"{target_path.name}.lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + timeout

    with lock_path.open("a+b") as lock_file:
        while True:
            try:
                lock_file.seek(0)
                if os.name == "nt":  # pragma: no cover - exercised only on Windows
                    msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except (BlockingIOError, OSError) as exc:
                if time.monotonic() >= deadline:
                    raise LockTimeoutError(
                        f"Timed out waiting for lock {lock_path}"
                    ) from exc
                time.sleep(0.05)

        try:
            yield
        finally:
            if os.name == "nt":  # pragma: no cover - exercised only on Windows
                lock_file.seek(0)
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
