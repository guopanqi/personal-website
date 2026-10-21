使用独立 Agent，model=gpt-6-luna，fork_turns=none。
仅读取本目录 inputs.json、taste.txt、SKILL.md。不得读取上级目录、金标准、候选版本以外的标准、其他运行结果或历史报告。禁止联网、扫描来源、写正式库和推进游标。输入是冻结资料；title_only 可依赖自身知识，但须注明未经核验，不能虚构证据，未知则保留不确定性。Skill中的联网与入库指令在本测试封装中禁用。
对全部案例实际判断。每条包含 id,title,score(1..5整数或null),result_label(必须推荐/推荐/不推荐/信息不足)，以及字符串字段 judgment, experience_center, mechanics, innovation, narrative_role, personal_interest, research_value, reason, evidence_basis, uncertainty。字段是记录格式，不预设结论；即使评分相同也应保留具体分析。
JSON格式 {"model":"gpt-6-luna","results":[...]}，保存到本目录 raw-output.json。
