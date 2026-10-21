# 游戏收集 Agent

这个目录维护个人游戏判断库；Gamer520 是其中一个自动发现来源。通过游戏库 CLI 管理数据，通过 AI Skill 执行每日更新流程。

## 项目结构

| 层 | 位置 | 说明 |
|----|------|------|
| 数据 | `game-library.csv`、`taste.txt` | 主数据库和口味基准，不直接编辑 |
| 工具 | `game_library_cli/` | 游戏库 CLI，所有数据库操作通过它完成 |
| 工作流 | `游戏库-Gamer520更新SKILL.md` | Gamer520 来源更新的执行流程 |
| 临时 | `scratch/` | 个人札记、历史产物，不属于生产流程 |

CLI 完整参考（命令、CSV schema、示例）见 `game_library_cli/README.md`。所有正式游戏库操作通过 `game_library_cli/game-library`，不要直接改 CSV、用户备注或来源游标。不要直接读取整份 CSV；使用 `search` 或 `export` 获取局部数据。不要创建流程中转文件；CLI 输出由 Agent 直接处理，持久化业务状态只写数据库和 Doctor 复核账本。

## 每日 Gamer520 更新

详细执行流程见 `游戏库-Gamer520更新SKILL.md`。常用命令：

```bash
游戏收集agent/game_library_cli/game-library <command>
```

```bash
# 查看最新收录边界（PC / Switch 分别查）
游戏收集agent/game_library_cli/game-library source gamer520 latest --platform PC --json
游戏收集agent/game_library_cli/game-library source gamer520 latest --platform Switch --json

# 搜索
游戏收集agent/game_library_cli/game-library search "关键词" --json

# 自动分页扫描与对账
游戏收集agent/game_library_cli/game-library source gamer520 scan --platform all

# 数据库通用体检
游戏收集agent/game_library_cli/game-library doctor --json

# 记录已复核的相似标题结论（先 --dry-run，再 --yes）
游戏收集agent/game_library_cli/game-library doctor-review \
  --title "标题 A" --title "标题 B" \
  --decision distinct --reason "不同游戏" --dry-run

# 导出最近 N 天
游戏收集agent/game_library_cli/game-library export --days 7 --json

# 健康检查
游戏收集agent/game_library_cli/game-library validate
```

## 判断标准修订与行为评估

修改 `taste.txt` 或游戏判断 Skill、复盘口味反馈时，先读取 `evals/SKILL.md`，按其中冻结基线、独立模型测试和具体判断对比的流程执行。候选标准与正式标准、现有金标准分开保存；新增测试案例先提交用户审核，不自行批准。模型审阅只是辅助意见，不能作为人工审核记录或自动采用授权。

该评估工作流允许保存冻结输入和真实模型输出，独立于每日来源流程的中转文件限制。默认使用独立 GPT 6 Luna Agent 测试。确定性工程验证与游戏判断行为评估是不同检查，不要把 CLI 单元测试称作行为评估。
