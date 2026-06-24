---
description: 抓取 Gamer520 PC/Switch 最新游戏列表，与口味基准对比，将新游戏写入数据库并向用户推荐
allowed-tools: Bash, Read, Agent
triggers:
  - "更新一下"
  - "daily update"
  - "今天有更新吗"
  - "今日更新"
---

# Gamer520 每日更新 Skill

用户说"更新一下"、"daily update"、"今天有更新吗"或"今日更新"时，直接执行本流程，不要问"要不要更新"。

> CLI 命令完整参考见 `游戏收集agent/gamer520-cli-SKILL.md`。

## 背景与原则

Gamer520 的列表页按更新时间排列，会把补丁更新、重新上首页的旧条目和新游戏混在一起。我们用数据库记录每款游戏的收录结果，每次更新时以"帖子发布日期"为边界，跳过已处理过的内容，避免重复评价。

**来源**

- PC PLAY 列表：`https://www.gamer520.com/pcplay`
- Switch 列表：`https://www.gamer520.com/gameswitch`
- 口味文件：`游戏收集agent/taste.txt`

**评估原则**

- `scrape-detail` 返回的详细信息通常够了，不必额外 WebFetch；内容明显不足时可酌情补充，但成本较高。
- 不确定时在回复中说明，交给用户判断，不强行新增。
- 口味以 `taste.txt` 为准；评分 1–5，对应"非常不推荐"到"优先推荐"。
- 最终在总结中, 提及值得关注的游戏时, 记得附上链接!

## 执行流程

### 第一步：确认边界

PC 和 Switch 各自有独立的时间边界：

```bash
uv run --project 游戏收集agent/gamer520_cli gamer520 latest --json --platform PC
uv run --project 游戏收集agent/gamer520_cli gamer520 latest --json --platform Switch
uv run --project 游戏收集agent/gamer520_cli gamer520 validate
```

记录 `pc_latest_date`、`pc_latest_link_id`、`switch_latest_date`、`switch_latest_link_id`。

### 第二步：抓取列表

```bash
uv run --project 游戏收集agent/gamer520_cli gamer520 scrape-list https://www.gamer520.com/pcplay
uv run --project 游戏收集agent/gamer520_cli gamer520 scrape-list https://www.gamer520.com/gameswitch
```

返回格式：`[{"title": "...", "url": "...", "date": "2026-06-14", "date_text": "3小时前"}]`

`date` 是从页面 `<time datetime="...">` 解析出的绝对日期，无需换算。

### 第三步：过滤新游戏 + 翻页判断

PC 和 Switch 各自用对应平台的 `latest_date` 过滤。

**过滤规则**：

- `date > platform_latest_date` → 候选，需确认是否已收录
- `date == platform_latest_date` → 用 `search` 确认（同一天可能有新旧混合）
- `date < platform_latest_date` → 已过边界，跳过

**翻页**：当前页所有条目均 `date < platform_latest_date` → 停止；否则处理完继续下一页。

**查重与跨平台合并**：

0. 本轮对话中已知在数据库里的游戏直接跳过，无需再次搜索。

1. 搜索（子串匹配，标题关键词或链接均可）：
```bash
uv run --project 游戏收集agent/gamer520_cli gamer520 search "候选标题关键词" --json
```
- 无结果 → 新游戏，进入第四步
- 找到，平台已包含当前来源 → 跳过
- 找到，平台不包含当前来源 → 标记**跨平台合并候选**，第五步用 `update` 合并

> 列表页标题可能与详情页标题略有出入——`add` 内部自动拒绝重复链接，是最终安全网。`scrape-detail` 返回的 `title` 才是写入数据库的准确值。

合并规则：任意平台组合 → `PC/Switch`。

**数量**：正常处理全部候选。超过 25 款时先告知用户再处理。

### 第四步：子代理抓取详情 + 评估

对每款新游戏启动子代理，多款时可并行。

**子代理 prompt 模板**（替换 `<URL>`、`<PLATFORM>`、`<FORUM_DATE>`、`<TASTE>`）：

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
{"帖子发布日期":"<FORUM_DATE>","平台":"<PLATFORM>","标题":"游戏名（去掉版本/build修饰，必要时补充英文名）","标签":"标签1；标签2；标签3","一句话描述":"基于scrape-detail返回内容的一句话介绍，不要凭标题猜测","推荐度":3,"推荐标签":"可试","判断理由":"结合口味的评分理由","链接":"<URL>","用户备注":""}
```

字段说明：
- `帖子发布日期`：直接填 `<FORUM_DATE>`（主代理已替换好的论坛帖子日期）；不要用 scrape-detail 返回的 `game_release_date`，那是游戏官方发行日期，与本字段无关
- `平台`：PC PLAY 来源 → "PC"，Switch 来源 → "Switch"
- `推荐标签` 只能是：`非常不推荐` / `不推荐` / `可试` / `推荐` / `优先推荐`，与 `推荐度` 1–5 严格对应
---

**主代理在启动子代理前需要**：
1. 读取 `游戏收集agent/taste.txt`，粘贴进 `<TASTE>`
2. 将 `<PLATFORM>` 填为 PC 或 Switch
3. 将 `<FORUM_DATE>` 填为该游戏在 scrape-list 结果中的 `date` 值（YYYY-MM-DD）

子代理只做 `scrape-detail` + 评估，不读数据库，不运行 add/sort/validate。

### 第五步：写入 + 收尾

**5a. 跨平台合并**（先执行）：

```bash
uv run --project 游戏收集agent/gamer520_cli gamer520 update --title "游戏标题" --set "平台=PC/Switch" --dry-run
uv run --project 游戏收集agent/gamer520_cli gamer520 update --title "游戏标题" --set "平台=PC/Switch" --yes
```

**5b. 新增条目**（heredoc 传 stdin，无需临时文件）：

```bash
uv run --project 游戏收集agent/gamer520_cli gamer520 add --stdin --dry-run << 'ENDOFDATA'
[{子代理返回的JSON对象...}]
ENDOFDATA

uv run --project 游戏收集agent/gamer520_cli gamer520 add --stdin << 'ENDOFDATA'
[{子代理返回的JSON对象...}]
ENDOFDATA

uv run --project 游戏收集agent/gamer520_cli gamer520 sort
uv run --project 游戏收集agent/gamer520_cli gamer520 validate
```

### 第六步：向用户汇报

用自然语言回复，格式如下：

```
今天新增 X 款（PC Y / Switch Z）。

《标题》值得玩，[一句理由]，评分 N 链接
《标题》可以试试，[一句理由]，评分 N 链接
```

**规则**：
- 第一行：总数和平台分布；有跨平台合并时加"合并跨平台 N 款"
- 值得关注的游戏每款一行，必须附链接；"值得关注"不只看评分，有鲜明特点或某个点特别符合口味的也列出来
- 无值得关注 → 第一行之后写一句"今天都不太推荐"
- 不写操作日志，不写客套结束语
