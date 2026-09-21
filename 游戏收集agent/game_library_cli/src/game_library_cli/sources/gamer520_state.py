import json
import os
import tempfile
from datetime import date
from pathlib import Path
from typing import Any

from ..normalize import extract_link_id

PLATFORMS = ("PC", "Switch")


def bootstrap_state(rows: list[dict[str, str]]) -> dict[str, Any]:
    gamer520: dict[str, dict[str, object]] = {}
    for platform in PLATFORMS:
        candidates = [
            row for row in rows
            if row.get("收录来源") == "gamer520"
            and platform in row.get("平台", "").split("/")
            and row.get("Gamer520帖子日期")
        ]
        if not candidates:
            continue
        newest = max(date.fromisoformat(row["Gamer520帖子日期"]) for row in candidates)
        newest_rows = [row for row in candidates if row["Gamer520帖子日期"] == newest.isoformat()]
        gamer520[platform] = {
            "latest_post_date": newest.isoformat(),
            "latest_link_id": max(extract_link_id(row.get("来源链接", "")) or 0 for row in newest_rows),
        }
    return {"version": 1, "gamer520": gamer520}


def read_state(path: str | Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        state = json.load(f)
    if not isinstance(state, dict) or state.get("version") != 1 or not isinstance(state.get("gamer520"), dict):
        raise ValueError("invalid Gamer520 sync state")
    return state


def write_state(path: str | Path, state: dict[str, Any]) -> None:
    target = Path(path)
    tmp = tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=target.parent, delete=False, suffix=".tmp")
    try:
        with tmp as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(tmp.name, target)
    except Exception:
        if os.path.exists(tmp.name):
            os.unlink(tmp.name)
        raise


def boundary_for(state: dict[str, Any], platform: str) -> date:
    try:
        return date.fromisoformat(str(state["gamer520"][platform]["latest_post_date"]))
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"sync state has no Gamer520 boundary for platform '{platform}'") from exc


def advance_state(state: dict[str, Any], platform: str, post_date: str, link_id: int) -> dict[str, Any]:
    current = state.setdefault("gamer520", {}).get(platform)
    incoming = date.fromisoformat(post_date)
    if current is None or incoming > date.fromisoformat(str(current["latest_post_date"])):
        state["gamer520"][platform] = {"latest_post_date": post_date, "latest_link_id": link_id}
    elif incoming == date.fromisoformat(str(current["latest_post_date"])):
        current["latest_link_id"] = max(int(current.get("latest_link_id", 0)), link_id)
    return state
