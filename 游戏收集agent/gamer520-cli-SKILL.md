---
description: Gamer520 游戏数据库 CLI 使用参考——命令、CSV schema、操作规范和示例
allowed-tools: Bash
---

# Gamer520 CLI 参考

## 项目概览

`gamer520_cli` 是管理 `gamer520-games.csv` 的命令行工具。所有对数据库的读写操作都应通过它完成，不要手写修改 CSV 行。

```bash
# 从项目根目录调用
uv run --project 游戏收集agent/gamer520_cli gamer520 <command>
```

**路径**

| 名称 | 路径 |
|------|------|
| 数据库 | `游戏收集agent/gamer520-games.csv` |
| 口味文件 | `游戏收集agent/taste.txt` |
| CLI 项目 | `游戏收集agent/gamer520_cli/` |

## CSV 字段（固定 schema，不可新增/重命名）

| 字段 | 类型 | 说明 |
|------|------|------|
| 帖子发布日期 | `YYYY-MM-DD` | gamer520 论坛帖子发布日期，从 `scrape-list` 的 `date` 字段取得；不是游戏官方发行日期，不覆盖旧条目 |
| 平台 | `PC` / `Switch` / `PC/Switch` | |
| 标题 | string | 去掉版本/build 修饰，保留游戏名，必要时补充英文名 |
| 标签 | string | 中文分号 `；` 分隔 |
| 一句话描述 | string | 基于详情页内容，不要凭标题猜测 |
| 推荐度 | `1`–`5` | |
| 推荐标签 | string | 固定取值：`优先推荐` / `推荐` / `可试` / `不推荐` / `非常不推荐` |
| 判断理由 | string | 结合口味解释评分 |
| 链接 | URL | gamer520 条目页，如 `https://www.gamer520.com/NNNNN.html` |
| 用户备注 | string | 新增默认留空 |

编码 UTF-8 with BOM，字段顺序固定。

## 命令一览

| 命令 | 用途 | 关键参数 |
|------|------|---------|
| `latest` | 返回最新帖子发布日期和最大 link_id | `--platform PC\|Switch`、`--json` |
| `search` | 全字段子串匹配；`--field` 限定单列 | `--field 字段名`、`--json`、`--limit`、`--full` |
| `validate` | 校验 CSV 完整性和数据健康 | `--json` |
| `sort` | 按帖子发布日期降序、同日期按 link_id 降序排列 | `--dry-run` |
| `add` | 追加新条目（JSON 数组） | `--stdin`、`--file`、`--dry-run`、`--json` |
| `remove` | 按标题精确删除 | `--title`、`--dry-run`、`--yes` |
| `update` | 修改已有条目的字段 | `--title`、`--set KEY=VALUE`、`--dry-run`、`--yes` |
| `export` | 按条件导出子集 | `--days`、`--latest`、`--query`、`--platform`、`--format json\|jsonl\|csv\|md`、`--full` |
| `scrape-list` | 抓取列表页 → `[{title, url, date, date_text}]` | `<url>` |
| `scrape-detail` | 抓取详情页 → `{title, game_release_date, genres, description}` | `<url>` |

**`scrape-detail` 返回字段说明**：`game_release_date` 是游戏官方发行日期（非帖子日期）；`description` 最长约 1500 字，已去除下载/系统需求等无关内容。

## 操作规范

- 写入前必须先 `--dry-run` 确认；`add` 用 heredoc 传 `--stdin`（避免中文 shell 转义问题）
- 写入后运行 `sort` 和 `validate`
- 不直接读取整份 CSV；需要局部数据用 `search` 或 `export`
- `add` 内部自动拒绝重复链接和重复标题

## 常用示例

```bash
# 查询边界（两平台各自独立）
uv run --project 游戏收集agent/gamer520_cli gamer520 latest --json --platform PC
uv run --project 游戏收集agent/gamer520_cli gamer520 latest --json --platform Switch

# 健康检查
uv run --project 游戏收集agent/gamer520_cli gamer520 validate

# 列表抓取
uv run --project 游戏收集agent/gamer520_cli gamer520 scrape-list https://www.gamer520.com/pcplay
uv run --project 游戏收集agent/gamer520_cli gamer520 scrape-list https://www.gamer520.com/gameswitch

# 搜索（标题关键词 / 链接 / 任意字段）
uv run --project 游戏收集agent/gamer520_cli gamer520 search "关键词" --json
uv run --project 游戏收集agent/gamer520_cli gamer520 search "优先推荐" --field 推荐标签 --json

# 详情抓取
uv run --project 游戏收集agent/gamer520_cli gamer520 scrape-detail https://www.gamer520.com/NNNNN.html

# 写入新条目（heredoc 传 stdin）
uv run --project 游戏收集agent/gamer520_cli gamer520 add --stdin --dry-run << 'ENDOFDATA'
[{"帖子发布日期":"2026-06-14","平台":"PC","标题":"游戏名","标签":"标签1；标签2","一句话描述":"...","推荐度":3,"推荐标签":"可试","判断理由":"...","链接":"https://www.gamer520.com/NNNNN.html","用户备注":""}]
ENDOFDATA

# 修改字段
uv run --project 游戏收集agent/gamer520_cli gamer520 update --title "游戏名" --set "用户备注=玩过" --dry-run
uv run --project 游戏收集agent/gamer520_cli gamer520 update --title "游戏名" --set "用户备注=玩过" --yes

# 导出最近 7 天
uv run --project 游戏收集agent/gamer520_cli gamer520 export --days 7 --json

# 收尾
uv run --project 游戏收集agent/gamer520_cli gamer520 sort
uv run --project 游戏收集agent/gamer520_cli gamer520 validate
```
