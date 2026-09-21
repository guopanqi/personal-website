# 游戏判断库 CLI

这个工具维护的是一份**个人游戏判断库**：每行是一款已收录的游戏，包含你的推荐度、理由与备注。Gamer520 是重要的自动发现来源，但不拥有这份库，也不会覆盖手工收录的条目。

所有 CSV 读写都通过 CLI 完成，不直接编辑 `game-library.csv`。

## 核心模型

| 字段 | 含义 |
|---|---|
| `收录日期` | 游戏进入判断库的日期；手工录入时通常为当天。 |
| `收录来源` | `gamer520` 或 `manual`，表示首次收录来源，创建后不可改写。 |
| `Gamer520帖子日期` | 仅 Gamer520 条目有值；只用于来源追溯和扫描。 |
| `来源链接` | Gamer520 条目必填；manual 条目可空，也可保存 Steam/官网链接。 |
| `用户备注` | 自由文本；状态继续写在这里，例如 `wishlist；需要 PC`。 |

Gamer520 扫描进度保存在独立的 `gamer520-sync-state.json` 中。它与游戏库分离：手工收录 PC 游戏不会移动 Gamer520 的 PC 扫描边界。

## 初始化迁移

旧 CSV 的全部记录会迁为 `gamer520`；旧“帖子发布日期”同时作为 `Gamer520帖子日期` 和历史近似的 `收录日期`。原有评分、理由、备注不变。

```bash
游戏收集agent/game_library_cli/game-library migrate --dry-run
游戏收集agent/game_library_cli/game-library migrate --yes
```

## 日常命令

```bash
# 查询、校验、排序（排序按收录日期）
游戏收集agent/game_library_cli/game-library search "wishlist" --field "用户备注" --json --full --limit 5000
游戏收集agent/game_library_cli/game-library validate
游戏收集agent/game_library_cli/game-library sort

# 更新既有条目；不能改写收录来源
游戏收集agent/game_library_cli/game-library update --title "游戏名" --set "用户备注=wishlist；需要 PC" --dry-run
游戏收集agent/game_library_cli/game-library update --title "游戏名" --set "用户备注=wishlist；需要 PC" --yes

# 新增条目：先用 --dry-run 预览，再用 --yes 正式写入
游戏收集agent/game_library_cli/game-library add --stdin --dry-run
游戏收集agent/game_library_cli/game-library add --stdin --yes

# 批量更新；一次锁定、读取、校验和写入
游戏收集agent/game_library_cli/game-library update-batch --stdin --dry-run <<'ENDJSON'
[
  {"title":"游戏 A","set":{"用户备注":"played"}},
  {"title":"游戏 B","set":{"用户备注":"wishlist；需要 PC"}}
]
ENDJSON

# Gamer520 扫描（只读），游标由独立状态文件提供
游戏收集agent/game_library_cli/game-library source gamer520 scan --platform all

# 所有扫描结果已处理并持久化后，推进对应游标
游戏收集agent/game_library_cli/game-library source gamer520 advance-cursor --platform PC --post-date 2026-08-21 --link-id 120238 --dry-run
游戏收集agent/game_library_cli/game-library source gamer520 advance-cursor --platform PC --post-date 2026-08-21 --link-id 120238 --yes
```

`source gamer520 scan` 输出 `next_cursor`。只有扫描完整、所有新增/复核结果已经写入游戏库并通过校验后，才能用它推进游标。

所有会修改 `game-library.csv` 的命令都会使用同一个 sidecar 锁文件
`game-library.csv.lock`，锁覆盖整个读取—修改—校验—写入事务。锁文件是运行时文件，已加入 `.gitignore`。

## 新增条目

统一使用 `source + assessment` JSON。旧版 Gamer520 输入中的 `date` 仍兼容，等价于 `collected_date` 和 `gamer520_post_date`。

### Gamer520 自动发现条目

```bash
游戏收集agent/game_library_cli/game-library add --stdin --dry-run <<'ENDJSON'
[
  {
    "source": {
      "type": "gamer520",
      "collected_date": "2026-08-21",
      "gamer520_post_date": "2026-08-21",
      "platform": "PC",
      "title": "游戏名",
      "url": "https://www.gamer520.com/123456.html"
    },
    "assessment": {
      "tags": ["叙事", "探索"],
      "judgment": "游戏判断：先写玩家会进入什么处境，再说明核心循环、有效差异与主要限制。",
      "score": 4,
      "reason": "具体的判断理由。",
      "user_note": ""
    }
  }
]
ENDJSON
```

dry-run 通过后，用相同输入再次执行 `add --stdin --yes` 正式写入。

### 手工收录条目

manual 不需要来源页；`collected_date` 省略时默认当天。

```bash
游戏收集agent/game_library_cli/game-library add --stdin --dry-run <<'ENDJSON'
[
  {
    "source": {
      "type": "manual",
      "platform": "PC",
      "title": "游戏名"
    },
    "assessment": {
      "tags": ["城镇建设"],
      "judgment": "游戏判断：先写玩家会进入什么处境，再说明核心循环、有效差异与主要限制。",
      "score": 4,
      "reason": "为什么值得记住。",
      "user_note": "wishlist；需要 PC"
    }
  }
]
ENDJSON
```

dry-run 通过后，用相同输入再次执行 `add --stdin --yes` 正式写入。

相同规范标题会被拒绝，防止重复。手工条目后来被 Gamer520 扫到时，扫描结果会归入 `existing`，不会新建、合并、改写或改变来源；高相似标题则留给人工复核。

## 关键路径

| 名称 | 路径 |
|---|---|
| 判断库 | `游戏收集agent/game-library.csv` |
| Gamer520 同步游标 | `游戏收集agent/gamer520-sync-state.json` |
| 口味基准 | `游戏收集agent/taste.txt` |
| 相似标题复核账本 | `游戏收集agent/game-library-doctor-reviews.json` |

## 运行方式

从仓库根目录调用项目自带脚本：

```bash
游戏收集agent/game_library_cli/game-library <子命令>
```

它复用项目 `.venv`，避免受限环境中 `uv sync` 的依赖下载问题。开发环境也可在 CLI 目录运行 `uv run game-library <子命令>`。
