from __future__ import annotations

import re
from collections.abc import Mapping
from datetime import date
from difflib import SequenceMatcher
from typing import Any

from .doctor_reviews import review_key
from .normalize import is_url_valid, normalize_title_key, normalize_url

_CJK_AND_DIGITS = re.compile(r"[\u3400-\u9fff0-9]+")


def reconcile_items(
    rows: list[dict[str, str]],
    items: list[dict[str, Any]],
    *,
    platform: str,
    latest_date: date,
    candidate_limit: int = 3,
    reviews: Mapping[tuple[str, str], Mapping[str, str]] | None = None,
) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = {
        "existing": [],
        "platform_merges": [],
        "ambiguous": [],
        "new": [],
        "before_boundary": [],
    }

    title_index: dict[str, list[dict[str, str]]] = {}
    url_index: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        title_key = normalize_title_key(row.get("标题", ""))
        if title_key:
            title_index.setdefault(title_key, []).append(row)
        normalized_url = normalize_url(row.get("来源链接", ""))
        if normalized_url:
            url_index.setdefault(normalized_url, []).append(row)

    normalized_items = [_normalize_source_item(item) for item in items]
    reviews = reviews or {}
    for source in normalized_items:
        source_date = date.fromisoformat(source["date"])
        if source_date < latest_date:
            groups["before_boundary"].append({"source": source})
            continue

        title_key = normalize_title_key(source["title"])
        exact_title_matches = title_index.get(title_key, [])
        url_matches = url_index.get(normalize_url(source["url"]), [])
        if len(exact_title_matches) == 1:
            title_match = exact_title_matches[0]
            conflicting_url_matches = [row for row in url_matches if row is not title_match]
            if conflicting_url_matches:
                groups["ambiguous"].append(
                    {
                        "source": source,
                        "reason": "title_url_conflict",
                        "candidates": [
                            _match_view(title_match, score=1.0),
                            *[
                                _match_view(row, score=1.0)
                                for row in conflicting_url_matches
                            ],
                        ],
                    }
                )
                continue
            _append_determined_match(
                groups,
                source,
                title_match,
                platform=platform,
                reason="title_exact",
            )
            continue
        if len(exact_title_matches) > 1:
            groups["ambiguous"].append(
                {
                    "source": source,
                    "reason": "title_exact_multiple",
                    "candidates": [_match_view(row, score=1.0) for row in exact_title_matches],
                }
            )
            continue

        if len(url_matches) == 1:
            _append_determined_match(
                groups,
                source,
                url_matches[0],
                platform=platform,
                reason="url_exact",
            )
            continue
        if len(url_matches) > 1:
            groups["ambiguous"].append(
                {
                    "source": source,
                    "reason": "url_exact_multiple",
                    "candidates": [_match_view(row, score=1.0) for row in url_matches],
                }
            )
            continue

        similar_matches = _similar_title_matches(source["title"], rows)
        if similar_matches:
            reviewed_same: list[tuple[float, dict[str, str], Mapping[str, str]]] = []
            unresolved_matches: list[tuple[float, dict[str, str]]] = []
            reviewed_distinct: list[dict[str, Any]] = []
            candidate_views: list[dict[str, Any]] = []
            for score, row in similar_matches:
                candidate = _match_view(row, score=score)
                review = reviews.get(review_key(source["title"], row.get("标题", "")))
                if review:
                    candidate["review"] = dict(review)
                    if review.get("decision") == "same":
                        reviewed_same.append((score, row, review))
                    elif review.get("decision") == "distinct":
                        reviewed_distinct.append(candidate)
                else:
                    unresolved_matches.append((score, row))
                candidate_views.append(candidate)

            if len(reviewed_same) == 1 and not unresolved_matches:
                _append_determined_match(
                    groups,
                    source,
                    reviewed_same[0][1],
                    platform=platform,
                    reason="doctor_review_same",
                )
                continue
            if not reviewed_same and not unresolved_matches and reviewed_distinct:
                groups["new"].append(
                    {
                        "source": source,
                        "reason": "doctor_review_distinct",
                        "reviewed_candidates": reviewed_distinct,
                    }
                )
                continue
            groups["ambiguous"].append(
                {
                    "source": source,
                    "reason": "title_similar",
                    "candidates": candidate_views[:candidate_limit],
                }
            )
        else:
            groups["new"].append({"source": source})

    candidate_count = len(normalized_items) - len(groups["before_boundary"])
    return {
        "platform": platform,
        "latest_date": latest_date.isoformat(),
        "match_order": ["title_exact", "url_exact", "title_similar"],
        "summary": {
            "input": len(normalized_items),
            "candidates": candidate_count,
            "existing": len(groups["existing"]),
            "platform_merges": len(groups["platform_merges"]),
            "ambiguous": len(groups["ambiguous"]),
            "new": len(groups["new"]),
            "before_boundary": len(groups["before_boundary"]),
        },
        **groups,
    }


def _normalize_source_item(item: dict[str, Any]) -> dict[str, str]:
    raw_title = str(item.get("raw_title") or item.get("title") or "").strip()
    title = str(item.get("title") or raw_title).strip()
    url = str(item.get("url") or "").strip()
    raw_date = str(item.get("date") or "").strip()
    if not title:
        raise ValueError("reconcile item has an empty title")
    if not url:
        raise ValueError(f"reconcile item '{title}' has an empty URL")
    if not is_url_valid(url):
        raise ValueError(f"reconcile item '{title}' has invalid URL '{url}'")
    try:
        date.fromisoformat(raw_date)
    except ValueError as exc:
        raise ValueError(f"reconcile item '{title}' has invalid date '{raw_date}'") from exc
    return {
        "title": title,
        "raw_title": raw_title,
        "url": url,
        "date": raw_date,
        "date_text": str(item.get("date_text") or "").strip(),
    }


def _append_determined_match(
    groups: dict[str, list[dict[str, Any]]],
    source: dict[str, str],
    row: dict[str, str],
    *,
    platform: str,
    reason: str,
) -> None:
    # A manual record is already the canonical game record.  A Gamer520 scan
    # must acknowledge it without changing its source, platform, or judgement.
    existing_platforms = row.get("平台", "").split("/")
    group = "existing" if row.get("收录来源") == "manual" or platform in existing_platforms else "platform_merges"
    groups[group].append(
        {
            "source": source,
            "reason": reason,
            "match": _match_view(row, score=1.0),
        }
    )


def _similar_title_matches(
    source_title: str,
    rows: list[dict[str, str]],
) -> list[tuple[float, dict[str, str]]]:
    matches: list[tuple[float, dict[str, str]]] = []
    for row in rows:
        score = title_similarity(source_title, row.get("标题", ""))
        if score >= 0.62:
            matches.append((score, row))
    matches.sort(key=lambda item: item[0], reverse=True)
    return matches


def title_similarity(left: str, right: str) -> float:
    left_key = normalize_title_key(left)
    right_key = normalize_title_key(right)
    if not left_key or not right_key:
        return 0.0

    scores = [SequenceMatcher(None, left_key, right_key).ratio()]
    left_cjk = "".join(_CJK_AND_DIGITS.findall(left_key))
    right_cjk = "".join(_CJK_AND_DIGITS.findall(right_key))
    if min(len(left_cjk), len(right_cjk)) >= 4:
        scores.append(SequenceMatcher(None, left_cjk, right_cjk).ratio())
        shorter, longer = sorted((left_cjk, right_cjk), key=len)
        if shorter in longer:
            coverage = len(shorter) / len(longer)
            scores.append(min(0.94, 0.72 + 0.22 * coverage))
    return max(scores)


def _match_view(row: dict[str, str], *, score: float) -> dict[str, Any]:
    return {
        "title": row.get("标题", ""),
        "platform": row.get("平台", ""),
        "source": row.get("收录来源", ""),
        "url": row.get("来源链接", ""),
        "score": round(score, 3),
    }
