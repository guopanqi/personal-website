# gamer520-cli

CLI 工具，用于管理 Gamer520 游戏收藏 CSV 数据。将确定性的 CSV 操作（查最新日期、搜索、校验、排序、追加、删除、导出）脚本化，保留 AI 对游戏内容的判断和人工可编辑性。

CSV 仍然是唯一主数据源，不引入数据库。

## 目录结构

```
游戏收集agent/
├── gamer520-games.csv          # 主数据源（UTF-8 with BOM）
├── taste.txt                   # 用户口味基准
├── gamer520-daily-update-SKILL.md  # AI 每日更新流程
├── gamer520_cli/               # 本 CLI 项目
│   ├── pyproject.toml
│   ├── README.md
│   ├── src/gamer520_cli/
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── cli.py              # CLI 命令入口
│   │   ├── config.py           # 默认路径配置
│   │   ├── csv_store.py        # CSV 读写（UTF-8 with BOM）
│   │   ├── models.py           # GameRow 数据模型
│   │   └── normalize.py        # URL/标题规范化
│   └── tests/
│       ├── fixtures/games.csv  # 测试用最小 CSV
│       ├── test_normalize.py
│       ├── test_csv_store.py
│       └── test_operations.py
```

## 前提

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## 安装

```bash
cd 游戏收集agent/gamer520_cli
uv sync
```

## 运行方式

在 CLI 子目录内：

```bash
cd 游戏收集agent/gamer520_cli
uv run gamer520 <command>
```

从仓库根目录：

```bash
uv run --project 游戏收集agent/gamer520_cli gamer520 <command>
```

## 命令参考

### `latest`

返回 CSV 中最新发布日期和相关统计。

```bash
uv run gamer520 latest
uv run gamer520 latest --json
```

输出：

```
latest_date: 2026-06-06
rows_on_latest_date: 11
latest_link_id: 114951
total_rows: 219
```

用途：每日更新前确定扫描边界。同一天多次更新时，不跳过当天新增内容。

### `search`

搜索标题、链接、备注。

```bash
uv run gamer520 search "灰烬王国"
uv run gamer520 search 114946
uv run gamer520 search "想玩" --limit 5
uv run gamer520 search --title "候选标题" --json
```

`--title` 使用模糊匹配（忽略空格、标点、大小写、版本后缀），适合查重。

`--full` 输出所有 10 个字段（默认仅 6 个）。

显式 `query` 参数使用简单子串匹配（不区分大小写），搜索标题、链接、用户备注。

纯数字 query 自动转为链接 ID 搜索。

```bash
uv run gamer520 search "宝石少女" --full --json
```

### `validate`

校验 CSV 数据健康。

```bash
uv run gamer520 validate
uv run gamer520 validate --json
```

检查项：
- 表头完整、字段顺序正确
- 日期格式 `YYYY-MM-DD`
- 平台合法（`PC` / `Switch` / `PC/Switch`）
- 推荐度 `1`–`5`
- URL 非空且格式合法
- 链接重复
- 规范化标题重复
- 空标题

RFC 中 `--strict` 参数已保留但当前无额外效果。标题唯一性默认检查。

### `sort`

按发布日期降序、同日期按链接 ID 降序排列。

```bash
uv run gamer520 sort              # 写入排序结果
uv run gamer520 sort --dry-run    # 仅预览
```

无法提取链接 ID 的条目排在同日期最后。

### `add`

追加新增条目。

```bash
# stdin 输入（AI 优先路径）
printf '%s\n' '[...JSON数组...]' | uv run gamer520 add --stdin --dry-run
printf '%s\n' '[...JSON数组...]' | uv run gamer520 add --stdin

# 文件输入（需要审阅或复用时）
uv run gamer520 add --file pending.json --dry-run
uv run gamer520 add --file pending.json
```

输入 JSON 格式：

```json
[
  {
    "发布日期": "2026-06-07",
    "平台": "PC",
    "标题": "游戏名称",
    "标签": "叙事；探索",
    "一句话描述": "玩家扮演...",
    "推荐度": "3",
    "推荐标签": "可试",
    "判断理由": "符合口味...",
    "链接": "https://www.gamer520.com/123456.html",
    "用户备注": ""
  }
]
```

写入前自动执行：
- 字段完整性校验
- 日期格式校验
- 推荐度范围校验
- URL 非空校验
- 链接重复拒绝
- 规范化标题重复拒绝
- 整体 CSV 健康校验（dry-run 和 write 均执行）

`--dry-run` 和写入路径均会校验最终 CSV 健康状态。如果已有 CSV 存在重复或坏数据，dry-run 也会失败。

### `remove`

按标题删除误收录条目。

```bash
uv run gamer520 remove --title "精确标题" --dry-run
uv run gamer520 remove --title "精确标题" --yes
```

匹配规则为规范化后精确匹配（忽略空格、标点、大小写，但不去版本后缀）。
- 匹配 0 行 → 失败
- 匹配多行 → 失败（输出候选列表）
- 删除后自动校验剩余 CSV，校验失败则拒绝删除

推荐先用 `search --title` 模糊找候选，再复制确认后的完整标题删除。

### `update`

修改已有条目的一个或多个字段。

```bash
# dry-run 预览
uv run gamer520 update --title "舒适森林 Cozy Grove" --set "用户备注=玩过" --dry-run

# 确认写入
uv run gamer520 update --title "舒适森林 Cozy Grove" --set "用户备注=玩过" --yes

# 多字段同时修改
uv run gamer520 update --title "游戏名" --set "推荐度=4" --set "推荐标签=推荐" --yes
```

匹配规则同 `remove`（规范化后精确匹配）。
- 匹配 0 行或匹配多行 → 失败
- 字段名必须是 CSV 的 10 个中文字段之一
- 标量校验：推荐度 1–5、平台 PC/Switch/PC/Switch、日期 YYYY-MM-DD
- 修改后自动执行全表校验，校验失败拒绝写入
- 无需先 `remove` 再 `add`，一步完成

### `export`

按条件导出 CSV 子集，供 AI 上下文使用。

```bash
uv run gamer520 export --date 2026-06-06
uv run gamer520 export --days 3
uv run gamer520 export --query "王国"
uv run gamer520 export --latest
uv run gamer520 export --platform PC
```

格式参数（默认 `jsonl`）：

```bash
--format jsonl   # AI 优先，每行一个 JSON 对象
--format csv     # 适合管道处理
--format md      # 适合人阅读
```

默认不输出长字段 `判断理由`，除非传 `--full`。

## 退出码

| 退出码 | 含义 |
|--------|------|
| 0 | 成功 |
| 1 | 数据校验失败或写入被拒绝 |
| 2 | 命令参数错误 |
| 3 | 文件路径或编码错误 |

## 输出约定

- stdout：正常结果
- stderr：错误和警告
- `--json`：机器可读 JSON，适合 AI 解析
- 写操作支持 `--dry-run`，只输出变化摘要不修改文件

## 测试

```bash
cd 游戏收集agent/gamer520_cli
uv run pytest
```

测试使用独立的 fixture CSV（`tests/fixtures/games.csv`），不影响真实数据。

### 测试策略

- `test_normalize.py`：URL 规范化、标题规范化（key vs search 两种语义）
- `test_csv_store.py`：UTF-8 with BOM 读写、字段顺序、表头校验
- `test_operations.py`：每个命令至少一个 CliRunner 集成测试

## CSV Schema

默认路径：`游戏收集agent/gamer520-games.csv`

字段（固定顺序）：

| 中文字段 | 说明 |
|----------|------|
| 发布日期 | `YYYY-MM-DD` |
| 平台 | `PC` / `Switch` / `PC/Switch` |
| 标题 | 去掉版本修饰，必要时补充英文名 |
| 标签 | 中文分号 `；` 分隔 |
| 一句话描述 | 基于详情页 |
| 推荐度 | `1`–`5` |
| 推荐标签 | 统一文字标签 |
| 判断理由 | 结合口味解释评分 |
| 链接 | 条目页 URL |
| 用户备注 | 人工填写，新增默认留空 |

编码：UTF-8 with BOM。

## 与 AI Skill 的关系

完整的每日更新流程在 `游戏收集agent/gamer520-daily-update-SKILL.md` 中定义。CLI 负责确定性操作部分：

| CLI 负责 | AI 负责 |
|----------|---------|
| CSV 读写、BOM 保留、字段顺序 | 游戏内容理解 |
| 链接/标题规范化 | 推荐度判断 |
| 重复检测 | 标签和描述写作 |
| 排序 | 版本是否独立收录 |
| 局部上下文导出 | PC/Switch 合并判断 |
| 数据健康检查 | 用户备注的语义整理 |
| 单条修改（`update`） | 修改内容的语义判断 |
