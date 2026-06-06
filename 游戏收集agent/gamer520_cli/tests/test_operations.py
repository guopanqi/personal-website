import json
import os
import tempfile
from pathlib import Path

from typer.testing import CliRunner

from gamer520_cli.cli import app
from gamer520_cli.csv_store import read_csv, write_csv
from gamer520_cli.normalize import extract_link_id

FIXTURE_DIR = Path(__file__).parent / "fixtures"
FIXTURE_CSV = FIXTURE_DIR / "games.csv"

runner = CliRunner()


def _temp_copy(path: str) -> str:
    tmp = tempfile.NamedTemporaryFile(
        mode="wb", suffix=".csv", delete=False
    )
    tmp.write(Path(path).read_bytes())
    tmp.close()
    return tmp.name


def _test_csv(rows: list[dict[str, str]]) -> str:
    tmp = tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8-sig", newline="", suffix=".csv", delete=False
    )
    tmp.close()
    write_csv(tmp.name, rows)
    return tmp.name


def test_latest():
    result = runner.invoke(app, ["latest", "--csv", str(FIXTURE_CSV)])
    assert result.exit_code == 0
    assert "latest_date: 2026-06-06" in result.stdout
    assert "total_rows: 5" in result.stdout


def test_latest_json():
    result = runner.invoke(app, ["latest", "--csv", str(FIXTURE_CSV), "--json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["latest_date"] == "2026-06-06"
    assert data["total_rows"] == 5


def test_search_by_query():
    result = runner.invoke(app, ["search", "Alpha", "--csv", str(FIXTURE_CSV)])
    assert result.exit_code == 0
    assert "Game Alpha" in result.stdout


def test_search_by_title():
    result = runner.invoke(app, ["search", "--title", "game alpha", "--csv", str(FIXTURE_CSV)])
    assert result.exit_code == 0
    assert "Game Alpha" in result.stdout


def test_search_by_link_id():
    result = runner.invoke(app, ["search", "100001", "--csv", str(FIXTURE_CSV)])
    assert result.exit_code == 0
    assert "Game Alpha" in result.stdout


def test_search_no_match():
    result = runner.invoke(app, ["search", "nonexistent", "--csv", str(FIXTURE_CSV)])
    assert "No matches found" in result.stdout


def test_search_json():
    result = runner.invoke(app, ["search", "Alpha", "--csv", str(FIXTURE_CSV), "--json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert len(data) == 1
    assert data[0]["标题"] == "Game Alpha"


def test_validate_ok():
    result = runner.invoke(app, ["validate", "--csv", str(FIXTURE_CSV)])
    assert result.exit_code == 0
    assert "All valid" in result.stdout


def test_validate_fails_invalid_date():
    rows = [
        {
            "发布日期": "not-a-date",
            "平台": "PC",
            "标题": "Bad",
            "标签": "",
            "一句话描述": "",
            "推荐度": "3",
            "推荐标签": "",
            "判断理由": "",
            "链接": "https://www.gamer520.com/100010.html",
            "用户备注": "",
        }
    ]
    path = _test_csv(rows)
    try:
        result = runner.invoke(app, ["validate", "--csv", path])
        assert result.exit_code == 1
        assert "invalid date" in result.stderr
    finally:
        os.unlink(path)


def test_validate_fails_invalid_platform():
    rows = [
        {
            "发布日期": "2026-06-06",
            "平台": "PS5",
            "标题": "Bad",
            "标签": "",
            "一句话描述": "",
            "推荐度": "3",
            "推荐标签": "",
            "判断理由": "",
            "链接": "https://www.gamer520.com/100010.html",
            "用户备注": "",
        }
    ]
    path = _test_csv(rows)
    try:
        result = runner.invoke(app, ["validate", "--csv", path])
        assert result.exit_code == 1
        assert "invalid platform" in result.stderr
    finally:
        os.unlink(path)


def test_validate_fails_invalid_score():
    rows = [
        {
            "发布日期": "2026-06-06",
            "平台": "PC",
            "标题": "Bad",
            "标签": "",
            "一句话描述": "",
            "推荐度": "6",
            "推荐标签": "",
            "判断理由": "",
            "链接": "https://www.gamer520.com/100010.html",
            "用户备注": "",
        }
    ]
    path = _test_csv(rows)
    try:
        result = runner.invoke(app, ["validate", "--csv", path])
        assert result.exit_code == 1
        assert "invalid score" in result.stderr
    finally:
        os.unlink(path)


def test_validate_fails_duplicate_title():
    rows = [
        {
            "发布日期": "2026-06-06",
            "平台": "PC",
            "标题": "Same Game",
            "标签": "",
            "一句话描述": "",
            "推荐度": "3",
            "推荐标签": "",
            "判断理由": "",
            "链接": "https://www.gamer520.com/100001.html",
            "用户备注": "",
        },
        {
            "发布日期": "2026-06-07",
            "平台": "PC",
            "标题": "Same Game",
            "标签": "",
            "一句话描述": "",
            "推荐度": "4",
            "推荐标签": "",
            "判断理由": "",
            "链接": "https://www.gamer520.com/200001.html",
            "用户备注": "",
        },
    ]
    path = _test_csv(rows)
    try:
        result = runner.invoke(app, ["validate", "--csv", path])
        assert result.exit_code == 1
        assert "Duplicate title" in result.stderr
    finally:
        os.unlink(path)


def test_validate_fails_duplicate_link():
    rows = [
        {
            "发布日期": "2026-06-06",
            "平台": "PC",
            "标题": "Game A",
            "标签": "",
            "一句话描述": "",
            "推荐度": "3",
            "推荐标签": "",
            "判断理由": "",
            "链接": "https://www.gamer520.com/100001.html",
            "用户备注": "",
        },
        {
            "发布日期": "2026-06-07",
            "平台": "PC",
            "标题": "Game B",
            "标签": "",
            "一句话描述": "",
            "推荐度": "4",
            "推荐标签": "",
            "判断理由": "",
            "链接": "https://www.gamer520.com/100001.html",
            "用户备注": "",
        },
    ]
    path = _test_csv(rows)
    try:
        result = runner.invoke(app, ["validate", "--csv", path])
        assert result.exit_code == 1
        assert "Duplicate link" in result.stderr
    finally:
        os.unlink(path)


def test_sort_dry_run():
    result = runner.invoke(app, ["sort", "--csv", str(FIXTURE_CSV), "--dry-run"])
    assert result.exit_code == 0
    assert "Would sort" in result.stdout


def test_sort_actual():
    rows = [
        {
            "发布日期": d,
            "平台": "PC",
            "标题": f"Game {i}",
            "标签": "",
            "一句话描述": "",
            "推荐度": "3",
            "推荐标签": "",
            "判断理由": "",
            "链接": f"https://www.gamer520.com/{link_id}.html",
            "用户备注": "",
        }
        for i, (d, link_id) in enumerate(
            [("2026-06-05", 100002), ("2026-06-06", 100003), ("2026-06-06", 100001)], start=1
        )
    ]
    path = _test_csv(rows)
    try:
        result = runner.invoke(app, ["sort", "--csv", path])
        assert result.exit_code == 0
        sorted_rows = read_csv(path)
        assert sorted_rows[0]["发布日期"] == "2026-06-06"
        assert extract_link_id(sorted_rows[0]["链接"]) == 100003
        assert sorted_rows[1]["发布日期"] == "2026-06-06"
        assert extract_link_id(sorted_rows[1]["链接"]) == 100001
        assert sorted_rows[2]["发布日期"] == "2026-06-05"
    finally:
        os.unlink(path)


def test_add_stdin():
    csv_path = _temp_copy(str(FIXTURE_CSV))
    entry = {
        "发布日期": "2026-06-07",
        "平台": "PC",
        "标题": "New Game",
        "标签": "action",
        "一句话描述": "A new game.",
        "推荐度": "4",
        "推荐标签": "推荐",
        "判断理由": "Looks good.",
        "链接": "https://www.gamer520.com/200001.html",
        "用户备注": "",
    }
    payload = json.dumps([entry])
    try:
        result = runner.invoke(app, ["add", "--stdin", "--csv", csv_path], input=payload)
        assert result.exit_code == 0, result.stderr
        assert "Added 1 entries" in result.stdout
    finally:
        os.unlink(csv_path)


def test_add_dry_run():
    result = runner.invoke(
        app,
        ["add", "--stdin", "--csv", str(FIXTURE_CSV), "--dry-run"],
        input=json.dumps([{"发布日期": "2026-06-07", "平台": "PC", "标题": "Dry Run Game", "标签": "action", "一句话描述": "Dry run.", "推荐度": "3", "推荐标签": "可试", "判断理由": "Test.", "链接": "https://www.gamer520.com/200002.html", "用户备注": ""}]),
    )
    assert result.exit_code == 0
    assert "Would add" in result.stdout


def test_add_rejects_duplicate_link():
    rows = [
        {
            "发布日期": "2026-06-06",
            "平台": "PC",
            "标题": "Existing",
            "标签": "",
            "一句话描述": "",
            "推荐度": "3",
            "推荐标签": "",
            "判断理由": "",
            "链接": "https://www.gamer520.com/100001.html",
            "用户备注": "",
        }
    ]
    path = _test_csv(rows)
    entry = {
        "发布日期": "2026-06-07",
        "平台": "PC",
        "标题": "Duplicate Link",
        "标签": "",
        "一句话描述": "",
        "推荐度": "4",
        "推荐标签": "",
        "判断理由": "",
        "链接": "https://www.gamer520.com/100001.html",
        "用户备注": "",
    }
    payload = json.dumps([entry])
    try:
        result = runner.invoke(app, ["add", "--stdin", "--csv", path], input=payload)
        assert result.exit_code == 1
        assert "duplicate link" in result.stderr
    finally:
        os.unlink(path)


def test_add_rejects_duplicate_title():
    rows = [
        {
            "发布日期": "2026-06-06",
            "平台": "PC",
            "标题": "Unique Title",
            "标签": "",
            "一句话描述": "",
            "推荐度": "3",
            "推荐标签": "",
            "判断理由": "",
            "链接": "https://www.gamer520.com/100001.html",
            "用户备注": "",
        }
    ]
    path = _test_csv(rows)
    entry = {
        "发布日期": "2026-06-07",
        "平台": "PC",
        "标题": "Unique Title",
        "标签": "",
        "一句话描述": "",
        "推荐度": "4",
        "推荐标签": "",
        "判断理由": "",
        "链接": "https://www.gamer520.com/200001.html",
        "用户备注": "",
    }
    payload = json.dumps([entry])
    try:
        result = runner.invoke(app, ["add", "--stdin", "--csv", path], input=payload)
        assert result.exit_code == 1
        assert "duplicate title" in result.stderr
    finally:
        os.unlink(path)


def test_add_from_file():
    csv_path = _temp_copy(str(FIXTURE_CSV))
    entry = {
        "发布日期": "2026-06-08",
        "平台": "Switch",
        "标题": "File Import Game",
        "标签": "rpg",
        "一句话描述": "From file.",
        "推荐度": "5",
        "推荐标签": "推荐",
        "判断理由": "Good.",
        "链接": "https://www.gamer520.com/300001.html",
        "用户备注": "",
    }
    tmp = tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", suffix=".json", delete=False
    )
    json.dump([entry], tmp, ensure_ascii=False)
    tmp.close()
    try:
        result = runner.invoke(app, ["add", tmp.name, "--csv", csv_path])
        assert result.exit_code == 0, result.stderr
        assert "Added 1 entries" in result.stdout
    finally:
        os.unlink(tmp.name)
        os.unlink(csv_path)


def test_remove_dry_run():
    result = runner.invoke(
        app, ["remove", "--title", "Game Alpha", "--csv", str(FIXTURE_CSV), "--dry-run"]
    )
    assert result.exit_code == 0
    assert "Would remove" in result.stdout


def test_remove_requires_yes():
    result = runner.invoke(app, ["remove", "--title", "Game Alpha", "--csv", str(FIXTURE_CSV)])
    assert result.exit_code == 1
    assert "--yes" in result.stderr


def test_remove_actual():
    csv_path = _temp_copy(str(FIXTURE_CSV))
    try:
        result = runner.invoke(
            app, ["remove", "--title", "Game Alpha", "--csv", csv_path, "--yes"]
        )
        assert result.exit_code == 0, result.stderr
        assert "Removed row" in result.stdout
        remaining = read_csv(csv_path)
        titles = [r["标题"] for r in remaining]
        assert "Game Alpha" not in titles
        assert len(remaining) == 4
    finally:
        os.unlink(csv_path)


def test_remove_no_match():
    result = runner.invoke(
        app, ["remove", "--title", "Nonexistent Game", "--csv", str(FIXTURE_CSV)]
    )
    assert result.exit_code == 1
    assert "No match" in result.stderr


def test_remove_partial_title_fails():
    result = runner.invoke(app, ["remove", "--title", "Game", "--csv", str(FIXTURE_CSV)])
    assert result.exit_code == 1


def test_remove_rejects_if_resulting_csv_invalid():
    rows = [
        {
            "发布日期": "2026-06-06",
            "平台": "PC",
            "标题": "Foo",
            "标签": "",
            "一句话描述": "",
            "推荐度": "3",
            "推荐标签": "",
            "判断理由": "",
            "链接": "https://www.gamer520.com/100001.html",
            "用户备注": "",
        },
        {
            "发布日期": "2026-06-07",
            "平台": "PC",
            "标题": "Target To Remove",
            "标签": "",
            "一句话描述": "",
            "推荐度": "4",
            "推荐标签": "",
            "判断理由": "",
            "链接": "https://www.gamer520.com/200001.html",
            "用户备注": "",
        },
        {
            "发布日期": "2026-06-08",
            "平台": "PC",
            "标题": "Foo",
            "标签": "",
            "一句话描述": "",
            "推荐度": "4",
            "推荐标签": "",
            "判断理由": "",
            "链接": "https://www.gamer520.com/300001.html",
            "用户备注": "",
        },
    ]
    path = _test_csv(rows)
    try:
        result = runner.invoke(
            app, ["remove", "--title", "Target To Remove", "--csv", path, "--yes"]
        )
        assert result.exit_code == 1
        assert "Post-removal validation error" in result.stderr
    finally:
        os.unlink(path)


def test_export_latest_jsonl():
    result = runner.invoke(app, ["export", "--latest", "--csv", str(FIXTURE_CSV)])
    assert result.exit_code == 0
    lines = result.stdout.strip().split("\n")
    assert len(lines) == 1
    for line in lines:
        obj = json.loads(line)
        assert "标题" in obj
        assert "判断理由" not in obj


def test_export_full_includes_reasoning():
    result = runner.invoke(app, ["export", "--latest", "--csv", str(FIXTURE_CSV), "--full"])
    assert result.exit_code == 0
    lines = result.stdout.strip().split("\n")
    obj = json.loads(lines[0])
    assert "判断理由" in obj


def test_export_query():
    result = runner.invoke(app, ["export", "--query", "Alpha", "--csv", str(FIXTURE_CSV)])
    assert result.exit_code == 0
    lines = result.stdout.strip().split("\n")
    assert len(lines) == 1
    obj = json.loads(lines[0])
    assert "Alpha" in obj["标题"]


def test_export_platform():
    result = runner.invoke(app, ["export", "--platform", "Switch", "--csv", str(FIXTURE_CSV)])
    assert result.exit_code == 0
    lines = result.stdout.strip().split("\n")
    assert len(lines) == 2
    for line in lines:
        obj = json.loads(line)
        assert obj["平台"] == "Switch"
