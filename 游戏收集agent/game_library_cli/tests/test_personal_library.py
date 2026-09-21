import json
from datetime import date
from pathlib import Path

from typer.testing import CliRunner

from game_library_cli.cli import app
from game_library_cli.csv_store import read_csv
from game_library_cli.reconcile import reconcile_items


runner = CliRunner()
FIXTURE_CSV = Path(__file__).parent / "fixtures" / "games.csv"


def test_migrate_preserves_legacy_games_and_creates_gamer520_cursor(tmp_path):
    csv_path = tmp_path / "games.csv"
    csv_path.write_bytes(FIXTURE_CSV.read_bytes())
    state_path = tmp_path / "state.json"

    preview = runner.invoke(app, ["migrate", "--dry-run", "--csv", str(csv_path), "--state", str(state_path)])
    assert preview.exit_code == 0
    assert "Would migrate CSV" in preview.stdout

    result = runner.invoke(app, ["migrate", "--yes", "--csv", str(csv_path), "--state", str(state_path)])
    assert result.exit_code == 0, result.stderr
    rows = read_csv(csv_path)
    assert rows[0]["收录来源"] == "gamer520"
    assert rows[0]["收录日期"] == "2026-06-06"
    assert rows[0]["Gamer520帖子日期"] == "2026-06-06"
    state = json.loads(state_path.read_text())
    assert state["gamer520"]["PC"]["latest_post_date"] == "2026-06-06"


def test_manual_add_allows_an_empty_source_url(tmp_path):
    csv_path = tmp_path / "games.csv"
    csv_path.write_bytes(FIXTURE_CSV.read_bytes())
    runner.invoke(app, ["migrate", "--yes", "--csv", str(csv_path), "--state", str(tmp_path / "state.json")])
    payload = json.dumps([{
        "source": {"type": "manual", "collected_date": "2026-08-21", "platform": "PC", "title": "Manual Game"},
        "assessment": {"tags": ["叙事"], "judgment": "手工收藏。", "score": 4, "reason": "手工判断。", "user_note": "wishlist"},
    }], ensure_ascii=False)

    result = runner.invoke(app, ["add", "--stdin", "--yes", "--csv", str(csv_path)], input=payload)
    assert result.exit_code == 0, result.stderr
    added = read_csv(csv_path)[-1]
    assert added["收录来源"] == "manual"
    assert added["来源链接"] == ""
    assert added["Gamer520帖子日期"] == ""


def test_multiple_manual_entries_can_omit_source_urls(tmp_path):
    csv_path = tmp_path / "games.csv"
    csv_path.write_bytes(FIXTURE_CSV.read_bytes())
    runner.invoke(app, ["migrate", "--yes", "--csv", str(csv_path), "--state", str(tmp_path / "state.json")])
    payload = json.dumps([
        {
            "source": {"type": "manual", "platform": "PC", "title": "Manual Game One"},
        "assessment": {"tags": [], "judgment": "手工收藏。", "score": 4, "reason": "手工判断。", "user_note": "wishlist"},
        },
        {
            "source": {"type": "manual", "platform": "PC", "title": "Manual Game Two"},
            "assessment": {"tags": [], "judgment": "手工收藏。", "score": 4, "reason": "手工判断。", "user_note": "wishlist"},
        },
    ], ensure_ascii=False)

    result = runner.invoke(app, ["add", "--stdin", "--yes", "--csv", str(csv_path)], input=payload)
    assert result.exit_code == 0, result.stderr
    assert [row["来源链接"] for row in read_csv(csv_path)[-2:]] == ["", ""]


def test_add_requires_yes_for_persistent_write(tmp_path):
    csv_path = tmp_path / "games.csv"
    csv_path.write_bytes(FIXTURE_CSV.read_bytes())
    payload = json.dumps([{
        "source": {"type": "manual", "platform": "PC", "title": "Pending Confirmation"},
        "assessment": {"tags": [], "judgment": "手工收藏。", "score": 4, "reason": "手工判断。"},
    }], ensure_ascii=False)

    result = runner.invoke(app, ["add", "--stdin", "--csv", str(csv_path)], input=payload)

    assert result.exit_code == 1
    assert "Use --yes to confirm add" in result.stderr
    assert len(read_csv(csv_path)) == 5


def test_gamer520_scan_acknowledges_manual_match_without_platform_merge():
    manual = {
        "收录日期": "2026-08-21", "收录来源": "manual", "Gamer520帖子日期": "", "来源链接": "",
        "平台": "PC", "标题": "Shared Game", "标签": "", "游戏判断": "", "推荐度": "4", "判断理由": "", "用户备注": "wishlist",
    }
    item = {"title": "Shared Game", "raw_title": "Shared Game", "url": "https://www.gamer520.com/200001.html", "date": "2026-08-21", "date_text": ""}
    result = reconcile_items([manual], [item], platform="Switch", latest_date=date(2026, 8, 20))
    assert len(result["existing"]) == 1
    assert result["platform_merges"] == []
    assert result["existing"][0]["match"]["source"] == "manual"
