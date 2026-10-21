# 游戏判断行为评估

入口是 [SKILL.md](SKILL.md)。这是现有 Python CLI 旁的独立、无第三方依赖工具，不导入游戏库写入模块，不改变 Gamer520 流程。

## 文件与审核边界

- `../game-library-test-set-draft.json`：现有已批准33案例，保持原样。原有三类推荐标签和 reason_types 仍为金标准，不新增固定 expected_score。
- 当前只载入原有33个案例；`archive/`中的旧扩充提案停用，不自动恢复或载入。
- `candidates/`：完整候选 Taste 与来源 Skill。当前只增加体验中心、叙事作用与双向因果关系的判断；正式版本已有玩法创新原则，不重复加强其权重。
- `experiments/<name>/`：输入、金标准、版本全文、SHA-256、Git HEAD、模型、假设、UTC时间与重复编号。基线是当前工作区；HEAD 只用于参考。两个子目录是无金标准的运行包。
- `*-raw.json`：实际模型输出原文；`*-result.json`：校验后的导入记录和独立Agent标识。导入器校验格式和来源输入一致性，不证明内容正确，也不能防止人为伪造模型记录。
- `comparison.json`、`report.md`：逐例原文对比；`human-review.json`：人工审阅入口，默认全部不确定。独立模型评审另存，不当作人工结论。

## 每次修订

先提出一个明确问题和小范围候选改动，再冻结实验：

```bash
python3 游戏收集agent/evals/eval.py prepare experiment-name \
  --hypothesis '具体分析方法会改善什么，同时保护哪些已有偏好' \
  --taste 游戏收集agent/evals/candidates/taste.txt \
  --skill 游戏收集agent/evals/candidates/SKILL.md
```

工具生成 baseline 与 candidate 运行包。主Agent分别用 collaboration.spawn_agent，设置 `model="gpt-6-luna"`、`reasoning_effort="high"`、`fork_turns="none"`，只给各自运行包绝对路径及 request.md，不传递当前对话。prepare 本身不调用模型。当前桌面Agent工具可实际运行，无需额外API密钥；脚本离开该环境时需要另一个具有相同隔离能力的模型执行器。

待两个 Agent 各自保存 raw-output.json 后：

```bash
python3 游戏收集agent/evals/eval.py import 游戏收集agent/evals/experiments/experiment-name baseline \
  游戏收集agent/evals/experiments/experiment-name/baseline/raw-output.json --agent-id '<实际Agent标识>'
python3 游戏收集agent/evals/eval.py import 游戏收集agent/evals/experiments/experiment-name candidate \
  游戏收集agent/evals/experiments/experiment-name/candidate/raw-output.json --agent-id '<实际Agent标识>'
python3 游戏收集agent/evals/eval.py compare 游戏收集agent/evals/experiments/experiment-name
```

人工在 human-review.json 中填写五个维度、理由、reviewed_by 和 verdict（改进/持平/退化/不确定），再运行 compare。不要只凭推荐标签一致或分数提高就批准候选。主指标是25个应推荐案例的覆盖，拒绝它们属于严重漏推荐；推荐与必须推荐之间变化只记录强度，不自动算退化。信息不足作为待确认单列，不冒充推荐覆盖或明确拒绝。不推荐案例被推荐单列误推荐；虚构机制、错误理解和证据仍需按具体理由评价。完整标签一致率只保留为次要描述，不作为优化目标或通过门槛。模型审阅可作为阅读辅助，最终是否采用由用户决定。

对同一假设需要重复时新建实验并设置 `--repetition 2` 等；记录全部结果。发现问题后只在开发集调参。已有33个案例曾参与benchmark，全部是开发/回归集。当前不引入新案例，`prepare ... --split holdout`会明确失败；不能把原33例重命名成独立保留集。保留集一旦影响下一次修订，不能继续称作未见验证集。

## 两种输入能证明什么

原33案例只有标题：适合推荐门槛回归，与历史benchmark口径一致；判断依据是模型记忆，不验证游戏实际玩法，也不测试联网核验。未知游戏必须诚实返回信息不足。本次统一结构化输出会让基线也关注体验中心等字段，因此测量的是同一封装下标准版本的边际效果，不是原每日自由文本流程的完整复现。

当前使用原案例，可在用户审核的前提下补充这些真实游戏的玩法证据，不新增假想样本。先冻结证据，再运行两个版本；不在两轮中分别实时搜索导致输入漂移。推荐强度带有主观和动态性，不宜当作硬标签约束。

## 工程验证

```bash
python3 -m unittest discover -s 游戏收集agent/evals/tests -v
```

这是工具的隔离与完整性检查，不能替代实际行为评估。运行产物供审阅，不写正式CSV、备注、复核账本或来源游标；没有自动推广生产标准的命令。

## 用户明确要求假想辅助实验时

使用单独命令，不改变原33例或任何提案审核状态：

```bash
python3 游戏收集agent/evals/eval.py diagnose auxiliary-name \
  --cases 游戏收集agent/evals/archive/proposed-cases.json \
  --hypothesis '比较给定规则下的判断，作为辅助诊断而非正式benchmark'
```

只选择带有synthetic_controlled_fixture证据的案例；真实游戏提案排除。运行包、独立Luna执行、导入和compare流程与正式实验相同。推荐标签金标准留空，不计算匹配通过率；审阅实际分析和成对差异，不能强制不同场景给不同分数。所有案例已被设计者看到，本轮不宣称独立保留验证。
