# Gamer520 游戏收藏数据库维护 Skill

## 目的

每天看看 Gamer520 PC PLAY 和 Switch 上架了什么新游戏，从中找出合口味的推荐给用户。

Gamer520 的列表页按更新时间排列，会把老游戏的更新补丁、重新上首页的旧条目和新游戏混在一起。为了能跳过已经看过的内容，我们维护了一个 CSV 数据库记录每款游戏的信息和评价。每次更新时，CSV 帮助判断哪些是真正的新游戏，避免重复评价同一款作品。

每次执行的流程是：`latest` 和 `search --title` 判断哪些是未收录的新游戏 → 打开详情页了解实际内容 → 按 `taste.txt` 口味基准生成评分、标签、描述和判断理由 → 写入 CSV → 把值得关注的游戏反馈给用户。

## 游戏信息判断规则

- 列表页标题可能不准确（简称、旧名、缺英文名、发布者随手写的名字）；标题最终以详情页可靠信息为准。
- 详情页信息不足时，可以自主查看 Steam/商店链接、外部搜索等额外来源做判断。
- `latest_date` 是主要边界，通常不需要翻阅早于它的列表页。
- 新补丁、豪华版/正式版、标题微调、旧游戏重新上首页 → 通常属于同一个游戏，不新增。
- 明确新作/续作、实质不同的重制版、大型独立资料片 → 通常视为不同游戏，可新增。
- 不确定时在回复中说明，交给用户判断，不强行新增。

## 游戏评价判断参考

- **口味**：以磁盘 `taste.txt` 为准。
- **评分标尺**：5=优先推荐，4=推荐，3=可试，2=不推荐，1=非常不推荐。
- **输出摘要**：简短说明新增/跳过数量、总条目数、最值得注意的几款、推荐原因。可以推荐分数较高（比较符合口味的），也可以即使整体分数不高，但是有独特亮点，或者某个点很合口味的。



## 固定来源
- **PC PLAY 列表页**：`https://www.gamer520.com/pcplay`
- **Switch 列表页**：`https://www.gamer520.com/gameswitch`
- **口味文件**：`游戏收集agent/taste.txt`
- **数据库**：`游戏收集agent/gamer520-games.csv`
- **CLI 项目**：`游戏收集agent/gamer520_cli/`

## CSV 字段（固定 schema，不可新增/重命名字段）

| 字段 | 说明 |
|------|------|
| 发布日期 | `YYYY-MM-DD`，首次收录日期，不覆盖旧条目 |
| 平台 | `PC` / `Switch` / `PC/Switch` |
| 标题 | 去掉版本修饰，必要时补充英文名 |
| 标签 | 中文分号 `；` 分隔 |
| 一句话描述 | 基于详情页，不要凭标题猜测 |
| 推荐度 | `1`–`5` |
| 推荐标签 | 统一文字标签 |
| 判断理由 | 结合口味解释评分 |
| 链接 | 条目页 URL |
| 用户备注 | 新增默认留空 |

编码 UTF-8 with BOM，字段顺序固定。

## CLI 使用说明

CLI 项目在 `游戏收集agent/gamer520_cli/`，所有 CSV 操作必须通过它完成，不得手写修改 CSV 行。

从项目根目录运行：
```bash
uv run --project 游戏收集agent/gamer520_cli gamer520 <command>
```

### 命令一览

| 命令 | 用途 | 关键参数 |
|------|------|---------|
| `latest` | 查询最新发布日期和链接 ID | `--json` |
| `search` | 模糊搜索标题、链接、备注 | `--title`、`--json`、`--limit` |
| `validate` | 校验 CSV 完整性和数据健康 | `--json` |
| `sort` | 按发布日期+链接ID降序排列 | `--dry-run` |
| `add` | 追加新增条目（stdin 或文件） | `--stdin`、`--dry-run`、`--json` |
| `remove` | 按标题精确删除 | `--title`、`--dry-run`、`--yes` |
| `export` | 按条件导出子集 | `--days`、`--latest`、`--query`、`--platform`、`--format`、`--full` |

### 使用规范

- 更新前运行 `latest` 和 `validate`，确认数据库边界和健康状态。
- `add` 写入前必须先 `--dry-run` 确认。
- 写入后运行 `sort` 和 `validate`。
- 不直接读取整份 CSV 做上下文判断；需要旧数据时用 `search` 或 `export` 获取局部信息。
- `add` 内部自动拒绝重复链接和重复标题；`remove` 删除后自动校验剩余 CSV。
- 单条修改或 PC/Switch 合并暂不进入 CLI，手动编辑 CSV 后运行 `sort` + `validate` 兜底。

### 常用示例

```bash
# 查最新日期 + 校验
uv run --project 游戏收集agent/gamer520_cli gamer520 latest
uv run --project 游戏收集agent/gamer520_cli gamer520 validate

# 查重
uv run --project 游戏收集agent/gamer520_cli gamer520 search --title "候选标题" --json

# 导出最近 3 天上下文
uv run --project 游戏收集agent/gamer520_cli gamer520 export --days 3 --format jsonl

# dry-run → 写入
printf '%s\n' '[...JSON数组...]' | uv run --project 游戏收集agent/gamer520_cli gamer520 add --stdin --dry-run
printf '%s\n' '[...JSON数组...]' | uv run --project 游戏收集agent/gamer520_cli gamer520 add --stdin

# 收尾
uv run --project 游戏收集agent/gamer520_cli gamer520 sort
uv run --project 游戏收集agent/gamer520_cli gamer520 validate

# 删除误收录
uv run --project 游戏收集agent/gamer520_cli gamer520 remove --title "精确标题" --dry-run
uv run --project 游戏收集agent/gamer520_cli gamer520 remove --title "精确标题" --yes
```
