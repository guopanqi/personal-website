# Gamer520 CSV CLI 工程文档

## 目标

用 `uv` 建一个轻量 Python CLI，把 Gamer520 游戏 CSV 的确定性操作脚本化，同时保留 AI 对数据的判断和人工可编辑性。

这个项目不把 CSV 立刻迁移成数据库。当前 `gamer520-games.csv` 仍然是唯一主数据源，CLI 负责：

- 查询最新日期、搜索条目、局部导出上下文
- 检查链接和标题重复
- 追加新增条目
- 按标题删除误收录条目
- 排序、校验、保留 UTF-8 with BOM

AI 仍然负责：

- 阅读详情页并理解游戏内容
- 标题中的版本和噪音
- 生成标签、一句话描述、推荐度和判断理由
- 判断模糊重复、版本差异、重制版/资料片是否应独立收录
- 处理 PC/Switch 合并、单条修改等低频维护操作；v1 由 AI 小范围编辑 CSV 后运行 `validate` 和 `sort` 兜底，只有高频发生时再考虑新增命令

## 非目标

- 第一阶段不引入 SQLite、DuckDB、Postgres 等数据库。
- 不做完整爬虫调度系统。
- 不自动下载游戏资源。
- 不让脚本替代 AI 的内容判断。
- 不把流程做成只能每日更新的固定管线，CLI 必须支持临时查询、修正和人工介入。

## 推荐目录结构

```text
游戏收集agent/
  gamer520-daily-update-SKILL.md
  gamer520-games.csv
  taste.txt
  gamer520-cli-engineering.md
  gamer520_cli/
    pyproject.toml
    README.md
    src/
      gamer520_cli/
        __init__.py
        __main__.py
        cli.py
        config.py
        csv_store.py
        models.py
        normalize.py
        operations.py
        render.py
    tests/
      test_normalize.py
      test_csv_store.py
      test_operations.py
```

第一阶段也可以把包放在根目录下：

```text
游戏收集agent/
  pyproject.toml
  src/gamer520_cli/
```

但推荐使用 `游戏收集agent/gamer520_cli/` 子项目，避免和 Astro 网站工程的 Node 配置混在一起。

## uv 项目初始化

在 `游戏收集agent` 下执行：

```bash
uv init gamer520_cli --package --python 3.12
cd gamer520_cli
uv add typer rich pydantic
uv add --dev pytest
```

依赖建议：

- `typer`：构建 CLI 命令。
- `rich`：漂亮地输出表格、警告和校验结果。
- `pydantic`：定义 CSV 行模型和输入 JSON 模型。
- `pytest`：测试规范化、读写和去重逻辑。

`pyproject.toml` 入口建议：

```toml
[project.scripts]
gamer520 = "gamer520_cli.cli:app"
```

运行方式：

```bash
uv run gamer520 latest
uv run gamer520 validate
uv run gamer520 search "星露谷"
```

如果当前目录不在 CLI 子项目：

```bash
uv run --project 游戏收集agent/gamer520_cli gamer520 latest
```

## 数据源约定

默认路径：

```text
游戏收集agent/gamer520-games.csv
游戏收集agent/taste.txt
```

CLI 应支持显式传参：

```bash
uv run gamer520 validate --csv ../gamer520-games.csv
uv run gamer520 latest --csv ../gamer520-games.csv
```

默认 CSV 字段顺序：

```text
发布日期
平台
标题
标签
一句话描述
推荐度
推荐标签
判断理由
链接
用户备注
```

字段说明：

- `标题` 存储最终用于检索、展示和判断的标题。
- 旧字段 `Gamer520标题` 不再保留在主 CSV 中。原始标题只用于当次抓取和 AI 判断，不进入长期数据库。
- 旧字段 `清理后标题` 迁移为 `标题`。
- 旧字段 `推荐度0-5` 迁移为 `推荐度`。
- `推荐度` 合法值为 `1` 到 `5`。如未来确实需要 `0`，应先修改 `taste.txt`、Skill 和校验规则，再做一次显式迁移。

写回规则：

- 读取时兼容 UTF-8 with BOM。
- 写入时始终使用 UTF-8 with BOM。
- 字段顺序固定。
- 未识别的额外字段第一阶段可以报错，避免无声丢数据。
- 如果旧 CSV 最后一列无标题但有内容，应命名为 `用户备注`。
- 任何写入命令默认先生成 diff 摘要或支持 `--dry-run`。
- CSV 读写使用 Python 标准库 `csv.DictReader` / `csv.DictWriter`，不引入 pandas。这个数据规模不需要 DataFrame，标准库更利于保留字段顺序、BOM 和精确写回语义。

## Schema 迁移

这次字段调整应在正式实现 CLI 前完成。原因是：

- CLI 的 `models.py`、`validate`、`add`、`export` 都依赖字段名。
- 如果先按旧表头实现，再改表头，会产生一轮无意义返工。
- 当前 CSV 只有几百行，迁移成本低，适合先把数据源整理干净。

迁移目标：

```text
旧字段 Gamer520标题 -> 删除
旧字段 清理后标题 -> 新字段 标题
旧字段 推荐度0-5 -> 新字段 推荐度
```

迁移规则：

- `标题` 优先取旧 `清理后标题`。
- 如果旧 `清理后标题` 为空，则用旧 `Gamer520标题` 兜底，并在迁移摘要中报告这些行。
- 删除 `Gamer520标题` 前先生成备份，避免原始标题信息不可逆丢失。
- `推荐度` 直接继承旧 `推荐度0-5` 的值。
- 迁移后立即运行校验：字段完整、行数不变、链接集合不变、备注不丢、推荐度均为 `1` 到 `5`。

建议迁移步骤：

- 由 AI 写一个临时 Python 脚本，或直接用一次性数据处理代码完成迁移。
- 迁移脚本不进入 CLI，不保留 `migrate-schema` 命令。
- 迁移前备份 `gamer520-games.csv`。
- 迁移后用临时校验脚本确认字段、行数、链接集合、备注和推荐度。
- CLI 项目只面向迁移后的新 schema。

## 数据模型

核心模型 `GameRow`：

```python
class GameRow(BaseModel):
    release_date: date
    platform: Literal["PC", "Switch", "PC/Switch"]
    title: str
    tags: str
    one_line_description: str
    score: int
    recommendation_label: str
    reasoning: str
    url: AnyUrl
    user_note: str = ""
```

内部字段名用英文，CSV 表头用中文。转换层集中放在 `models.py`，不要让中文字段名散落在各个操作里。

## 规范化规则

`normalize.py` 负责所有去重相关规则。

### 链接规范化

输入：

```text
https://www.gamer520.com/114951.html?foo=bar
https://GAMER520.com/114951.html/
http://www.gamer520.com/114951.html
```

统一为：

```text
https://www.gamer520.com/114951.html
```

规则：

- 域名小写。
- 去掉 query 和 fragment。
- 去掉末尾 `/`。
- 协议统一为 `https`。
- 提取链接 ID 用正则 `/(\\d+)\\.html$`。

### 标题规范化

用于去重，不用于展示。

规则：

- 转小写。
- 去空格和常见标点。
- 去括号中的版本修饰。
- 去常见版本后缀，例如：
  - 正式版
  - 支持者版
  - 豪华版
  - 数字豪华版
  - 传奇版
  - 先锋版
  - 终极版
  - 完整版
  - 典藏版
  - v1.0 / v2.3.4

标题规范化只能用于“候选重复判断”，不能直接改写 `标题`。

## CLI 命令设计

命令面保持小而稳定，第一版只做 7 个日常命令：

```text
latest
validate
search
export
add
remove
sort
```

设计原则：

- CLI 尽量接受文本输入、输出文本结果，方便 AI 直接调用和解析。
- 写入类命令支持 `--dry-run`，dry run 只向 stdout 输出将发生的变化，不修改 CSV。
- 结构化输出优先支持 `--json` 或 `--format jsonl`。
- 默认输出使用 plain text 或 JSON/JSONL。Rich 美化只能作为可选展示层，不能成为 AI 解析结果的前提。
- stdin / 纯文本输入是第一等入口，临时文件是需要留痕、审阅或复用时的备选入口。

### `latest`

返回 CSV 中最新发布日期。

```bash
uv run gamer520 latest
```

输出示例：

```text
latest_date: 2026-06-06
rows_on_latest_date: 12
latest_link_id: 114951
total_rows: 219
```

用途：

- 每日更新前确定扫描边界。
- 同一天多次更新时，不跳过当天新增内容。

### `search`

搜索标题、链接、备注。

```bash
uv run gamer520 search "灰烬王国"
uv run gamer520 search "灰烬王国" --json
uv run gamer520 search --title "灰烬王国 陨落纪元"
uv run gamer520 search 114946
uv run gamer520 search "想玩"
```

参数：

```bash
--limit 20
--json
--fields 日期,平台,标题,推荐度,链接,备注
```

标题查重规则：

- 每日更新时，候选游戏的查重主路径是 `search --title "..."`。
- `--title` 默认使用模糊匹配，不要求精确相等。
- 模糊匹配应覆盖常见差异：空格、标点、大小写、版本后缀、中文名/英文名缺失、AI 清理标题时产生的小偏差。
- CLI 只负责返回候选条目，不直接判断“是不是同一个游戏”。
- AI 根据候选条目的标题、平台、链接、日期、标签、描述和理由，判断是否同一款游戏、版本更新、资料片或新作。

用途：

- AI 或用户修改某个条目前，先定位行。
- 每日新增前，用标题模糊匹配找出可能重复的旧条目。
- 不需要读整份 CSV。

### `export`

按条件导出一部分 CSV。这个命令统一承担“最近条目”和“AI 上下文导出”，避免维护 `recent` 与 `export-context` 两套重叠逻辑。

```bash
uv run gamer520 export --date 2026-06-06
uv run gamer520 export --days 3
uv run gamer520 export --query "王国"
uv run gamer520 export --latest
uv run gamer520 export --platform PC
```

格式参数：

```bash
--format jsonl
--format md
--format csv
```

默认输出 `jsonl`，适合 AI 消费；`md` 适合人看；`csv` 适合进一步管道处理。

默认字段应比 CSV 更省 token：

```jsonl
{"发布日期":"2026-06-06","平台":"PC","标题":"灰烬王国 陨落纪元 Kingdom of Ashes","推荐度":"3","链接":"https://www.gamer520.com/114946.html","用户备注":""}
```

默认不输出长字段 `判断理由`，除非传：

```bash
--full
```

### `add`

追加新增条目。

```bash
echo '[...]' | uv run gamer520 add --stdin --dry-run
echo '[...]' | uv run gamer520 add --stdin
uv run gamer520 add pending.json --dry-run
uv run gamer520 add pending.json
```

`add` 必须同时支持 stdin 输入和文件输入。stdin 是 AI 的优先路径，因为 AI 可以直接生成 JSON 文本并管给 CLI，不需要额外读写临时文件。文件输入只在需要人工审阅、保留中间结果或重复执行时使用。

输入 JSON 格式：

```json
[
  {
    "发布日期": "2026-06-06",
    "平台": "PC",
    "标题": "灰烬王国 陨落纪元 Kingdom of Ashes",
    "标签": "叙事；探索",
    "一句话描述": "玩家...",
    "推荐度": "4",
    "推荐标签": "推荐",
    "判断理由": "符合...",
    "链接": "https://www.gamer520.com/114999.html",
    "用户备注": ""
  }
]
```

写入前必须执行：

- 字段完整性校验。
- 日期格式校验。
- 推荐度范围校验。
- URL 规范化。
- 完全重复链接检查，重复则拒绝写入。
- 规范化标题完全重复检查，重复则拒绝写入并输出匹配行。

如果发现重复，默认拒绝写入，并输出匹配行。

输出规则：

- `--dry-run` 输出新增数量、重复数量、将写入的条目摘要和错误详情。
- 真正写入时 stdout 输出写入摘要，stderr 只放错误和警告。
- `--json` 时输出机器可读 JSON，便于 AI 解析。

### `remove`

按标题删除误收录条目。这个命令只做最小删除能力，和 `add` 组成基础编辑闭环。

```bash
uv run gamer520 remove --title "灰烬王国 陨落纪元 Kingdom of Ashes" --dry-run
uv run gamer520 remove --title "灰烬王国 陨落纪元 Kingdom of Ashes" --yes
```

规则：

- 只允许 `--title` 删除，第一版不做批量删除。
- `remove --title` 不使用模糊匹配。删除是破坏性操作，必须比搜索更严格。
- 匹配规则为规范化后精确匹配：可忽略空格、标点、大小写等纯格式差异，但不能用部分标题、缺失英文名、近似标题来删除。
- 如果匹配 0 行，失败并提示无匹配。
- 如果匹配多行，说明数据库标题唯一性被破坏，必须失败并输出候选列表，交给 AI 或用户先修复数据。
- 推荐流程是先用 `search --title` 模糊找候选，再复制确认后的完整 `标题` 调用 `remove --title`。
- 默认必须先 `--dry-run` 查看将删除的行。
- 真正删除必须显式传 `--yes`。
- 删除后自动执行与写操作相同的校验。
- stdout 输出删除摘要；stderr 只放错误和警告。

### `sort`

排序并写回。

```bash
uv run gamer520 sort
uv run gamer520 sort --dry-run
```

排序规则：

- `发布日期` 降序。
- 同日期按 Gamer520 链接 ID 降序。
- 无法提取链接 ID 的条目放在同日期最后，并在输出中提示。

### `validate`

校验数据健康。

```bash
uv run gamer520 validate
uv run gamer520 validate --strict
```

检查项：

- CSV 表头是否完整。
- 每行字段数是否正确。
- 日期是否为 `YYYY-MM-DD`。
- 平台是否为 `PC` / `Switch` / `PC/Switch`。
- 推荐度是否为 `1` 到 `5`。
- 推荐标签是否和分数大体一致。
- 链接是否是 Gamer520 条目页。
- 链接重复数量。
- 规范化标题重复数量。
- 备注列是否存在且未丢。
- 是否存在英文逗号破坏 CSV 不是问题，因为 CSV 会正确转义；但用户备注仍建议使用中文标点。

`--strict` 可以把可疑标题重复视为失败。

## 每日更新流程

新的 Skill 流程应改为：

1. 运行：

   ```bash
   uv run --project 游戏收集agent/gamer520_cli gamer520 latest
   uv run --project 游戏收集agent/gamer520_cli gamer520 validate
   ```

2. 读取 `taste.txt`。

3. 浏览 Gamer520 PC 和 Switch 列表页。

4. 根据 `latest_date` 和 `latest_link_id` 决定停止边界：

   - 同一天更新时，不能只看日期。
   - 如果列表页出现的链接 ID 已经小于等于 CSV 最新链接 ID，且日期不新于最新日期，可以停止。
   - 如果日期相同但链接 ID 更大，仍然需要处理。

5. 对候选条目逐个运行标题模糊搜索：

   ```bash
   uv run gamer520 search --title "..." --json
   ```

6. AI 根据 `search --title` 返回的候选，判断是否同一游戏、版本更新、资料片或新作。只有判断为未收录的新条目，才继续打开详情页生成新增数据。

7. AI 生成新增条目的 JSON 文本。

8. 写入前 dry run：

   ```bash
   printf '%s\n' '[...]' | uv run gamer520 add --stdin --dry-run
   ```

9. 确认无问题后写入：

   ```bash
   printf '%s\n' '[...]' | uv run gamer520 add --stdin
   uv run gamer520 sort
   uv run gamer520 validate
   ```

10. 如果新增 JSON 需要人工审阅或复用，再保存为 `pending.json` 并用文件模式执行 `add`。

11. AI 根据新增条目和校验摘要生成最终回复。

## AI 和 CLI 的分工边界

### 脚本确定性处理

- CSV 读写
- BOM 保留
- 字段顺序
- 链接规范化
- 标题规范化
- 重复检测
- 排序
- 小上下文导出
- 数据健康检查

### AI 判断性处理

- 游戏内容理解
- 推荐度判断
- 标签和描述写作
- 版本是否应独立收录
- PC/Switch 是否真的是同一游戏
- 用户备注的语义整理
- 异常条目的人工审阅

## 第一阶段开发任务

### P0：最小可用

- 初始化 uv 项目。
- 实现 CSV 读写。
- 实现 `latest`。
- 实现 `search`。
- 实现 `validate`。
- 实现 `sort`。
- 添加基础测试。

### P1：每日更新可用

- 实现 `add`。
- 实现 `remove`。
- 实现 `export`。
- 修改 `gamer520-daily-update-SKILL.md`，让它优先使用 CLI。
- 为每日更新准备 JSON 文本示例，默认通过 stdin 直接传给 `add`；只有需要留痕时才保存为 `pending.json`。

### P2：维护能力增强

- 增加更细的标题规范化测试。
- 增加更多 `export` 筛选条件。
- 增加更好的 `validate --json` 报告，帮助 AI 判断是否需要手动修 CSV。

### P3：可选升级

- 自动备份写入前 CSV。
- 更详细的写入前后 diff 摘要。
- 从 Markdown 表格导入的能力，但仍复用 `add`，不新增日常命令。

## 测试策略

### 单元测试

`test_normalize.py`：

- 链接 query 去除。
- 域名大小写统一。
- 末尾 slash 去除。
- 标题版本后缀去除。
- 中英文标点去除。

`test_csv_store.py`：

- UTF-8 with BOM 读取。
- UTF-8 with BOM 写入。
- 字段顺序不变。
- 用户备注不丢。

`test_operations.py`：

- latest 日期和最新链接 ID。
- search 标题模糊匹配能命中空格、标点、版本后缀差异。
- search 标题模糊匹配能处理候选标题缺少英文名或只保留中文名的情况。
- sort 日期和 ID 排序。
- add 拒绝重复链接。
- add 拒绝规范化标题完全重复。
- add 支持文件输入。
- add 支持 stdin 输入。
- remove 规范化标题精确且唯一命中时可以 dry-run。
- remove 不接受部分标题或模糊标题删除。
- remove 标题匹配 0 行或多行时拒绝删除。

### 集成测试

准备一个小型 fixture CSV，不使用真实大 CSV：

```text
tests/fixtures/games.csv
```

每个命令至少有一个 `CliRunner` 测试，确认输出和退出码。

## 错误处理约定

退出码：

- `0`：成功。
- `1`：数据校验失败或写入被拒绝。
- `2`：命令参数错误。
- `3`：文件路径或编码错误。

输出：

- 默认输出 plain text，避免 ANSI 样式影响 AI 读取。
- 给 AI 或脚本消费使用 `--json`。
- 写操作都支持 `--dry-run`。
- `add --stdin` 是第一版的默认协作方式，不是未来扩展点。
- stdout 放正常结果，stderr 放错误和警告，方便 AI 分离解析。

## 写入安全

所有会修改 CSV 的命令都应遵守：

- 读取完整 CSV。
- 在内存中生成新 CSV。
- 校验新 CSV。
- 写入临时文件。
- 原子替换原文件。
- 保留 UTF-8 with BOM。

建议自动备份：

```text
gamer520-games.csv.bak-20260606-153000
```

第一阶段可以只在写入前打印摘要，第二阶段再加自动备份。

## Skill 修改建议

`gamer520-daily-update-SKILL.md` 应减少对整份 CSV 的描述，把数据操作改为 CLI 命令：

- 每次更新前必须运行 `latest`、`validate`。
- 新增查重优先使用 `search --title` 做标题模糊搜索，不要读取整份 CSV。
- 完全重复链接和规范化标题完全重复由 `add` 内部拒绝，不暴露单独命令。
- 新增内容默认用 JSON 文本通过 stdin 交给 `add`；需要审阅或复用时再保存为 `pending.json`。
- 写入必须通过 `add`，不能手写追加 CSV 行。
- 误添加删除必须通过 `remove --title`，不能手写删除 CSV 行。
- 排序必须通过 `sort`。
- 查询局部上下文必须通过 `export`。
- 最终验证必须通过 `validate`。
- PC/Switch 合并、单条修改暂时由 AI 小范围编辑 CSV 后运行 `validate` 和 `sort` 完成，不进入第一版 CLI 命令面。

## 数据库升级判断

只有满足以下条件之一时，再考虑迁移数据库：

- CSV 超过几千到上万行，搜索和校验明显变慢。
- 需要记录评分历史、多个来源、多个下载链接、平台版本、标签表。
- 需要多人或多 agent 同时写入。
- 需要在网站中做复杂筛选和统计。

即使升级，也建议保留：

```bash
uv run gamer520 export-csv
uv run gamer520 import-csv
```

这样 CSV 仍然可以作为人工编辑和 AI 审阅格式。

## 推荐实现顺序

1. 建 uv 项目。
2. 由 AI 写临时脚本或一次性数据处理代码，把 CSV 迁移到 `标题`、`推荐度` 的新表头；这个迁移不进入 CLI。
3. 对迁移后的真实 CSV 做行数、链接集合、备注和推荐度校验。
4. 写 `models.py` 和 `csv_store.py`，只支持新 schema。
5. 写 `normalize.py`。
6. 写 `latest/search/validate/sort`。
7. 用真实 CSV 跑 dry run。
8. 写测试。
9. 写 `add/remove/export`，其中 `add` 优先支持 stdin 输入，同时支持文件输入。
10. 修改 Skill。
11. 根据真实使用情况再决定是否增加新命令，默认不扩张命令面。

这个顺序能最快解决上下文浪费问题，同时不牺牲 AI 的灵活操作能力。
