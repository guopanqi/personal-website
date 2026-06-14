---
description: 抓取 Gamer520 PC/Switch 最新游戏列表，与口味基准对比，将新游戏写入 CSV 数据库并向用户推荐
allowed-tools: Bash, Read, Write, Agent
---

# Gamer520 游戏收藏数据库维护 Skill

## 目的

每天看看 Gamer520 PC PLAY 和 Switch 上架了什么新游戏，从中找出合口味的推荐给用户。

Gamer520 的列表页按更新时间排列，会把老游戏的更新补丁、重新上首页的旧条目和新游戏混在一起。为了能跳过已经看过的内容，我们维护了一个 CSV 数据库记录每款游戏的信息和评价。每次更新时，CSV 帮助判断哪些是真正的新游戏，避免重复评价同一款作品。

## 执行流程

### 第一步：确认边界

PC 和 Switch 分别查询，各自有独立的时间边界：

```bash
uv run --project 游戏收集agent/gamer520_cli gamer520 latest --json --platform PC
uv run --project 游戏收集agent/gamer520_cli gamer520 latest --json --platform Switch
uv run --project 游戏收集agent/gamer520_cli gamer520 validate
```

记录 `pc_latest_date`、`pc_latest_link_id`、`switch_latest_date`、`switch_latest_link_id`。

### 第二步：抓取列表（代替 WebFetch）

```bash
uv run --project 游戏收集agent/gamer520_cli gamer520 scrape-list https://www.gamer520.com/pcplay
uv run --project 游戏收集agent/gamer520_cli gamer520 scrape-list https://www.gamer520.com/gameswitch
```

每次调用返回紧凑 JSON（而非 ~200 行页面内容），格式：
```json
[{"title": "...", "url": "https://www.gamer520.com/NNNNN.html", "date": "2026-06-14", "date_text": "3小时前"}]
```

`date` 是从页面 `<time datetime="...">` 解析出的绝对日期，无需自行换算。

### 第三步：过滤新游戏 + 翻页判断

PC 和 Switch 各自用对应平台的边界日期过滤。

**过滤规则**（PC 用 `pc_latest_date`，Switch 用 `switch_latest_date`）：

- `date > platform_latest_date` → 候选新游戏，需确认是否已收录
- `date == platform_latest_date` → 用 `search` 确认（同一天可能既有新游戏也有已收录的老游戏更新）
- `date < platform_latest_date` → 肯定已过边界，跳过

**翻页判断**：

- 若当前页全部 `date < platform_latest_date` → 停止，不再翻页
- 若当前页有 `date >= platform_latest_date` 的条目 → 处理完后继续下一页

**查重**：对 `date >= platform_latest_date` 的候选，优先用 link_id（数字）搜索，更可靠：

```bash
uv run --project 游戏收集agent/gamer520_cli gamer520 search "115709" --json
# 或按标题
uv run --project 游戏收集agent/gamer520_cli gamer520 search --title "候选标题" --json
```

**正常情况下处理全部候选游戏。** 如候选数量异常巨大（超过 25 款），说明距上次更新已过去很久，先告知用户数量并征询是否全部处理，避免单轮上下文过重。

### 第四步：子代理抓取详情 + 评估

对每款确认的新游戏，用 `Agent` 工具启动子代理——即使只有 1 款也使用子代理，保持详情页内容不进入主对话上下文。多款时可并行启动。

**子代理 prompt 模板**（替换 `<URL>`、`<PLATFORM>`、`<TODAY>`、`<TASTE>`）：

---
你是一个游戏评估助手，任务完成后只返回一个 JSON 对象，不要其他文字，不要 markdown 代码块包裹。

运行命令获取游戏详情：
```
uv run --project 游戏收集agent/gamer520_cli gamer520 scrape-detail <URL>
```

根据以下口味基准评估：
```
<TASTE>
```

返回格式（严格按此结构，值均为字符串或数字，不要添加注释）：
```
{"发布日期":"<TODAY>","平台":"<PLATFORM>","标题":"游戏名（去掉版本/build修饰，必要时补充英文名）","标签":"标签1；标签2；标签3","一句话描述":"基于scrape-detail返回内容的一句话介绍，不要凭标题猜测","推荐度":3,"推荐标签":"可试","判断理由":"结合口味的评分理由","链接":"<URL>","用户备注":""}
```

字段说明：
- `发布日期`：今天的收录日期（`<TODAY>`），不是游戏官方发行日期
- `平台`：根据来源列表填写，PC PLAY → "PC"，Switch → "Switch"
- 评分标尺：5=优先推荐, 4=推荐, 3=可试, 2=不推荐, 1=非常不推荐
---

**主代理**在启动子代理前需要：
1. 读取 `游戏收集agent/taste.txt`（读取一次，粘贴进每个子代理 prompt 的 `<TASTE>` 位置）
2. 将 `<PLATFORM>` 填为 PC 或 Switch
3. 将 `<TODAY>` 填为今日日期 YYYY-MM-DD

子代理只做 `scrape-detail` + 评估，不读 CSV，不运行 add/sort/validate。

### 第五步：写入 + 收尾

收集所有子代理返回的 JSON 对象，用 **Write 工具**写入临时文件（避免 shell 转义问题，中文内容用 printf 管道会崩溃）：

```
Write /tmp/gamer520_new.json
[子代理返回的JSON对象组成的数组]
```

然后写入数据库：

```bash
# dry-run 预览
uv run --project 游戏收集agent/gamer520_cli gamer520 add --file /tmp/gamer520_new.json --dry-run

# 确认后写入
uv run --project 游戏收集agent/gamer520_cli gamer520 add --file /tmp/gamer520_new.json

# 收尾
uv run --project 游戏收集agent/gamer520_cli gamer520 sort
uv run --project 游戏收集agent/gamer520_cli gamer520 validate
```

### 第六步：向用户汇报

简短说明：新增/跳过数量、总条目数、最值得关注的游戏（附链接）及推荐理由。

---

## 游戏信息判断规则

- `scrape-detail` 返回的信息（发行日期、类型、描述）通常足够评估，不必额外 WebFetch。
- 如果 `scrape-detail` 描述过于简短或明显不准确，可以考虑额外查询，但成本较高，通常不必要。
- 不确定时在回复中说明，交给用户判断，不强行新增。

## 游戏评价判断参考

- **口味**：以磁盘 `taste.txt` 为准。
- **评分标尺**：5=优先推荐, 4=推荐, 3=可试, 2=不推荐, 1=非常不推荐。
- **输出摘要**：简短说明新增/跳过数量、总条目数、最值得注意的几款、推荐原因。可以推荐分数较高（比较符合口味的），也可以推荐即使整体分数不高但有独特亮点的。推荐游戏时必须附链接。

## 固定来源

- PC PLAY 列表：`gamer520 scrape-list https://www.gamer520.com/pcplay`
- Switch 列表：`gamer520 scrape-list https://www.gamer520.com/gameswitch`
- 口味文件：`游戏收集agent/taste.txt`
- 数据库：`游戏收集agent/gamer520-games.csv`
- CLI 项目：`游戏收集agent/gamer520_cli/`

## CSV 字段（固定 schema，不可新增/重命名字段）

| 字段 | 说明 |
|------|------|
| 发布日期 | `YYYY-MM-DD`，首次**收录**日期，不是游戏官方发行日期，不覆盖旧条目 |
| 平台 | `PC` / `Switch` / `PC/Switch` |
| 标题 | 去掉版本/build修饰，保留游戏名，必要时补充英文名 |
| 标签 | 中文分号 `；` 分隔 |
| 一句话描述 | 基于详情页，不要凭标题猜测 |
| 推荐度 | `1`–`5` |
| 推荐标签 | 固定取值：`优先推荐`/`推荐`/`可试`/`不推荐`/`非常不推荐` |
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
| `latest` | 查询最新发布日期和链接 ID | `--platform`、`--json` |
| `search` | 模糊搜索标题、链接、备注 | `--title`、`--json`、`--limit`、`--full` |
| `validate` | 校验 CSV 完整性和数据健康 | `--json` |
| `sort` | 按发布日期+链接ID降序排列 | `--dry-run` |
| `add` | 追加新增条目（stdin 或文件） | `--stdin`、`--file`、`--dry-run`、`--json` |
| `remove` | 按标题精确删除 | `--title`、`--dry-run`、`--yes` |
| `update` | 修改已有条目的字段 | `--title`、`--set`、`--dry-run`、`--yes`、`--json` |
| `export` | 按条件导出子集 | `--days`、`--latest`、`--query`、`--platform`、`--format`、`--full` |
| `scrape-list` | 抓取列表页 → `[{title,url,date,date_text}]` | `<url>` |
| `scrape-detail` | 抓取详情页 → `{title,release_date,genres,description}` | `<url>` |

### 使用规范

- 更新前运行 `latest --platform PC` 和 `latest --platform Switch`，分别确认两个平台的边界。
- `add` 写入前必须先 `--dry-run` 确认；写入用 `--file` 传 JSON 文件，避免 shell 转义问题。
- 写入后运行 `sort` 和 `validate`。
- 不直接读取整份 CSV 做上下文判断；需要旧数据时用 `search` 或 `export` 获取局部信息。
- `add` 内部自动拒绝重复链接和重复标题。

### 常用示例

```bash
# 初始化（分平台）
uv run --project 游戏收集agent/gamer520_cli gamer520 latest --json --platform PC
uv run --project 游戏收集agent/gamer520_cli gamer520 latest --json --platform Switch
uv run --project 游戏收集agent/gamer520_cli gamer520 validate

# 列表抓取
uv run --project 游戏收集agent/gamer520_cli gamer520 scrape-list https://www.gamer520.com/pcplay
uv run --project 游戏收集agent/gamer520_cli gamer520 scrape-list https://www.gamer520.com/gameswitch

# 查重（按 link_id 更可靠）
uv run --project 游戏收集agent/gamer520_cli gamer520 search "115709" --json
uv run --project 游戏收集agent/gamer520_cli gamer520 search --title "候选标题" --json

# 详情抓取（子代理内运行）
uv run --project 游戏收集agent/gamer520_cli gamer520 scrape-detail https://www.gamer520.com/NNNNN.html

# 写入（用 --file 避免 shell 转义）
uv run --project 游戏收集agent/gamer520_cli gamer520 add --file /tmp/gamer520_new.json --dry-run
uv run --project 游戏收集agent/gamer520_cli gamer520 add --file /tmp/gamer520_new.json

# 收尾
uv run --project 游戏收集agent/gamer520_cli gamer520 sort
uv run --project 游戏收集agent/gamer520_cli gamer520 validate

# 修改已有条目
uv run --project 游戏收集agent/gamer520_cli gamer520 update --title "舒适森林 Cozy Grove" --set "用户备注=玩过" --dry-run
uv run --project 游戏收集agent/gamer520_cli gamer520 update --title "舒适森林 Cozy Grove" --set "用户备注=玩过" --yes
```
