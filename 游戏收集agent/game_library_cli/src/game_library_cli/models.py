from datetime import date
from typing import Literal

from pydantic import AnyUrl, BaseModel, field_validator


class GameRow(BaseModel):
    collected_date: date
    source: Literal["gamer520", "manual"]
    gamer520_post_date: date | None = None
    source_url: AnyUrl | None = None
    platform: Literal["PC", "Switch", "PC/Switch"]
    title: str
    tags: str
    game_judgment: str
    score: int
    reasoning: str
    user_note: str = ""

    @field_validator("score")
    @classmethod
    def score_range(cls, v: int) -> int:
        if v < 1 or v > 5:
            raise ValueError(f"score must be 1-5, got {v}")
        return v


CSV_FIELDS = [
    "收录日期",
    "收录来源",
    "Gamer520帖子日期",
    "来源链接",
    "平台",
    "标题",
    "标签",
    "游戏判断",
    "推荐度",
    "判断理由",
    "用户备注",
]

LEGACY_CSV_FIELDS = [
    "帖子发布日期",
    "平台",
    "标题",
    "标签",
    "一句话描述",  # pre-migration schema; kept only for backward-compatible import
    "推荐度",
    "判断理由",
    "链接",
    "用户备注",
]


def legacy_row_to_current(row: dict[str, str]) -> dict[str, str]:
    """Map the pre-migration Gamer520 schema without changing its meaning."""
    post_date = str(row.get("帖子发布日期") or "").strip()
    return {
        "收录日期": post_date,
        "收录来源": "gamer520",
        "Gamer520帖子日期": post_date,
        "来源链接": str(row.get("链接") or "").strip(),
        "平台": str(row.get("平台") or "").strip(),
        "标题": str(row.get("标题") or "").strip(),
        "标签": str(row.get("标签") or "").strip(),
        "游戏判断": str(row.get("一句话描述") or "").strip(),
        "推荐度": str(row.get("推荐度") or "").strip(),
        "判断理由": str(row.get("判断理由") or "").strip(),
        "用户备注": str(row.get("用户备注") or "").strip(),
    }

MODEL_FIELD_MAP: dict[str, str] = {
    "收录日期": "collected_date",
    "收录来源": "source",
    "Gamer520帖子日期": "gamer520_post_date",
    "来源链接": "source_url",
    "平台": "platform",
    "标题": "title",
    "标签": "tags",
    "游戏判断": "game_judgment",
    "推荐度": "score",
    "判断理由": "reasoning",
    "用户备注": "user_note",
}


def row_to_csv_dict(row: GameRow) -> dict[str, str]:
    return {
        "收录日期": row.collected_date.isoformat(),
        "收录来源": row.source,
        "Gamer520帖子日期": row.gamer520_post_date.isoformat() if row.gamer520_post_date else "",
        "来源链接": str(row.source_url) if row.source_url else "",
        "平台": row.platform,
        "标题": row.title,
        "标签": row.tags,
        "游戏判断": row.game_judgment,
        "推荐度": str(row.score),
        "判断理由": row.reasoning,
        "用户备注": row.user_note,
    }


def csv_dict_to_row(data: dict[str, str]) -> GameRow:
    raw: dict[str, str | int] = {}
    for csv_field, model_field in MODEL_FIELD_MAP.items():
        val = data.get(csv_field, "").strip()
        if model_field == "score":
            raw[model_field] = int(val) if val else 0
        elif model_field in ("gamer520_post_date", "source_url") and not val:
            raw[model_field] = None
        else:
            raw[model_field] = val
    return GameRow.model_validate(raw)
