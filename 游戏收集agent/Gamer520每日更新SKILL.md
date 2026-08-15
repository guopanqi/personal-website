---
name: gamer520-daily-update
description: 抓取 Gamer520 PC/Switch 最新游戏列表，与口味基准对比，将新游戏写入数据库并向用户推荐
allowed-tools: Bash, Read, Agent, WebSearch, WebFetch
triggers:
  - "更新一下"
  - "daily update"
  - "今天有更新吗"
  - "今日更新"
---

# Gamer520 每日更新 Skill

触发后直接执行，不询问是否开始。CLI 参考见 `游戏收集agent/gamer520_cli/README.md`。

## 运行环境

所有命令通过项目自带的可执行脚本调用，**不要**使用 `uv run --project ... gamer520 ...`：

```bash
游戏收集agent/gamer520_cli/gamer520 <子命令> [参数...]
```

脚本复用项目里已装好依赖的 `.venv`，不经过 `uv sync`（沙箱里 `uv sync` 需要的 wheel 下载被限速，且 `.venv/bin/python3` 在 Linux 下打不开）；只在必要时联网下载一次 Python 3.12 解释器，冷启动约 20 秒，之后每条命令约 1 秒。完整原因见 `游戏收集agent/gamer520_cli/README.md`。

如果脚本报错找不到 `.venv` 或 `src`，说明依赖损坏，需要在有正常网络的机器上运行 `uv sync --project 游戏收集agent/gamer520_cli` 重建，Skill 本身不负责重建依赖。

## 职责与约束

- CLI 负责确定性操作；本 Skill 负责编排；Agent 负责“是否同一游戏”和推荐度等语义判断。
- 通过 CLI 获取数据库状态，不直接读取整份 `gamer520-games.csv`。口味只读 `游戏收集agent/taste.txt`。
- 命令输出直接在 Agent 上下文中处理，不创建中转目录或临时 CSV/JSON，不将输出落盘后再读取或过滤。
- scraper 返回的 `title` 已规范化，不再自行截断标题，也不删除 `+`、数字或版本词。
- 非游戏内容不得进入数据库。列表抓取器应直接排除公告、置顶通知、工具/资源页等站点内容；若详情阶段仍发现候选不是独立游戏，必须标记为跳过，不评分、不生成 `add` 输入。
- `complete: false`、数据库校验失败或任一 dry-run 失败时，禁止写入。
- taste.txt 的修改必须由 Agent 执行，但只能在用户明确同意后才能写入。Agent 可以基于用户反馈提出具体的修改建议（连同触发证据一起说明），未获同意前只停留在建议阶段，不得写入。

## 流程

### 1. 预检与扫描

读取一次 `taste.txt`，然后运行：

```bash
游戏收集agent/gamer520_cli/gamer520 validate
游戏收集agent/gamer520_cli/gamer520 doctor --json
游戏收集agent/gamer520_cli/gamer520 scan-updates --platform all
```

`scan-updates` 自动推导两个平台的边界、分页抓取并分类。结果必须 `complete: true`；否则提高 `--max-pages` 重跑。仅排障时使用 `--debug`。

候选处理规则：

| 输出 | 处理 |
|---|---|
| `platforms.*.summary.existing/before_boundary` | CLI 已跳过，默认不返回具体条目 |
| `platforms.*.platform_merges` | Agent 确认后将已有记录更新为 `PC/Switch` |
| `platforms.*.new` | 抓详情、评估并准备新增 |
| `platforms.*.ambiguous` | Agent 判断同一或不同游戏，再决定跳过、更新或新增 |
| `cross_platform_candidates` | CLI 用标题/URL 确定性归组；Agent确认后生成一条 `PC/Switch` 记录 |
| Doctor `unresolved_candidates` | Agent 复核并记录结论 |

同一新游戏只生成一条 `PC/Switch` 记录。`summary.scanned_items` 是边界内扫描总量，包含已有条目；不得称为候选数。真实待处理数使用 `summary.unique_actionable_candidates`（单平台时使用 `summary.actionable_candidates`）。只有真实待处理数超过 50 时，才先告知用户再继续。

### 2. 语义裁决

对 `ambiguous` 和 Doctor 未决组使用同一判断阶梯：

1. 比较规范标题、英文名、系列编号、平台、描述和链接。
2. 仍不确定时，对相关链接运行 `scrape-detail`。
3. 仍不确定时联网查 Steam、官网或发行商等一手来源。
4. 确认不同：`doctor-review --decision distinct`；确认相同：`doctor-review --decision same`，并准备通用 `update/remove` 操作。
5. 仍无法判断才交给用户；不得写复核结论或修改相关数据。

明确的续作或不同系列编号通常是 `distinct`。合并数据时保留有效标题、平台、评分理由和用户备注；平台组合统一为 `PC/Switch`。所有 `doctor-review` 也要先 `--dry-run`。

### 3. 详情与评估

对每个确定的新游戏运行：

```bash
游戏收集agent/gamer520_cli/gamer520 scrape-detail <URL>
```

语义评估默认由主代理直接判断，无需启动子代理；候选数量很多时可以用子代理并行加速抓详情和评估，一般情况没必要。主代理结合每个候选对应的 `scrape-detail` 详情和完整 `taste.txt` 生成详情标题和语义评估，每条评估必须能追溯到对应候选的详情证据：

```json
{"title":"<scrape-detail title>","assessment":{"tags":["标签1","标签2"],"description":"基于详情的介绍","score":3,"reason":"结合口味的理由"}}
```

详情返回后先做内容类型门禁：只有能够确认是独立游戏作品的候选才进入评分。公告、置顶通知、下载说明、修改器/补丁/固件/插件、资源合集、站务文章等统一跳过；不得为了满足 1–5 分字段而给非游戏内容打 1 分。最终核对时，所有扫描候选都必须明确归入 `已有 / 合并 / 新增 / 非游戏跳过 / 未决` 之一，避免裁决后漏项。`ambiguous` 判为 `distinct` 后必须转入新增详情评估，不能只写 `doctor-review`。写入前必须核对数量守恒：`唯一待处理数 = 合并 + 新增 + 非游戏跳过 + 未决`；等式不成立时禁止写入。

主代理将扫描结果中的 `date/platform/url`、返回的详情标题和 `assessment` 组合为 `add` 输入：

```json
{"source":{"date":"<列表页 date>","platform":"<PC|Switch|PC/Switch>","title":"<详情标题>","url":"<URL>"},"assessment":{...}}
```

评估规则：

评分只回答一个问题：这款游戏值不值得用户点开细看。它是过滤器，不是精确排序。口味依据全部来自 `taste.txt`，本节只定义怎么把口味换算成分数，两边不重复写口味内容。

判断顺序：先认主循环（玩家大部分时间实际在做什么，看玩法本身而不是标签、题材或宣传语），再看辅助元素。Roguelite、时间压力、重复循环、战斗如果只是用来组织进程或支撑经营取舍，记为风险即可，不算命中；判断办法是把这个元素拿掉，剩下的还成立就是辅助。只有实际占据主循环时才算命中。

- 主循环命中 `taste.txt` 的“我不喜欢的”或负面判例：给 1–2 分，不因其他优点拉高，并在 `reason` 里写明命中哪一条。整个主循环都是雷区且没有任何独立吸引力时给 1 分。
- 5 分：故事、探索、生活感、经营取舍、制度压力、形式或氛围里至少一项强到让人想立刻打开。不要吝啬——一批几十款里一个 5 分都没有，通常说明标准跑偏了，而不是这批都平庸。
- 4 分：有一个明确成立的强项，`reason` 要指名具体的系统、叙事或形式；说不出具体的就不是 4 分。
- 3 分：有明确贴合点，同时有说得出的局限，两样都要写进 `reason`；只写得出一样说明还没看清，按信息不足处理。
- 信息不足：看不出主循环、题材或核心机制时不要猜。`tags` 加入 `信息不足`，在汇报中单列交用户审查。`推荐度` 字段必填 1–5，此时按已知信息保守给，但这个分数不代表判断结论，也不得用 3 分兜底。
- 写不出具体理由说明还没看懂这款游戏，此时不要用模板句填充 `description` 或 `reason`，按信息不足处理。
- `description_quality` 为 `limited/missing` 时，打开该 gamer520 详情页原始页面（看文本或截图）补充调查；仍看不清主循环时才按信息不足处理并注明不确定性。帖子日期必须使用列表页 `date`，不是游戏发行日期。

### 4. 统一写入

先整理本轮全部 `doctor-review/update/remove/add` 操作，对每项执行 dry-run。全部成功后才正式执行：`doctor-review/update/remove` 将 `--dry-run` 替换为 `--yes`，`add` 移除 `--dry-run`。不得边预检边写入。

```bash
游戏收集agent/gamer520_cli/gamer520 update --title "游戏标题" --set "平台=PC/Switch" --dry-run
游戏收集agent/gamer520_cli/gamer520 remove --title "重复记录" --dry-run
游戏收集agent/gamer520_cli/gamer520 add --stdin --dry-run << 'ENDOFDATA'
[{...}]
ENDOFDATA
```

正式写入后运行：

```bash
游戏收集agent/gamer520_cli/gamer520 sort
游戏收集agent/gamer520_cli/gamer520 validate
游戏收集agent/gamer520_cli/gamer520 doctor --json
```

最终必须 validate 通过，Doctor 无完全重复和未处理的相似候选。

### 5. 汇报

首行写：`今天新增 X 款（PC Y / Switch Z）`；有跨平台更新时补充数量。

随后只汇报 3 分及以上游戏；低于 3 分但特色鲜明的也可列出。汇报顺序必须按评分从高到低排列；同评分时保持扫描结果中的稳定顺序。每款必须单独一行，并严格包含以下四项：

`游戏名称｜推荐语｜评分：X/5｜链接`

其中：

- `游戏名称` 使用详情抓取返回的规范标题。
- `推荐语` 根据评估 `reason` 改写为面向用户的简短推荐说明，不能只写标签或重复评分。
- `评分` 必须明确写成 `X/5`，使用 1–5 分评估结果。
- `链接` 必须是对应 Gamer520 详情页的完整 Markdown 链接，格式为 `[游戏名称](URL)`。

示例：

`太阳港 Sun Haven｜农场经营、生活模拟、城镇关系和探索都高度贴合口味，优先推荐。｜评分：5/5｜[详情](https://www.gamer520.com/57477.html)`

正文之后，若本轮有 `信息不足` 标记的游戏，另起一节写 `信息不足，待你判断：`，每款一行 `游戏名称｜看不清的是什么｜链接`，不写评分。这一节不计入正文推荐数量。

新增数为 0 时，首行已说明情况，不再补写”今天都不太推荐”，正文到此为止。仅当本轮确实新增了游戏、但均不足 3 分（或无特色可列）时，才写”今天都不太推荐”。不写操作日志、过程说明或客套结束语。

### 6. 口味反馈复盘

触发时机：用户对已入库游戏给出评价、备注或事后补充观后感时——无论是紧跟当次汇报，还是过了几天回来补充”这个我玩了/wishlist 后又看了一眼，感觉如何”——都把这轮反馈和当初写入的评分理由做一次对照。

判断标准：
- 反馈与当初的评分理由一致，只是确认 → 不用改 taste.txt，正常回应即可。
- 反馈明显偏离评分理由（例如某个元素被当作”新颖/例外”加了分，但用户实际反感；或者某类描述用户格外买账，taste.txt 却没覆盖）→ 提炼成一条具体、可执行的 taste.txt 修改建议，说明触发证据（哪款游戏、原评分理由 vs 用户反馈的落差），报给用户定夺。不要每条反馈都强行找出一个”建议”，没有明显信号就不提。

权限边界：修改动作由 Agent 来做，但必须先在对话中提出建议、拿到用户明确同意（用户也可以要求调整措辞）后才能写入；未获同意前不得改动 taste.txt。用户当次选择不加或没回应，不代表以后不能再提，但同一个信号不要反复刷屏。

自动化场景（定时任务、用户不在场）：如果扫描或写入过程中发现近期新增的”用户备注”里有信息量大的评价（明确喜欢/讨厌，或备注内容与当初评分理由存在落差），在”汇报”末尾追加一小节”口味观察”，列出建议但不写入 taste.txt，留到下次人机对话时由用户确认。
