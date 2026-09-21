import csv
import os
import tempfile
from pathlib import Path
from typing import Any

from .models import CSV_FIELDS, LEGACY_CSV_FIELDS, GameRow, csv_dict_to_row, legacy_row_to_current, row_to_csv_dict


def read_csv(path: str | Path) -> list[dict[str, str]]:
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        csv_fields = reader.fieldnames
        if not csv_fields:
            raise ValueError("CSV file is empty or has no header")
        legacy = list(csv_fields) == LEGACY_CSV_FIELDS
        if not legacy:
            check_header(csv_fields)
        rows: list[dict[str, str]] = []
        for i, row in enumerate(reader, start=2):
            clean = {k: v for k, v in row.items() if k is not None}
            if legacy:
                clean = legacy_row_to_current(clean)
            for f in CSV_FIELDS:
                if f not in clean:
                    if f == "用户备注":
                        clean[f] = ""
                    else:
                        raise ValueError(f"Row {i}: missing field '{f}'")
            rows.append(clean)
    return rows


def read_raw_csv(path: str | Path) -> tuple[list[str], list[dict[str, str]]]:
    """Read a CSV without enforcing the current schema; used only by migration."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        if not fieldnames:
            raise ValueError("CSV file is empty or has no header")
        return list(fieldnames), [{k: v for k, v in row.items() if k is not None} for row in reader]


def write_csv(path: str | Path, rows: list[dict[str, str]]) -> None:
    path = Path(path)
    tmp = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8-sig",
        newline="",
        dir=path.parent,
        delete=False,
        suffix=".tmp",
    )
    try:
        with tmp as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, lineterminator="\n")
            writer.writeheader()
            for row in rows:
                if set(row).issuperset(LEGACY_CSV_FIELDS):
                    row = legacy_row_to_current(row)
                writer.writerow({field: row.get(field, "") for field in CSV_FIELDS})
        os.replace(tmp.name, path)
    except Exception:
        if os.path.exists(tmp.name):
            os.unlink(tmp.name)
        raise


def read_rows(path: str | Path) -> list[GameRow]:
    data = read_csv(path)
    return [csv_dict_to_row(r) for r in data]


def check_header(fieldnames: list[Any] | None) -> None:
    if not fieldnames:
        raise ValueError("No header found")
    if list(fieldnames) != CSV_FIELDS:
        missing = set(CSV_FIELDS) - set(fieldnames)
        extra = set(fieldnames) - set(CSV_FIELDS)
        parts = []
        if missing:
            parts.append(f"missing: {missing}")
        if extra:
            parts.append(f"extra: {extra}")
        if parts:
            raise ValueError(f"CSV header mismatch: {'; '.join(parts)}")
