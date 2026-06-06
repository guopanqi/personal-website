# Gamer520 游戏增量更新 Skill

## 目的
检查 Gamer520 PC PLAY 和 Switch 页面，根据用户维护的游戏口味基准，为新增条目生成简短标签、一句话描述、推荐分数和判断理由，把新条目加入数据中，并把找到的新游戏反馈给用户。

所有 CSV 操作优先通过 CLI 完成，不得手写追加、删除或排序 CSV 行。

## 固定来源
- **PC PLAY 列表页**：`https://www.gamer520.com/pcplay`
- **Switch 列表页**：`https://www.gamer520.com/gameswitch`
- **口味文件**：`游戏收集agent/taste.txt`
- **数据库**：`游戏收集agent/gamer520-games.csv`
- **CLI**：`游戏收集agent/gamer520_cli/`（基于 uv + typer）


### CSV 字段
| 字段 | 说明 |
|------|------|
| 发布日期 | 首次收录日期，`YYYY-MM-DD` |
| 平台 | `PC` / `Switch` / `PC/Switch`（跨平台合并一行） |
| 标题 | 去掉版本修饰，必要时补充英文名 |
| 标签 | 短词概括，用中文分号 `；` 分隔 |
| 一句话描述 | 基于详情页简介，避免凭标题猜测 |
| 推荐度 | `1`–`5` |
| 推荐标签 | 统一文字标签 |
| 判断理由 | 结合口味解释评分 |
| 链接 | 条目页链接，不放下载链接 |
| 用户备注 | 人工填写内容，新增默认留空；必须用中文全角标点（`，` 而非 `,`） |

输出 UTF-8 with BOM。表头固定以上顺序，不可新增/重命名字段。

## CLI 使用说明

CLI 项目在 `游戏收集agent/gamer520_cli/`，通过 uv 运行。从当前仓库根目录执行：

```bash
uv run --project 游戏收集agent/gamer520_cli gamer520 <command>
```

如果在 CLI 子目录内，可简写：

```bash
cd 游戏收集agent/gamer520_cli && uv run gamer520 <command>
```

### 可用命令

| 命令 | 用途 | 关键参数 |
|------|------|---------|
| `latest` | 查询 CSV 中最新发布日期和链接 ID | `--json` |
| `search` | 搜索标题（模糊匹配）、链接、备注 | `--title`、`--json`、`--limit`、`--csv` |
| `validate` | 校验 CSV 完整性和数据健康 | `--json` |
| `sort` | 按发布日期+链接ID降序排列 | `--dry-run` |
| `add` | 追加新增条目（stdin 或文件） | `--stdin`、`--dry-run`、`--json`、`--csv` |
| `remove` | 按标题精确删除条目 | `--title`、`--dry-run`、`--yes` |
| `export` | 按条件导出子集（AI 上下文） | `--latest`、`--days`、`--query`、`--platform`、`--format`、`--full` |

### 常用操作示例

查询最新日期：
```bash
uv run --project 游戏收集agent/gamer520_cli gamer520 latest
```

查重（写入前对候选条目运行）：
```bash
uv run --project 游戏收集agent/gamer520_cli gamer520 search --title "游戏标题" --json
```

导出最近 3 天上下文（供 AI 判断新增边界）：
```bash
uv run --project 游戏收集agent/gamer520_cli gamer520 export --days 3 --format jsonl
```

dry-run 预览新增：
```bash
printf '%s\n' '[{"发布日期":"2026-06-07","平台":"PC","标题":"...","标签":"...","一句话描述":"...","推荐度":"3","推荐标签":"可试","判断理由":"...","链接":"https://www.gamer520.com/123456.html","用户备注":""}]' | uv run --project 游戏收集agent/gamer520_cli gamer520 add --stdin --dry-run
```

真实写入：
```bash
printf '%s\n' '[...]' | uv run --project 游戏收集agent/gamer520_cli gamer520 add --stdin
```

删除误收录条目：
```bash
uv run --project 游戏收集agent/gamer520_cli gamer520 remove --title "精确标题" --dry-run
uv run --project 游戏收集agent/gamer520_cli gamer520 remove --title "精确标题" --yes
```

整体排序和校验：
```bash
uv run --project 游戏收集agent/gamer520_cli gamer520 sort
uv run --project 游戏收集agent/gamer520_cli gamer520 validate
```

## 每日更新的原则

### 规则
- 更新前读取 `taste.txt`，口味以磁盘文件为准。
- 更新前运行 `latest` 和 `validate`，确认数据库日期边界和健康状态。
- 不直接读取整份 CSV 做上下文判断；需要旧数据时用 `search` 或 `export` 获取局部信息。
- 新增通过 `add`，先 `--dry-run`，确认后再写入。
- 写入后运行 `sort` 和 `validate`。
- CSV schema 固定，不新增、不重命名字段。
- 严重问题（坏日期、坏分数、重复标题）先修复再继续。

### 信息判断
- 列表页信息用于发现候选和判断日期边界，标题可能不准确，是简称、旧名、缺英文名或发布者随手写的名字。
- 详情页通常会提供更加可靠的信息，标题、英文名、简介、Steam/商店链接、更新说明等都可以用于判断。外部链接或搜索不是固定步骤；当详情页信息不足、标题疑似别名、或是否重复不明确时，AI 可以自主查看额外来源。
- 最终写入的 `标题` 应以更可靠的信息为准，而不是机械照抄列表页标题。

- 以 `latest_date` 为主要边界，更新查找条目时不需要查找发布日期早于latest_date的条目。由于gamer520的列表页是按更新顺序排列的，通常早于 `latest_date` 的条目已经被处理过了。


- 查重: 可以使用`search --title` 进行候选检索工具，进行查重
```bash
uv run --project 游戏收集agent/gamer520_cli gamer520 search --title "候选标题" --json
```

- 写入: 新增条目通常优先用 JSON 文本通过 stdin 交给 CLI。

dry-run：
```bash
printf '%s\n' '[...JSON 数组...]' | uv run --project 游戏收集agent/gamer520_cli gamer520 add --stdin --dry-run
```

真实写入：
```bash
printf '%s\n' '[...JSON 数组...]' | uv run --project 游戏收集agent/gamer520_cli gamer520 add --stdin
```

收尾：
```bash
uv run --project 游戏收集agent/gamer520_cli gamer520 sort
uv run --project 游戏收集agent/gamer520_cli gamer520 validate
```

`add` 内部会自动执行：字段完整性校验、日期格式校验、推荐度范围校验、URL 非空/格式校验、链接重复检查（使用规范化比较，但保留原始链接）、标题重复检查。发现重复则拒绝写入并输出匹配行。

### 判断边界
- 不新增：新补丁、豪华版/正式版、标题微调、旧游戏重新上首页。
- 可新增：明确新作/续作、实质不同的重制版、大型独立资料片。
- 不确定时在回复中说明，不强行新增。
- 相对日期按 Asia/Singapore 转为具体日期；发布日期是首次收录日期，不覆盖旧条目的日期。
- 不要仅凭标题生成描述和评分；信息少则保守描述并注明。

### 输出摘要
简短说明：新增/跳过数量、总条目数、最值得注意的 3-6 款、降权原因。不罗列全部。

## 低频维护操作

- **误添加**：已通过 `remove` 进入 CLI。先用 `search --title` 模糊找候选，再复制确认后的完整标题调用 `remove --title --dry-run` → `remove --title --yes`
- **单条修改**（如修正评分、补备注）：暂不进入 CLI 命令面。由 AI 小范围编辑 CSV 后运行 `validate` 和 `sort` 兜底
- **PC/Switch 合并**：同上，手动编辑 CSV 后运行 `validate` 和 `sort`

后两项暂不进入 CLI 命令面，但完成后必须通过 CLI 验证。

## 标签写法
用短词让人一眼理解游戏是什么，避免长句和模糊词。
好：`旅途冒险；末日世界；递送；叙事`
不好：`冒险；有趣；好玩`

## 一句话描述写法
基于详情页，说明玩家扮演谁、做什么、核心情境/目标。控制在一句内，不堆砌系统。

## 用户口味基准
以 `游戏收集agent/taste.txt` 为准，每次更新前读取。

## 评分规则
| 分 | 标签 | 条件 | 说明 |
|----|------|------|------|
| 5 | 优先推荐 | 多个强匹配点：氛围、叙事、独特体验、探索推进、人物关系、资源取舍 | 非常符合口味 |
| 4 | 推荐 | 至少一项很强：故事/探索/生活感/策略压力/经营结构/形式新颖/氛围独特 | - |
| 3 | 可试 | 有贴合点但有明显限制：重复风险、过轻、过重、题材不贴合、战斗占比高 | 也可标注「研究可看」 |
| 2 | 不推荐 | 少量元素有用，或整体明显偏离口味 | 某方面极好则在学习参考中标注 |
| 1 | 非常不推荐 | 纯战斗/纯反应/重复刷/挂机/换皮/低辨识度/缺体验核心 | 同上 |

注意：1-2 分条目如果有精心设计的子系统（对话树、地图、UI、存档、任务追踪、场景叙事等），在回复「学习参考」中单独说明。

## 判断优先级
1. 有无明确体验核心？
2. 有无叙事、氛围或人物牵引？
3. 玩家是否会持续发现新内容？
4. 系统是否制造有意义的取舍？
5. 是否依赖重复、刷数值或高强度操作？
6. 即使不玩，是否值得设计参考？

表层标签（末日/赛博/西部等）≠高分，看体验结构。

## 最终回复格式
简短说明：有无新增、新增/跳过数量、总条目数、最值得注意的 3-6 款、降权原因。不罗列全部。

### 推荐摘要（≥3 分）
```
**[游戏名称]** ⭐⭐⭐⭐⭐/⭐⭐⭐⭐/⭐⭐⭐
- 推荐理由：xxx
- 链接：https://...
```

### 学习参考（低分但有亮点）
```
**[游戏名称]**（推荐度 X）
- 值得关注：xxx（具体说明哪个子系统或设计值得学习）
- 链接：https://...
```

每款单独一段。无则跳过对应节。
