import os
import subprocess
import sys
import time
from pathlib import Path

from game_library_cli.file_lock import file_lock


def test_file_lock_serializes_processes(tmp_path: Path):
    target = tmp_path / "games.csv"
    source_root = Path(__file__).parents[1] / "src"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(source_root) + os.pathsep + env.get("PYTHONPATH", "")
    script = """
import sys
import time
from game_library_cli.file_lock import file_lock

with file_lock(sys.argv[1]):
    print("locked", flush=True)
    time.sleep(0.35)
"""
    holder = subprocess.Popen(
        [sys.executable, "-c", script, str(target)],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert holder.stdout is not None
    assert holder.stdout.readline().strip() == "locked"

    started = time.monotonic()
    with file_lock(target, timeout=2.0):
        waited = time.monotonic() - started

    stdout, stderr = holder.communicate(timeout=3)
    assert holder.returncode == 0, stderr
    assert stdout == ""
    assert waited >= 0.25
