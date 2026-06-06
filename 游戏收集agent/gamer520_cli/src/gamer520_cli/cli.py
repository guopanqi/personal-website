import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from .config import DEFAULT_CSV_PATH
from .csv_store import read_csv, write_csv
from .models import CSV_FIELDS
from .normalize import (
    extract_link_id,
    is_url_valid,
    normalize_title_for_search,
    normalize_title_key,
    normalize_url,
)

app = typer.Typer(
    name="gamer520",
    help="CLI for managing Gamer520 game CSV data",
    no_args_is_help=True,
)

err_console = Console(stderr=True)

CSV_ARG = typer.Argument(
    None,
    help="Path to CSV file (default: ../gamer520-games.csv)",
)
CSV_OPT = typer.Option(
    None,
    "--csv",
    help="Path to CSV file (default: ../gamer520-games.csv)",
)


def _resolve_csv(csv_arg: Optional[str], csv_opt: Optional[str]) -> Path:
    if csv_opt:
        return Path(csv_opt)
    if csv_arg:
        return Path(csv_arg)
    return DEFAULT_CSV_PATH


def _fuzzy_match(query: str, target: str) -> bool:
    q = normalize_title_for_search(query)
    t = normalize_title_for_search(target)
    return q in t or t in q


def _search_rows(
    rows: list[dict[str, str]],
    *,
    title: Optional[str] = None,
    query: Optional[str] = None,
    link_id: Optional[int] = None,
) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    for row in rows:
        if title:
            if _fuzzy_match(title, row.get("标题", "")):
                results.append(row)
                continue
        if link_id is not None:
            row_url = row.get("链接", "")
            rid = extract_link_id(row_url)
            if rid == link_id:
                results.append(row)
                continue
        if query:
            q = query.lower()
            if (
                q in row.get("标题", "").lower()
                or q in row.get("链接", "").lower()
                or q in row.get("用户备注", "").lower()
            ):
                results.append(row)
                continue
    return results


def _latest_info(rows: list[dict[str, str]]) -> tuple[date, int, int]:
    latest: date | None = None
    for row in rows:
        try:
            d = date.fromisoformat(row["发布日期"])
        except ValueError:
            continue
        if latest is None or d > latest:
            latest = d
    if latest is None:
        msg = "No valid dates found in CSV"
        raise typer.BadParameter(msg)
    rows_on_date = [r for r in rows if r["发布日期"] == latest.isoformat()]
    max_id = 0
    for r in rows_on_date:
        rid = extract_link_id(r.get("链接", ""))
        if rid and rid > max_id:
            max_id = rid
    return latest, len(rows_on_date), max_id


def _check_duplicates(
    rows: list[dict[str, str]],
) -> dict[str, list[tuple[int, str, str]]]:
    link_groups: dict[str, list[tuple[int, str, str]]] = {}
    title_groups: dict[str, list[tuple[int, str, str]]] = {}
    for i, row in enumerate(rows, start=2):
        url = normalize_url(row.get("链接", ""))
        link_groups.setdefault(url, []).append((i, row["标题"], url))
        norm = normalize_title_key(row.get("标题", ""))
        if norm:
            title_groups.setdefault(norm, []).append((i, row["标题"], url))
    dups: dict[str, list[tuple[int, str, str]]] = {}
    link_dups = {k: v for k, v in link_groups.items() if len(v) > 1}
    title_dups = {k: v for k, v in title_groups.items() if len(v) > 1}
    dups["links"] = list(link_dups.values())
    dups["titles"] = list(title_dups.values())
    return dups


def _validate_rows(
    rows: list[dict[str, str]],
    strict: bool = False,
) -> list[str]:
    errors: list[str] = []
    for i, row in enumerate(rows, start=2):
        raw_date = row.get("发布日期", "").strip()
        platform = row.get("平台", "").strip()
        score = row.get("推荐度", "").strip()
        url = row.get("链接", "").strip()
        try:
            date.fromisoformat(raw_date)
        except ValueError:
            errors.append(f"Row {i}: invalid date '{raw_date}'")
        if platform not in ("PC", "Switch", "PC/Switch"):
            errors.append(f"Row {i}: invalid platform '{platform}'")
        if score not in ("1", "2", "3", "4", "5"):
            errors.append(f"Row {i}: invalid score '{score}'")
        if not url:
            errors.append(f"Row {i}: empty link")
        elif not is_url_valid(url):
            errors.append(f"Row {i}: invalid URL '{url[:60]}'")
        if not row.get("标题", "").strip():
            errors.append(f"Row {i}: empty title")
    dups = _check_duplicates(rows)
    for group in dups["links"]:
        lines = ", ".join(str(x[0]) for x in group)
        errors.append(f"Duplicate link (rows {lines}): {group[0][2]}")
    for group in dups["titles"]:
        lines = ", ".join(str(x[0]) for x in group)
        errors.append(f"Duplicate title (rows {lines}): {group[0][1]}")
    return errors


def _export_rows(
    rows: list[dict[str, str]],
    *,
    full: bool = False,
    format: str = "jsonl",
) -> str:
    fields = CSV_FIELDS
    if not full:
        fields = [f for f in CSV_FIELDS if f != "判断理由"]
    if format == "jsonl":
        lines: list[str] = []
        for row in rows:
            obj = {k: row.get(k, "") for k in fields}
            lines.append(json.dumps(obj, ensure_ascii=False))
        return "\n".join(lines)
    elif format == "csv":
        import csv
        import io

        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fields})
        return buf.getvalue()
    elif format == "md":
        lines_out: list[str] = []
        lines_out.append("| " + " | ".join(fields) + " |")
        lines_out.append("| " + " | ".join("---" for _ in fields) + " |")
        for row in rows:
            vals = [row.get(k, "").replace("|", "\\|") for k in fields]
            lines_out.append("| " + " | ".join(vals) + " |")
        return "\n".join(lines_out)
    else:
        msg = f"Unknown format: {format}"
        raise typer.BadParameter(msg)


@app.command()
def latest(
    csv_arg: Optional[str] = CSV_ARG,
    csv_opt: Optional[str] = CSV_OPT,
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    rows = read_csv(_resolve_csv(csv_arg, csv_opt))
    d, count_on_date, max_id = _latest_info(rows)
    total = len(rows)
    if json_output:
        obj = {
            "latest_date": d.isoformat(),
            "rows_on_latest_date": count_on_date,
            "latest_link_id": max_id,
            "total_rows": total,
        }
        print(json.dumps(obj, ensure_ascii=False))
    else:
        print(f"latest_date: {d.isoformat()}")
        print(f"rows_on_latest_date: {count_on_date}")
        print(f"latest_link_id: {max_id}")
        print(f"total_rows: {total}")
    raise typer.Exit()


@app.command()
def search(
    query: Optional[str] = typer.Argument(
        None,
        help="Search query (matches title, url, user_note)",
    ),
    title: Optional[str] = typer.Option(
        None, "--title", help="Fuzzy match on title field",
    ),
    limit: int = typer.Option(20, "--limit", "-n", help="Max results"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    csv_arg: Optional[str] = CSV_ARG,
    csv_opt: Optional[str] = CSV_OPT,
):
    if not query and not title:
        err_console.print("Error: provide a search query or --title", style="red")
        raise typer.Exit(code=2)
    rows = read_csv(_resolve_csv(csv_arg, csv_opt))
    link_id = None
    if query and query.isdigit():
        link_id = int(query)
    results = _search_rows(rows, title=title, query=query, link_id=link_id)
    results = results[:limit]
    if json_output:
        out = json.dumps(
            [
                {k: r.get(k, "") for k in ("发布日期", "平台", "标题", "推荐度", "链接", "用户备注")}
                for r in results
            ],
            ensure_ascii=False,
            indent=2,
        )
        print(out)
    else:
        if not results:
            print("No matches found.")
            raise typer.Exit()
        for r in results:
            print(
                f"{r['发布日期']} [{r['平台']}] {r['标题']} (score: {r['推荐度']}) {r['链接']}"
            )


@app.command()
def validate(
    csv_arg: Optional[str] = CSV_ARG,
    csv_opt: Optional[str] = CSV_OPT,
    strict: bool = typer.Option(False, "--strict", help="(reserved for future strict checks)"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    csv_path = _resolve_csv(csv_arg, csv_opt)
    try:
        rows = read_csv(csv_path)
    except ValueError as e:
        err_console.print(f"CSV read error: {e}", style="red")
        raise typer.Exit(code=1)
    errors = _validate_rows(rows, strict=strict)
    if json_output:
        obj = {
            "valid": len(errors) == 0,
            "total_rows": len(rows),
            "errors": errors,
        }
        print(json.dumps(obj, ensure_ascii=False))
    else:
        if errors:
            for e in errors:
                err_console.print(f"  {e}", style="red")
            err_console.print(f"\nTotal: {len(rows)} rows, {len(errors)} errors", style="red")
            raise typer.Exit(code=1)
        else:
            print(f"All valid: {len(rows)} rows, no errors.")


@app.command("sort")
def sort_csv(
    csv_arg: Optional[str] = CSV_ARG,
    csv_opt: Optional[str] = CSV_OPT,
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview sort, do not write"),
):
    csv_path = _resolve_csv(csv_arg, csv_opt)
    rows = read_csv(csv_path)

    def sort_key(row: dict[str, str]) -> tuple[str, int]:
        try:
            d = date.fromisoformat(row["发布日期"])
        except ValueError:
            d = date.min
        rid = extract_link_id(row.get("链接", "")) or 0
        return (-d.toordinal(), -rid)

    sorted_rows = sorted(rows, key=sort_key)
    if dry_run:
        print(f"Would sort {len(sorted_rows)} rows (no write)")
        for r in sorted_rows[:5]:
            print(f"  {r['发布日期']} id={extract_link_id(r.get('链接',''))} {r['标题']}")
        if len(sorted_rows) > 5:
            print(f"  ... and {len(sorted_rows) - 5} more")
    else:
        write_csv(csv_path, sorted_rows)
        print(f"Sorted and wrote {len(sorted_rows)} rows to {csv_path}")


@app.command()
def add(
    file_path: Optional[str] = typer.Argument(
        None,
        help="JSON file with entries to add",
    ),
    stdin: bool = typer.Option(False, "--stdin", help="Read JSON from stdin"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes, do not write"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    csv_arg: Optional[str] = CSV_ARG,
    csv_opt: Optional[str] = CSV_OPT,
):
    if not stdin and not file_path:
        err_console.print("Error: provide a JSON file or --stdin", style="red")
        raise typer.Exit(code=2)
    csv_path = _resolve_csv(csv_arg, csv_opt)
    existing = read_csv(csv_path)
    try:
        if stdin:
            raw = sys.stdin.read()
        else:
            raw = Path(file_path).read_text(encoding="utf-8")
        entries = json.loads(raw)
        if not isinstance(entries, list):
            err_console.print("Error: input must be a JSON array", style="red")
            raise typer.Exit(code=2)
    except json.JSONDecodeError as e:
        err_console.print(f"Error parsing JSON: {e}", style="red")
        raise typer.Exit(code=2)

    new_rows: list[dict[str, str]] = []
    errors: list[str] = []
    rejected_count = 0
    for i, entry in enumerate(entries):
        row = {}
        for field in CSV_FIELDS:
            val = entry.get(field, "")
            row[field] = str(val).strip() if val else ""
        row.setdefault("用户备注", "")
        errors_in_row = _validate_entry(row, i + 1, existing + new_rows)
        if errors_in_row:
            errors.extend(errors_in_row)
            rejected_count += 1
            continue
        new_rows.append(row)

    if errors:
        for e in errors:
            err_console.print(e, style="red")
        if json_output:
            print(
                json.dumps(
                    {
                        "accepted_entries": len(new_rows),
                        "rejected_entries": rejected_count,
                        "error_count": len(errors),
                        "errors": errors,
                    },
                    ensure_ascii=False,
                )
            )
        raise typer.Exit(code=1)

    all_rows = existing + new_rows
    validation_errors = _validate_rows(all_rows)
    if validation_errors:
        for e in validation_errors:
            err_console.print(f"Validation error: {e}", style="red")
        if json_output and dry_run:
            print(
                json.dumps(
                    {
                        "would_add": len(new_rows),
                        "validation_errors": validation_errors,
                    },
                    ensure_ascii=False,
                )
            )
        raise typer.Exit(code=1)

    if dry_run:
        msg = f"Would add {len(new_rows)} entries (no duplicates, no errors)"
        print(msg)
        for r in new_rows:
            print(f"  + {r['发布日期']} [{r['平台']}] {r['标题']} ({r['链接']})")
    else:
        write_csv(csv_path, all_rows)
        if json_output:
            print(
                json.dumps(
                    {"added": len(new_rows), "total": len(all_rows)},
                    ensure_ascii=False,
                )
            )
        else:
            print(f"Added {len(new_rows)} entries. Total: {len(all_rows)} rows.")


def _validate_entry(
    row: dict[str, str],
    num: int,
    all_rows: list[dict[str, str]],
) -> list[str]:
    errs: list[str] = []
    try:
        date.fromisoformat(row["发布日期"])
    except (ValueError, KeyError):
        errs.append(f"Entry #{num}: invalid date '{row.get('发布日期', '')}'")
    if row.get("平台") not in ("PC", "Switch", "PC/Switch"):
        errs.append(f"Entry #{num}: invalid platform '{row.get('平台', '')}'")
    score = row.get("推荐度", "")
    if score not in ("1", "2", "3", "4", "5"):
        errs.append(f"Entry #{num}: invalid score '{score}'")
    if not row.get("标题", "").strip():
        errs.append(f"Entry #{num}: empty title")
    if not row.get("链接", "").strip():
        errs.append(f"Entry #{num}: empty link")
    else:
        normalized = normalize_url(row["链接"])
        if not is_url_valid(normalized):
            errs.append(f"Entry #{num}: invalid URL '{row['链接'][:60]}'")
        dup = _find_duplicate_link(normalized, all_rows)
        if dup:
            errs.append(
                f"Entry #{num}: duplicate link '{normalized}' matches row {dup[0]}: {dup[1]}"
            )
    norm = normalize_title_key(row.get("标题", ""))
    if norm:
        dup = _find_duplicate_title(norm, all_rows)
        if dup:
            errs.append(
                f"Entry #{num}: duplicate title '{row.get('标题', '')}' matches row {dup[0]}: {dup[1]}"
            )
    return errs


def _find_duplicate_link(
    url: str, rows: list[dict[str, str]],
) -> tuple[int, str] | None:
    for i, r in enumerate(rows, start=2):
        if normalize_url(r.get("链接", "")) == url:
            return (i, r.get("标题", ""))
    return None


def _find_duplicate_title(
    norm_title: str, rows: list[dict[str, str]],
) -> tuple[int, str] | None:
    for i, r in enumerate(rows, start=2):
        if normalize_title_key(r.get("标题", "")) == norm_title:
            return (i, r.get("标题", ""))
    return None


@app.command()
def remove(
    title: str = typer.Option(..., "--title", help="Exact title to remove (after normalization)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview removal, do not write"),
    yes: bool = typer.Option(False, "--yes", help="Confirm removal"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    csv_arg: Optional[str] = CSV_ARG,
    csv_opt: Optional[str] = CSV_OPT,
):
    csv_path = _resolve_csv(csv_arg, csv_opt)
    rows = read_csv(csv_path)
    norm_query = normalize_title_key(title)
    matches: list[tuple[int, dict[str, str]]] = []
    for i, r in enumerate(rows, start=2):
        if normalize_title_key(r.get("标题", "")) == norm_query:
            matches.append((i, r))
    if len(matches) == 0:
        err_console.print(f"No match for title '{title}' (normalized: '{norm_query}')", style="red")
        raise typer.Exit(code=1)
    if len(matches) > 1:
        err_console.print(
            f"Multiple matches ({len(matches)}) for title. Data integrity issue.", style="red"
        )
        for line, r in matches:
            err_console.print(f"  Row {line}: {r['标题']} ({r['链接']})")
        raise typer.Exit(code=1)
    line, match_row = matches[0]
    if dry_run:
        if json_output:
            print(json.dumps({"would_remove": match_row}, ensure_ascii=False))
        else:
            print(
                f"Would remove row {line}: {match_row['发布日期']} [{match_row['平台']}] {match_row['标题']}"
            )
        raise typer.Exit()
    if not yes:
        err_console.print(
            "Use --yes to confirm removal (preview with --dry-run first)", style="red"
        )
        raise typer.Exit(code=1)
    remaining = [r for i, r in enumerate(rows, start=2) if i != line]
    validation_errors = _validate_rows(remaining)
    if validation_errors:
        for e in validation_errors:
            err_console.print(f"Post-removal validation error: {e}", style="red")
        raise typer.Exit(code=1)
    write_csv(csv_path, remaining)
    if json_output:
        print(
            json.dumps({"removed": match_row["标题"], "remaining": len(remaining)}, ensure_ascii=False)
        )
    else:
        print(f"Removed row {line}: {match_row['标题']}. {len(remaining)} rows remaining.")


@app.command()
def export(
    date_filter: Optional[str] = typer.Option(None, "--date", help="Export entries for a specific date"),
    days: Optional[int] = typer.Option(None, "--days", help="Export entries from last N days"),
    query: Optional[str] = typer.Option(None, "--query", help="Export entries matching query"),
    platform: Optional[str] = typer.Option(None, "--platform", help="Filter by platform (PC/Switch/PC/Switch)"),
    latest_only: bool = typer.Option(False, "--latest", help="Export only latest date entries"),
    format: str = typer.Option("jsonl", "--format", help="Output format: jsonl, csv, md"),
    full: bool = typer.Option(False, "--full", help="Include 判断理由 field"),
    csv_arg: Optional[str] = CSV_ARG,
    csv_opt: Optional[str] = CSV_OPT,
):
    rows = read_csv(_resolve_csv(csv_arg, csv_opt))
    if date_filter:
        rows = [r for r in rows if r.get("发布日期", "") == date_filter]
    if days is not None:
        cutoff = date.today() - timedelta(days=days)
        rows = [
            r
            for r in rows
            if r.get("发布日期", "")
            and date.fromisoformat(r["发布日期"]) >= cutoff
        ]
    if query:
        q = query.lower()
        rows = [
            r
            for r in rows
            if q in r.get("标题", "").lower()
            or q in r.get("标签", "").lower()
            or q in r.get("用户备注", "").lower()
        ]
    if platform:
        rows = [r for r in rows if r.get("平台", "") == platform]
    if latest_only:
        d_info, _, _ = _latest_info(rows)
        rows = [r for r in rows if r.get("发布日期", "") == d_info.isoformat()]
    output = _export_rows(rows, full=full, format=format)
    print(output)


if __name__ == "__main__":
    app()
