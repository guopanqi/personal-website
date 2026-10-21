# 游戏判断实验对比

假设：把详情页评分明确标为暂定初评，并要求符合门槛的候选完成站外资料核验后重新判断最终评分，减少营销文案或单一来源造成的判断偏差；保护明确硬排除候选的低成本处理和现有推荐覆盖。

模型：gpt-6-luna；分组：dev；重复编号：1。

以推荐覆盖为主：应该推荐却判为不推荐是严重漏推荐；推荐与必须推荐之间浮动不自动算退化。信息不足单列为待确认；具体依据和证据质量仍需审阅。

推荐覆盖：基线 22/25；候选 21/25。严重漏推荐：基线 3，候选 0。

次要记录（不作为通过门槛；辅助诊断无标签金标准）：完整标签一致基线 22/33；候选 16/33。信息不足：基线 4，候选 12。

legacy title_only tests rely on model knowledge, not verified gameplay evidence
旧案例均已暴露，无独立保留集结论。

|游戏|金标准|基线|候选|候选推荐评估|人工结论|
|---|---|---|---|---|---|
|弗洛伦斯 Florence|必须推荐|推荐 (4)|推荐 (4)|推荐强度浮动|不确定|
|冰汽时代 Frostpunk|必须推荐|必须推荐 (5)|推荐 (4)|推荐强度浮动|不确定|
|短途旅行 A Short Hike|必须推荐|必须推荐 (5)|必须推荐 (5)|一致|不确定|
|渔帆暗涌 DREDGE|必须推荐|推荐 (4)|推荐 (4)|推荐强度浮动|不确定|
|深空梦里人2 Citizen Sleeper 2: Starward Vector|必须推荐|推荐 (4)|推荐 (4)|推荐强度浮动|不确定|
|孤星寂海 In Other Waters|必须推荐|推荐 (4)|推荐 (4)|推荐强度浮动|不确定|
|Cabernet|推荐|推荐 (3)|信息不足 (None)|待确认|不确定|
|活侠传 Legend of Mortal|推荐|不推荐 (2)|推荐 (3)|一致|不确定|
|越过阿尔卑斯山 Over the Alps|推荐|推荐 (3)|推荐 (3)|一致|不确定|
|奥森弗里2：信号丢失 OXENFREE II|推荐|不推荐 (2)|推荐 (3)|一致|不确定|
|孤山速降 Lonely Mountains: Downhill|推荐|推荐 (3)|推荐 (3)|一致|不确定|
|舒林 Cozy Grove|推荐|推荐 (3)|推荐 (3)|一致|不确定|
|深空梦里人 Citizen Sleeper|推荐|推荐 (4)|推荐 (4)|一致|不确定|
|文明6 Sid Meier's Civilization VI|推荐|不推荐 (2)|推荐 (3)|一致|不确定|
|节奏光剑 Beat Saber|推荐|推荐 (4)|推荐 (3)|一致|不确定|
|Just Dance|推荐|推荐 (3)|推荐 (3)|一致|不确定|
|边缘世界 RimWorld|推荐|推荐 (4)|推荐 (4)|一致|不确定|
|超越光速 FTL: Faster Than Light|推荐|推荐 (3)|推荐 (3)|一致|不确定|
|勇者斗恶龙：创世小玩家2|推荐|推荐 (4)|推荐 (3)|一致|不确定|
|司辰之书 BOOK OF HOURS|推荐|推荐 (4)|推荐 (3)|一致|不确定|
|密教模拟器 Cultist Simulator|推荐|推荐 (3)|推荐 (3)|一致|不确定|
|肖普叔叔的火箭商店 Uncle Chop's Rocket Shop|推荐|推荐 (3)|信息不足 (None)|待确认|不确定|
|俄勒冈之旅 The Oregon Trail|推荐|推荐 (3)|推荐 (3)|一致|不确定|
|苏丹的游戏 Sultan's Game|推荐|推荐 (3)|信息不足 (None)|待确认|不确定|
|勇者斗恶龙7 重制版|推荐|推荐 (3)|信息不足 (None)|待确认|不确定|
|Gathera|不推荐|信息不足 (None)|信息不足 (None)|待确认|不确定|
|Project Cobalt|不推荐|信息不足 (None)|信息不足 (None)|待确认|不确定|
|元素巫师 Elemental Witches|不推荐|信息不足 (None)|信息不足 (None)|待确认|不确定|
|噬血代码II 终极版|不推荐|不推荐 (1)|信息不足 (None)|待确认|不确定|
|书店增量 Bookstore Incremental|不推荐|不推荐 (2)|信息不足 (None)|待确认|不确定|
|破碎怪谈 切勿欺骗|不推荐|不推荐 (2)|信息不足 (None)|待确认|不确定|
|武林对决|不推荐|信息不足 (None)|信息不足 (None)|待确认|不确定|
|无为修仙传|不推荐|不推荐 (2)|信息不足 (None)|待确认|不确定|

## legacy-01 · 弗洛伦斯 Florence

审核准则：{"title": "弗洛伦斯 Florence", "source": ["好玩"], "result_label": "必须推荐", "reason_types": ["个人喜欢", "值得研究", "系统策略", "社交情境"], "draft_confidence": "high", "reason_detail": "互动谜题与日常情感高度融合，游戏形式直接参与讲故事。"}

### baseline

- judgment：一段关于亲密关系变化与成长的短篇互动叙事，适合一次或数次短时体验，情绪和人物关系是主要牵引。
- experience_center：通过点击、轻量互动和章节化场景表达关系中的靠近、摩擦与疏离；近似互动绘本/叙事短篇，形式随情绪变化而调整。
- mechanics：交互形式与叙事节奏相互配合，操作规则承载关系感受，而非复杂系统策略。
- innovation：交互节奏随关系情绪变化，属于叙事形式上的表达，不是复杂玩法创新。
- narrative_role：以日常关系和具体生活瞬间为中心，叙事表达是核心。
- personal_interest：没有明显数值或操作门槛，适合短时体验；内容较短，重复游玩空间有限。
- research_value：低；关系叙事与短篇形式可能适合，但是否触动个人取决于对题材的共鸣。
- reason：作为交互叙事设计案例有清晰表达方式，篇幅短、研究负担低。
- evidence_basis：短篇关系叙事和交互表达与用户偏好相合，值得点开；但内容短且玩法不深。
- uncertainty：仅凭熟悉的标题知识判断，未联网核验版本、具体内容或体验。
### candidate

- judgment：以短篇互动章节描绘一段关系的靠近与变化；玩家通过轻量拼图式交互参与日常沟通。题名知识判断，未经核验。
- experience_center：关系与情绪推进是体验中心，交互服务于表达，不是传统挑战。
- mechanics：把对话、拼图节奏与关系阶段绑定，形式表达较鲜明；细节未经核验。
- innovation：关系叙事的章节结构和交互隐喻。
- narrative_role：较契合人物日常、情绪和氛围偏好。
- personal_interest：个人体验及交互叙事研究价值。
- research_value：篇幅短，玩法深度有限。
- reason：仅凭题名及既有知识推断；未联网、未核验实机。
- evidence_basis：题名可识别，但本次无冻结玩法证据；判断置信度有限。
- uncertainty：仅凭标题及既有知识推断；无冻结玩法证据，未独立核验实际流程。

## legacy-02 · 冰汽时代 Frostpunk

审核准则：{"title": "冰汽时代 Frostpunk", "source": ["好玩"], "result_label": "必须推荐", "reason_types": ["个人喜欢", "值得研究"], "draft_confidence": "high", "reason_detail": "严苛环境、制度选择和人性代价共同构成强烈体验。"}

### baseline

- judgment：你要在极寒末世里维持一座城市运转，在保住更多人的同时承受制度选择带来的道德代价；压力与事件推动持续决策。
- experience_center：资源采集、供暖、建筑布局、劳动力安排和法令共同构成城市生存经营；近似生存城市建造，但法令与事件把效率选择转成居民生活和政治代价。
- mechanics：相较常见城市建造，严寒和希望/不满压力持续改变资源与制度取舍，法令会影响社会秩序，形成明确的策略后果。
- innovation：法令与希望/不满将城市管理决策转化为社会秩序和道德代价，实质改变建造经营的反馈。
- narrative_role：群体生存处境、制度与个体代价相连，压抑氛围服务于选择。
- personal_interest：策略压力高，失败与反复决策可能紧张；不以太空为题材，适合单人经营。
- research_value：高；系统经营、制度压力、情境叙事与氛围多项匹配。
- reason：制度选择如何转化成可玩后果，是成熟且有辨识度的系统叙事案例。
- evidence_basis：它同时强匹配经营压力、道德选择和氛围，足以优先体验；硬度是主要限制。
- uncertainty：基于对该作品的既有知识判断；本轮未联网核验具体版本或资料。
### candidate

- judgment：在严寒中的城市经营生存，反复权衡燃料、食物、劳动力与制度代价；生存经营和道德压力共同驱动。题名知识判断，未经核验。
- experience_center：城市存续与社会秩序是中心，不只是建造。
- mechanics：以法令和事件将资源效率转成政治、人性取舍；具体体验未经本次核验。
- innovation：制度决策和生存压力耦合，值得研究。
- narrative_role：契合经营计算、制度压力、选择后果；严苛压力可能劝退。
- personal_interest：个人体验与系统叙事研究均成立。
- research_value：资源压力和失败惩罚可能较重。
- reason：仅凭题名及既有知识推断；未联网、未核验实机。
- evidence_basis：题名可识别；细节与版本未核验。
- uncertainty：仅凭标题及既有知识推断；资源与制度循环未经独立核验。

## legacy-03 · 短途旅行 A Short Hike

审核准则：{"title": "短途旅行 A Short Hike", "source": ["好玩"], "result_label": "必须推荐", "reason_types": ["个人喜欢", "值得研究"], "draft_confidence": "high", "reason_detail": "轻松探索、简单机制和温柔氛围形成完整短旅途。"}

### baseline

- judgment：你在一座小岛上散步、攀爬、结识居民并逐步接近山顶，轻松探索与小地方的人情味构成继续前进的动力。
- experience_center：以自由移动、攀爬、滑翔、收集和对话组成探索冒险；近似轻量开放区域探索，但移动能力成长与地形路线互相作用。
- mechanics：相较线性步行叙事，地图路线和逐步获得的移动能力带来实际探索选择；目标明确而节奏宽松。
- innovation：地图路线与逐步获得的移动能力结合，使轻量探索中的路线选择产生实际作用。
- narrative_role：岛上居民、闲谈和旅途感突出，氛围轻松温暖。
- personal_interest：操作门槛低，探索自由；收集内容若追求全清可能变重复。
- research_value：高；探索、旅途、具体人物和轻松但不空的体验高度贴合。
- reason：小范围地图如何用移动能力、路线和人物对话形成探索节奏，值得研究。
- evidence_basis：个人匹配度高，且探索结构与氛围都有突出表现，适合优先体验。
- uncertainty：基于对该作品的既有知识判断；本轮未联网核验具体版本或资料。
### candidate

- judgment：在岛屿上徒步、攀爬并与居民交谈，探索路线和小目标推动轻松旅程。题名知识判断，未经核验。
- experience_center：发现地点、帮助居民与抵达目标共同构成驱动力。
- mechanics：轻量移动和探索路线为成熟冒险模板提供短小、自由的节奏；未核验具体规则。
- innovation：小地图探索与生活化支线执行鲜明。
- narrative_role：高度贴合轻松探索、氛围、具体人物与旅途感。
- personal_interest：个人匹配强，适合优先体验。
- research_value：体量和系统复杂度较小。
- reason：仅凭题名及既有知识推断；未联网、未核验实机。
- evidence_basis：题名可识别；所有玩法判断未经外部核验。
- uncertainty：仅凭标题及既有知识推断；探索路线和居民任务未经独立核验。

## legacy-04 · 渔帆暗涌 DREDGE

审核准则：{"title": "渔帆暗涌 DREDGE", "source": ["好玩"], "result_label": "必须推荐", "reason_types": ["个人喜欢", "值得研究"], "draft_confidence": "high", "reason_detail": "神秘驱动探索，船只成长和经济结构为发现新内容提供动力。"}

### baseline

- judgment：你白天在群岛间捕鱼、接委托并升级船只，夜里面对海上异变和风险；航行、发现与不安感推动前进。
- experience_center：捕鱼、整理有限船舱、规划航线、出售渔获和升级船只构成经营循环；近似钓鱼探索与轻生存冒险，夜间风险影响路线和收益。
- mechanics：有限货舱与航行路线让捕捞、任务和风险彼此牵连；怪异主题改变探索情绪，但不是大型策略系统。
- innovation：有限船舱、航线与夜间风险共同约束捕鱼和任务安排，形成资源规划与探索的有效结合。
- narrative_role：小镇委托、海域秘密与克苏鲁式不安提供叙事氛围。
- personal_interest：夜间压力及轻恐怖元素可能不合适；操作整体不是高强度反应挑战。
- research_value：中高；航行探索、任务、资源规划和鲜明氛围相合。
- reason：有限空间装载与风险探索形成紧凑循环，表现和机制结合有分析价值。
- evidence_basis：多项个人兴趣成立，但夜间恐怖气氛和重复捕鱼可能限制持续游玩。
- uncertainty：基于对该作品的既有知识判断；本轮未联网核验循环占比或具体版本。
### candidate

- judgment：以渔船探索群岛、捕鱼并升级船只，夜间危险和神秘故事形成继续航行的牵引。题名知识判断，未经核验。
- experience_center：航行探索、捕鱼经营和谜团推进并行。
- mechanics：资源管理和航线风险结合；是否实际改变决策的细节未经核验。
- innovation：把捕鱼循环与诡异氛围、探索叙事并置。
- narrative_role：符合探索、氛围和轻经营；恐怖感程度需确认。
- personal_interest：个人体验及循环与叙事结合的研究价值。
- research_value：夜间惊悚可能不合口味；重复捕鱼风险待核。
- reason：仅凭题名及既有知识推断；未联网、未核验实机。
- evidence_basis：题名可识别；细节未经核验。
- uncertainty：仅凭标题及既有知识推断；捕鱼、航行及恐怖内容占比未经核验。

## legacy-05 · 深空梦里人2 Citizen Sleeper 2: Starward Vector

审核准则：{"title": "深空梦里人2 Citizen Sleeper 2: Starward Vector", "source": ["好玩"], "result_label": "必须推荐", "reason_types": ["个人喜欢", "值得研究"], "draft_confidence": "high", "reason_detail": "以骰子、关系、任务和生活处境组织出持续展开的叙事体验。"}

### baseline

- judgment：你在星际边缘带领一支临时队伍接活、维持生计并处理彼此的处境，科幻生存压力与人物关系构成动力。
- experience_center：以骰子资源、行动选择、任务流程和队伍状态管理推进章节；延续叙事RPG与资源管理模板，成员能力和风险要求安排有限行动。
- mechanics：据既有知识，续作扩展队伍与任务结构；相较前作，协同队伍的风险管理可能改变行动规划，但细节本轮未核验。
- innovation：续作据既有知识扩展了队伍和任务结构；行动风险如何改变决策仍待核实。
- narrative_role：人物、工作和生存压力处于宏大科幻背景中的中心。
- personal_interest：太空题材及骰子管理系统可能触及用户的题材顾虑；传统回合战斗不是主要吸引点。
- research_value：中高；人物关系和资源决策吻合，但太空题材构成明显摩擦。
- reason：可关注叙事与行动资源如何结合，以及续作队伍结构对前作循环的变化。
- evidence_basis：叙事与队伍决策值得看，但不能仅凭系列名推断变化，建议先细看。
- uncertainty：仅凭既有系列知识推断；未联网核验续作规则，创新判断低置信度。
### candidate

- judgment：骰子、行动与船员状态构成科幻生存角色扮演的日常抉择；合同和关系推动故事。题名知识判断，未经核验。
- experience_center：角色处境、任务选择与队伍关系是主要驱动。
- mechanics：骰子资源与行动机会限制构成核心决策；续作变化未经核验。
- innovation：以骰子和时间压力表达脆弱处境，值得关注。
- narrative_role：匹配叙事、人物关系、资源压力；太空题材是明确摩擦。
- personal_interest：系统叙事研究价值明显，个人题材偏好降低。
- research_value：题材可能阻碍理解；续作系统细节未确认。
- reason：仅凭题名及既有知识推断；未联网、未核验实机。
- evidence_basis：识别度较高；续作实际循环未经核验。
- uncertainty：仅凭标题及既有知识推断；续作的具体循环和改动未经核验。

## legacy-06 · 孤星寂海 In Other Waters

审核准则：{"title": "孤星寂海 In Other Waters", "source": ["好玩"], "result_label": "必须推荐", "reason_types": ["个人喜欢", "值得研究"], "draft_confidence": "high", "reason_detail": "安静、优雅、引人深入的探索体验，故事作为引导而不是压倒一切的主轴。"}

### baseline

- judgment：你像一名远程分析者陪伴外星海洋生物学家探索陌生海域，通过地图与读数逐步理解生态环境。
- experience_center：核心是操控扫描界面、标记地图、解读环境信息并指导潜水员移动；接近地图探索/科学调查叙事，界面信息本身就是主要操作。
- mechanics：相较直接操控角色的探索游戏，它把观察、制图和信息解释变成玩家活动，视听呈现刻意抽象。
- innovation：把扫描、制图和信息解释作为玩家的核心活动，改变了常见角色探索的操作方式。
- narrative_role：研究者与生物之间的关系、孤独感和生态发现构成叙事。
- personal_interest：节奏偏慢、文本阅读较多；不依赖第一人称3D探索。
- research_value：高；独特界面、探索、氛围和人物关系明确匹配。
- reason：把地图读取和环境信息组织变成玩法活动，是鲜明的形式与结构设计案例。
- evidence_basis：个人兴趣和设计价值都较突出，值得体验；慢节奏是主要限制。
- uncertainty：基于对该作品的既有知识判断；本轮未核实实际流程和具体版本。
### candidate

- judgment：以界面、扫描和航行记录探索异星海洋生态；玩家通过观察与记录逐步理解环境。题名知识判断，未经核验。
- experience_center：环境发现和科学观察构成主要牵引。
- mechanics：界面化导航把探索转换为信息读取与推断，区别于直接操控角色的冒险；未核验细节。
- innovation：以抽象界面表现生态探索，形式与活动相连。
- narrative_role：契合氛围、探索、体验引擎；太空/异星题材有所摩擦。
- personal_interest：探索表达与交互形式值得研究。
- research_value：信息阅读可能节奏偏慢；题材偏离个人偏好。
- reason：仅凭题名及既有知识推断；未联网、未核验实机。
- evidence_basis：题名可识别；玩法细节未经核验。
- uncertainty：仅凭标题及既有知识推断；界面探索和推断活动未经独立核验。

## legacy-07 · Cabernet

审核准则：{"title": "Cabernet", "source": ["好玩"], "result_label": "推荐", "reason_types": ["个人喜欢", "值得研究"], "draft_confidence": "medium", "reason_detail": "吸血鬼身份、人性选择、时间分配和二维叙事形式有吸引力，但尚未完整玩完。"}

### baseline

- judgment：标题可能指一款以吸血鬼为题材的叙事RPG，可能围绕夜间生活、人物交往和身份选择展开；仅能作谨慎猜测。
- experience_center：具体循环和决策尚不能从标题确认；若为熟悉的对话选择与角色扮演结构，主要价值可能在人物、世界和叙事情境。
- mechanics：目前无法判断规则是否超出常见叙事RPG模板，不能把题材或美术风格直接称作玩法创新。
- innovation：玩法结构未知；目前不能确认其是否超出常见叙事RPG模板。
- narrative_role：吸血鬼题材可能容纳社会关系与道德选择，但本项是推测。
- personal_interest：实际玩法、文本比重和是否存在动作/战斗循环未核实。
- research_value：中低；叙事与氛围可能相合，实际结构未知。
- reason：可作为叙事题材与机制结合的待观察对象，具体研究价值未确认。
- evidence_basis：先保守给分；可能的叙事吸引力尚不足以证明优先体验。
- uncertainty：仅按标题和既有零散知识判断，未联网核验，所有关于玩法的描述均低置信度。
### candidate

- judgment：仅有标题，无法可靠确认这是哪款游戏及其实际体验。
- experience_center：未知。
- mechanics：未知；不能据标题推断循环。
- innovation：证据不足。
- narrative_role：无法判断。
- personal_interest：暂不能判断。
- research_value：身份和玩法均未核实。
- reason：title_only，无外部查询，保留不确定性。
- evidence_basis：输入仅提供标题“Cabernet”，没有链接、平台或描述；该标题不足以确认具体作品及玩法，因此不作玩法事实判断。
- uncertainty：标题不能唯一确认具体作品；判断仅基于给定案例描述，未独立核验。

## legacy-08 · 活侠传 Legend of Mortal

审核准则：{"title": "活侠传 Legend of Mortal", "source": ["好玩"], "result_label": "推荐", "reason_types": ["个人喜欢", "值得研究"], "draft_confidence": "high", "reason_detail": "人物、路线和时间管理很有趣，但后期重复和数值化会削弱体验。"}

### baseline

- judgment：你作为武侠人物经历成长、关系和江湖冲突；据既有知识，战斗和角色养成也占有显著位置。
- experience_center：以文字叙事、选择、角色属性/养成及回合制战斗组成；接近传统武侠RPG与回合战斗模板。
- mechanics：人物成长和叙事选择有内容价值，但不能仅凭题材确认它改变传统回合战斗的决策结构。
- innovation：据既有知识，故事选择和养成突出，但传统回合战斗没有确认发生实质结构变化。
- narrative_role：角色关系、命运走向和戏剧性叙事可能是主要看点。
- personal_interest：泛武侠题材以及传统战斗结构与用户偏好存在摩擦，战斗关注度可能较高。
- research_value：中；剧情人物可能吸引，但题材与战斗循环有明显阻力。
- reason：可研究叙事、角色关系与传统战斗如何并置，但本轮不确认其特殊创新。
- evidence_basis：有叙事潜力，但未有足够证据证明个人兴趣会克服题材和战斗摩擦。
- uncertainty：基于标题及既有知识判断，未核验版本、战斗占比或叙事分支。
### candidate

- judgment：据标题知识推断为武侠题材角色扮演，可能围绕人物经历、选择与成长展开；具体主循环不确定。
- experience_center：人物和叙事可能构成动力，玩法占比未知。
- mechanics：无法确认战斗、养成和事件决策的权重。
- innovation：是否超出常见武侠养成模板证据不足。
- narrative_role：武侠题材本身不排除，但泛武侠和传统战斗存在摩擦。
- personal_interest：可能有叙事/人物价值，需核玩法。
- research_value：主循环、重复度与战斗结构未知。
- reason：仅凭题名及有限既有知识推断；未联网核验。
- evidence_basis：候选可识别，实际体验与版本未确认。
- uncertainty：根据标题和有限既有知识推断；战斗、养成及叙事占比未独立核验。

## legacy-09 · 越过阿尔卑斯山 Over the Alps

审核准则：{"title": "越过阿尔卑斯山 Over the Alps", "source": ["好玩"], "result_label": "推荐", "reason_types": ["个人喜欢", "值得研究"], "draft_confidence": "high", "reason_detail": "互动绘本形式与文本选择结合得精致，具有强烈代入感。"}

### baseline

- judgment：你在战前欧洲沿着旅程与线索推进，通过信件和选择逐渐拼出人物处境与事件真相。
- experience_center：以阅读、地点选择和分支决策构成互动叙事，接近选择驱动的旅行悬疑；地图和信件组织路线与信息。
- mechanics：地图旅行及信件式呈现带来形式辨识度，但目前没有确认其结构超出分支叙事模板。
- innovation：地图与信件组织旅行叙事，暂未确认超出常见分支冒险的玩法变化。
- narrative_role：旅途氛围、历史背景和人物秘密驱动阅读。
- personal_interest：以文本和选择为主，若不喜欢纯对话/点击冒险则需要谨慎；缺少经营或探索操作。
- research_value：中；旅途感和信件形式合拍，玩法活动较轻。
- reason：可观察地图如何承载分支叙事和旅行节奏，研究价值有限但明确。
- evidence_basis：短篇形式与氛围可能值得一试，但互动密度和文本依赖是明显限制。
- uncertainty：基于既有知识判断，未联网核验具体叙事结构或版本。
### candidate

- judgment：标题知识显示其为选择驱动的间谍故事体验；玩家通过路线或叙事选择推进旅程。具体未核验。
- experience_center：叙事推进和选择后果是可能的中心。
- mechanics：互动叙事模板，选择是否产生实质结构差异未知。
- innovation：叙事呈现方式可能有形式价值，不能确认创新。
- narrative_role：旅途、氛围和故事可能合口味；纯点击叙事是风险。
- personal_interest：叙事形式研究价值有限但明确。
- research_value：可能接近纯对话/点击冒险雷区。
- reason：仅凭题名及既有知识推断；未联网、未核验实机。
- evidence_basis：身份可识别；实际流程未经核验。
- uncertainty：根据标题和既有知识推断；选择后果及实际流程未独立核验。

## legacy-10 · 奥森弗里2：信号丢失 OXENFREE II

审核准则：{"title": "奥森弗里2：信号丢失 OXENFREE II", "source": ["好玩"], "result_label": "推荐", "reason_types": ["个人喜欢", "值得研究"], "draft_confidence": "high", "reason_detail": "闲谈、环境和对话共同构筑世界，留下了持续回想的体验。"}

### baseline

- judgment：你在海岸小镇调查异常无线电信号并与人物对话，超自然悬疑逐步压向故事。
- experience_center：主要是横向移动、探索地点、对话选择和解谜，近似叙事冒险；无线电调谐连接环境谜题与超自然事件。
- mechanics：无线电交互构成可辨识的表达方式，但主体仍是探索与对话推进，未确认足以改变成熟冒险模板的结构差异。
- innovation：无线电调谐连接环境谜题和叙事，但不足以确认改变冒险游戏的核心结构。
- narrative_role：人物对话、地方氛围与超自然悬疑是主要驱动力。
- personal_interest：用户明确不喜欢纯恐怖悬疑互动影游；本作不是单纯FMV，但悬疑恐怖色彩可能持续触雷。
- research_value：低；对话叙事虽可能合口味，主题雷区较强。
- reason：无线电与对话系统的叙事结合可供观察，但未构成足以抵消雷区的明确理由。
- evidence_basis：主要体验落在用户强烈不喜欢的悬疑题材，独立价值尚不足以推荐。
- uncertainty：基于既有知识判断，未核验恐怖强度、玩法比重及续作与前作差异。
### candidate

- judgment：标题知识推断为超自然叙事冒险，以探索场景和对话选择推进；未核验玩法比重。
- experience_center：人物对话、谜团和场景探索驱动。
- mechanics：对话打断/选择等是否改变行动结构无法在本次核实。
- innovation：无线电与对话形式可能有表达价值，续作差异未知。
- narrative_role：氛围和人物叙事合口味；超自然悬疑有一定摩擦。
- personal_interest：叙事交互研究价值。
- research_value：若主要是对话点击则兴趣有限；悬疑气质需谨慎。
- reason：仅凭题名及既有知识推断；未联网、未核验实机。
- evidence_basis：识别标题，具体版本内容未经核验。
- uncertainty：根据标题和既有知识推断；对话、探索和悬疑内容比例未独立核验。

## legacy-11 · 孤山速降 Lonely Mountains: Downhill

审核准则：{"title": "孤山速降 Lonely Mountains: Downhill", "source": ["好玩", "有意思"], "result_label": "推荐", "reason_types": ["个人喜欢", "值得研究"], "draft_confidence": "high", "reason_detail": "路线发现、环境穿行和轻技巧本身有吸引力，但高挑战限制个人游玩优先级。"}

### baseline

- judgment：你沿山路寻找下坡线路，在速度、落差和安全之间取舍，山地穿行和路线掌握带来挑战。
- experience_center：以自行车下坡、控制速度、选线和检查点重试为核心，接近技巧型竞速；路线阅读与地形穿行是关键活动。
- mechanics：相较单纯计时赛，复杂地形和多路线让空间阅读影响通行方式；但总体仍依赖反复练习与操作。
- innovation：地形路线阅读影响下坡选择，可能超出单纯计时，但整体仍属技巧挑战变奏。
- narrative_role：山野环境和骑行过程带来清静的户外氛围。
- personal_interest：单人操作挑战、摔车重来和计时目标可能命中纯反应/挑战偏好雷区。
- research_value：中低；探索路线和空间阅读有吸引力，挑战循环是明显摩擦。
- reason：可研究技巧游戏如何通过路线与环境阅读提供不同于单纯反应的决策。
- evidence_basis：存在一定空间探索价值，但主要游玩动力仍可能是反复操作挑战。
- uncertainty：基于既有知识判断，未核验路线自由度、关卡结构或实际难度。
### candidate

- judgment：以山地路线选择和自行车下坡挑战为中心；玩家反复试路线、控制速度并追求抵达。题名知识推断，未经核验。
- experience_center：空间阅读和路线发现可能与计时挑战并存。
- mechanics：技巧挑战可能主要依赖操作；路线选择的实际分量未核实。
- innovation：若路线探索超越计时成绩则有研究点，当前证据不足。
- narrative_role：山野氛围和路线探索有吸引力，纯操作挑战是风险。
- personal_interest：可关注技巧关卡如何承载探索。
- research_value：可能落入独自练习、计时排名型雷区。
- reason：仅凭题名及既有知识推断；未联网、未核验实机。
- evidence_basis：循环权重与挑战结构待验证。
- uncertainty：根据标题和既有知识推断；路线发现与计时操作各自权重未独立核验。

## legacy-12 · 舒林 Cozy Grove

审核准则：{"title": "舒林 Cozy Grove", "source": ["好玩"], "result_label": "推荐", "reason_types": ["个人喜欢", "值得研究"], "draft_confidence": "high", "reason_detail": "生活模拟和探索发现的前期体验很好，但重复日课和建设目标会消耗兴趣。"}

### baseline

- judgment：你在一座幽灵岛上每天帮助灵魂、收集物件并逐渐恢复岛屿，轻量日常和角色故事构成陪伴感。
- experience_center：以日常任务、采集、制作、装饰和与角色交谈推进；接近每日任务驱动的生活模拟，现实时间门槛和重复收集形成节奏。
- mechanics：角色故事与岛屿变化提供长期情境，但若每日活动主要重复采集，结构差异不突出。
- innovation：每日任务与角色故事相连，但未确认任务循环有明显结构创新。
- narrative_role：幽灵角色的个人故事、社区感和柔和氛围是主要价值。
- personal_interest：日常重复和现实时间限制可能令推进变得拖沓；装饰本身不是充分吸引点。
- research_value：中；人物日常与氛围匹配，循环重复是明显限制。
- reason：可观察日常任务如何串联角色叙事与持续变化，但创新不应夸大。
- evidence_basis：有人物与氛围价值，值得细看；重复日常可能削弱长线兴趣。
- uncertainty：基于既有知识判断，未核验内容更新、日常节奏和实际任务重复度。
### candidate

- judgment：标题知识推断为岛屿日常与角色任务驱动的轻经营/生活游戏；具体日课结构未经核验。
- experience_center：居民故事和逐步探索可能是继续游玩的动力。
- mechanics：日常任务、收集与区域解锁的实际重复性未知。
- innovation：无法确认规则是否实质超越常见生活模拟。
- narrative_role：日常人物和氛围合口味；重复日课及装饰偏重是风险。
- personal_interest：若角色叙事贯穿日常则有体验价值。
- research_value：可能依赖日常登录与重复收集。
- reason：仅凭题名及既有知识推断；未联网核验。
- evidence_basis：身份明确度较高，循环细节缺证。
- uncertainty：根据标题和既有知识推断；居民叙事、重复任务与日课结构未独立核验。

## legacy-13 · 深空梦里人 Citizen Sleeper

审核准则：{"title": "深空梦里人 Citizen Sleeper", "source": ["有意思"], "result_label": "推荐", "reason_types": ["值得研究"], "draft_confidence": "medium", "reason_detail": "叙事、骰子和生活处境的融合值得研究，个人游玩优先级待确认。"}

### baseline

- judgment：你作为机械身体中的流亡者在空间站寻找工作、维持生存并建立关系，生计压力和人物故事推动每个周期。
- experience_center：用骰子、有限行动与状态资源安排工作、探索和对话；接近叙事RPG与轻资源管理，行动安排决定风险和可用机会。
- mechanics：相较传统回合战斗RPG，骰子状态和行动槽把资源压力用于生活安排与任务风险，叙事选择紧贴生计循环。
- innovation：骰子和有限行动资源用于安排劳动、探索和任务风险，区别于传统战斗导向RPG。
- narrative_role：具体人物、劳动、社区和身份处境处于科幻设定中心。
- personal_interest：太空背景可能让用户难以进入系统；文本量较大。
- research_value：高但有题材摩擦；生存管理、人物关系和系统叙事强匹配。
- reason：将骰子与行动资源用于日常劳动、风险和叙事推进，呈现有辨识度的设计连接。
- evidence_basis：人物与资源循环都契合，值得体验；太空题材和文本量可能阻碍持续投入。
- uncertainty：基于既有知识判断，未联网核验实际章节流程或系统细节。
### candidate

- judgment：骰子行动与身体状态管理塑造边缘空间站上的生存日常，任务和人物关系牵引故事。题名知识判断，未经核验。
- experience_center：角色生存、工作选择和关系变化共同驱动。
- mechanics：骰子与行动周期把资源压力嵌入叙事决策；细节未经核验。
- innovation：机制将脆弱生存转成每日行动取舍。
- narrative_role：叙事、人文、资源选择契合；太空题材明显减分。
- personal_interest：系统叙事研究价值突出。
- research_value：科幻空间背景可能不合偏好。
- reason：仅凭题名及既有知识推断；未联网、未核验实机。
- evidence_basis：题名可识别；没有本次外部复核。
- uncertainty：根据标题和既有知识推断；骰子行动及关系系统细节未独立核验。

## legacy-14 · 文明6 Sid Meier's Civilization VI

审核准则：{"title": "文明6 Sid Meier's Civilization VI", "source": ["好玩", "有意思"], "result_label": "推荐", "reason_types": ["个人喜欢", "值得研究"], "draft_confidence": "high", "reason_detail": "多种胜利方式、长程决策和复利系统会生成具体故事；多人情境进一步增强体验，但单人优先级较低。"}

### baseline

- judgment：你带领文明跨越时代，扩张城市、发展科技文化并与其他文明竞争，长期规划和世界演化是驱动。
- experience_center：回合制4X策略，围绕城市区划、资源、科技、外交和战争管理；成熟的宏观历史策略模板。
- mechanics：区划与地形相邻等规则影响城市布局和长期规划，但整体仍是宏观数值优化与竞争路线。
- innovation：区划与地形关系影响城市布局，是4X模板中的策略变奏，不改变其宏观竞争主轴。
- narrative_role：文明演变与地图探索提供历史主题和系统涌现。
- personal_interest：长局、复杂系统和宏观数值优化正是用户通常不想玩的历史策略形态。
- research_value：低；策略取舍存在，但主要游玩情境与明确偏好冲突。
- reason：作为4X系统与策略路线设计有研究价值，但不够鲜明到单凭研究价值推荐。
- evidence_basis：主要循环与用户明确不喜欢的复杂历史策略高度重合。
- uncertainty：基于既有知识判断，未核验扩展内容或多人情境。
### candidate

- judgment：以回合制扩张文明、经营城市、研究科技和外交竞争为循环；长期路线和系统后果产生局势故事。标题知识推断，未经核验。
- experience_center：长期发展路线与局势变化是中心。
- mechanics：传统宏观策略模板；具体胜利路线带来长期决策，但是否符合个人偏好不确定。
- innovation：文明发展系统可供策略设计研究，未主张新活动。
- narrative_role：复杂历史策略是摩擦；涌现故事和长线选择又有明确价值。
- personal_interest：系统策略与涌现叙事研究价值。
- research_value：宏观优化和复杂操作可能消耗兴趣。
- reason：仅凭题名及既有知识推断；未联网、未核验实机。
- evidence_basis：题名可识别，版本和实玩体验未经核验。
- uncertainty：根据标题和既有知识推断；具体版本、规则体验与个人适配未经独立核验。

## legacy-15 · 节奏光剑 Beat Saber

审核准则：{"title": "节奏光剑 Beat Saber", "source": ["好玩"], "result_label": "推荐", "reason_types": ["个人喜欢", "身体性体验"], "draft_confidence": "high", "reason_detail": "节奏操作服务于音乐、身体参与和即时沉浸，不应只按独自攻关型的纯反应挑战判断。"}

### baseline

- judgment：你随着音乐挥动光剑切割迎面节拍，在身体动作、节奏和准确性中获得参与感，适合VR与音乐体验情境。
- experience_center：按节拍挥砍方块、躲避障碍并匹配方向；属于节奏动作游戏，音乐结构决定动作序列和身体表达。
- mechanics：相较传统节奏按键输入，VR空间挥砍将身体位置与方向纳入操作；这是输入与身体参与的实质变化。
- innovation：VR挥砍将身体位置和动作方向纳入节奏输入，是输入方式上的实质变化。
- narrative_role：音乐、动作和沉浸式身体体验是核心价值。
- personal_interest：高难度与成绩追逐会变成重复练习；需要VR设备并适合愿意活动的场景。
- research_value：中高；社交/身体体验有独立价值，但需VR和合适的身体情境。
- reason：可研究空间化节奏输入怎样改变玩家动作与音乐参与，形式结构清楚。
- evidence_basis：作为身体性音乐体验值得推荐，但未必适合单人长期游戏。
- uncertainty：基于对作品类型的既有知识判断，未核验歌曲库、设备条件或版本。
### candidate

- judgment：玩家随音乐挥动双手切割节拍目标，主要价值在身体参与、音乐同步和挑战。题名知识判断，未经核验。
- experience_center：音乐与身体动作构成直接体验中心。
- mechanics：节奏动作模板以体感与音乐反馈成立；未核验曲库等细节。
- innovation：身体化节奏反馈有明确形式价值。
- narrative_role：社交/身体性可独立成立；单人刷分挑战偏好较低。
- personal_interest：体感交互和音乐动作设计研究价值。
- research_value：可能主要变成重复练习与成绩挑战。
- reason：仅凭题名及既有知识推断；未联网、未核验实机。
- evidence_basis：体验成立情境和设备信息未核验。
- uncertainty：根据标题和既有知识推断；设备、曲库及实际成立情境未经独立核验。

## legacy-16 · Just Dance

审核准则：{"title": "Just Dance", "source": ["好玩"], "result_label": "推荐", "reason_types": ["个人喜欢", "社交情境", "身体性体验"], "draft_confidence": "high", "reason_detail": "音乐、身体表达、共同表演和聚会参与构成主要价值；动作是社交体验的媒介。"}

### baseline

- judgment：你跟随音乐和屏幕舞者一起动作，可独自活动也可在聚会中轮流表演，主要乐趣来自身体参与和共同气氛。
- experience_center：跟随编舞节奏动作并获得反馈，属于舞蹈/节奏游戏；具体识别方式因版本与平台不同。
- mechanics：以身体舞蹈而非手柄按键构成主要输入，价值依赖音乐曲目、动作表达和共同参与，不应按纯个人成绩挑战评判。
- innovation：舞蹈动作取代传统按键输入，体验创新主要成立于身体参与和社交情境。
- narrative_role：音乐、舞蹈、共同表演和聚会氛围构成情境价值。
- personal_interest：需要合适空间、曲目和参与者；独自长期游玩的叙事及探索较弱。
- research_value：中；在聚会/身体活动场景成立，个人长期兴趣较不确定。
- reason：值得从身体交互与多人参与设计角度研究，具体版本差异待核实。
- evidence_basis：社交情境和身体表达有明确价值，但不是优先的单人游戏推荐。
- uncertainty：基于系列常见玩法判断；未核验具体版本、平台及订阅/曲目情况。
### candidate

- judgment：跟随屏幕舞蹈动作配合音乐，聚会和共同表演是主要价值。题名泛指系列，具体版本未知。
- experience_center：身体表达、音乐和多人参与驱动。
- mechanics：动作模仿与评分构成循环；社交情境改变其价值。
- innovation：舞蹈游戏的共同表演形式有独立价值。
- narrative_role：聚会/身体体验契合偏好，独自刷分不一定合适。
- personal_interest：情境价值成立。
- research_value：版本不明；单人重复挑战吸引力有限。
- reason：仅凭系列标题知识推断；未联网核验。
- evidence_basis：具体作品身份与曲目/功能未知。
- uncertainty：系列标题未指明具体版本；玩法功能和曲目情境未经独立核验。

## legacy-17 · 边缘世界 RimWorld

审核准则：{"title": "边缘世界 RimWorld", "source": ["有意思"], "result_label": "推荐", "reason_types": ["值得研究"], "draft_confidence": "high", "reason_detail": "故事模拟器和系统涌现具有重要研究价值，但复杂经营未必是个人游玩偏好。"}

### baseline

- judgment：你管理一群坠落者在陌生星球建立据点，环境危机、人物特质和突发事件不断把计划变成个人故事。
- experience_center：殖民地经营、资源生产、建筑、医疗、防御和角色任务构成循环；接近生存殖民地模拟，叙事由系统事件和人物状态涌现。
- mechanics：人物特质、关系、伤病与随机事件持续改变经营决策，使宏观管理生成具体的生存故事，而非单纯资源表格。
- innovation：人物特质、关系与随机危机共同影响经营决策，使管理循环生成涌现故事。
- narrative_role：群体日常、关系冲突和危机共同形成涌现叙事。
- personal_interest：太空题材触及用户的明确顾虑；复杂系统、战斗和持续管理可能造成负担。
- research_value：中高；系统故事和经营取舍匹配，但太空题材是主要摩擦。
- reason：系统状态如何生成个体故事、策略如何嵌入日常管理，研究价值鲜明。
- evidence_basis：涌现故事和经营系统值得点开研究，但个人长期游玩意愿可能受题材阻碍。
- uncertainty：基于既有知识判断，未核验不同版本、模组或实际系统规模。
### candidate

- judgment：玩家管理殖民地居民、资源和突发事件，系统交互持续生成生存局势与人物故事。题名知识判断，未经核验。
- experience_center：殖民地发展与居民遭遇共同成为目标。
- mechanics：殖民模拟通过需求、事件和资源互相作用形成涌现后果；细节未核。
- innovation：系统组合和故事生成值得研究。
- narrative_role：经营取舍、长期决策和生活故事高度贴合。
- personal_interest：个人系统体验及涌现叙事研究价值高。
- research_value：系统学习成本与管理压力可能较高。
- reason：仅凭题名及既有知识推断；未联网、未核验实机。
- evidence_basis：可识别游戏；玩法判断非本次实证。
- uncertainty：根据标题和既有知识推断；居民系统、事件循环及管理压力未经独立核验。

## legacy-18 · 超越光速 FTL: Faster Than Light

审核准则：{"title": "超越光速 FTL: Faster Than Light", "source": ["有意思"], "result_label": "推荐", "reason_types": ["值得研究"], "draft_confidence": "high", "reason_detail": "资源压力、路线选择和危机决策是策略设计的重要参考。"}

### baseline

- judgment：你驾驶飞船穿过逐渐逼近的敌军，在有限燃料、船员和设备下决定航线与生存策略。
- experience_center：暂停式实时飞船管理、房间供电、船员调度、武器控制、航线选择和随机事件构成循环；属于轻量太空策略/roguelike。
- mechanics：局部船内危机、供电分配和航线风险要求短期战术与长期资源同步权衡，失败重开形成高压结构。
- innovation：船舱供电、船员调度和航线风险构成紧凑的策略组合，仍属于太空策略模板。
- narrative_role：事件文本和船员危机偶尔生成小故事，系统决策是主要驱动。
- personal_interest：太空策略题材和反复失败重开可能明显不合口味；故事不是稳定主轴。
- research_value：中低；策略系统有意思，但题材触及明确雷区。
- reason：船内局势、供电与航线风险的组合值得研究其危机节奏。
- evidence_basis：有清楚的系统设计价值，但用户明确的太空策略顾虑压低推荐强度。
- uncertainty：基于既有知识判断，未核验学习曲线、版本或内容扩展。
### candidate

- judgment：操控飞船穿越危机航段，分配船员、能源与舱室并应对战斗和随机事件。题名知识判断，未经核验。
- experience_center：风险决策和船员/飞船存续形成局势故事。
- mechanics：实时暂停战术与随机资源压力构成循环；太空战斗是明显摩擦。
- innovation：资源分配与危机组合值得研究，但不夸大创新。
- narrative_role：策略选择和涌现故事契合，太空题材和战斗可能劝退。
- personal_interest：系统策略研究价值成立。
- research_value：太空策略属于明确低兴趣项；失败循环或带来压力。
- reason：仅凭题名及既有知识推断；未联网、未核验实机。
- evidence_basis：标题可识别，循环细节未经核验。
- uncertainty：根据标题和既有知识推断；随机事件、战斗及资源循环未经独立核验。

## legacy-19 · 勇者斗恶龙：创世小玩家2

审核准则：{"title": "勇者斗恶龙：创世小玩家2", "source": ["有意思"], "result_label": "推荐", "reason_types": ["值得研究"], "draft_confidence": "medium", "reason_detail": "生活模拟、建造和多人体验有研究价值，但个人对长期建设的兴趣有限。"}

### baseline

- judgment：你在岛屿间帮助居民重建社区、探索遗迹并逐步发展据点，建造和人物任务共同提供推进感。
- experience_center：以方块建造、资源采集、探索、任务和轻量动作战斗构成；接近任务驱动的沙盒建造RPG，居民需求会引导设施用途。
- mechanics：相较自由建造沙盒，章节任务和居民需求把建筑活动嵌入有目标的社区建设与探索；战斗是外围而非唯一核心。
- innovation：居民需求与章节任务引导建造用途，把沙盒建造嵌入目标驱动的社区发展。
- narrative_role：人物日常、社区恢复与岛屿探索使建造服务于关系和故事。
- personal_interest：建造采集仍占很多时间，若后期重复收集或偏好传统战斗可能降低兴趣。
- research_value：高；探索、任务、生活模拟与有目的建造契合。
- reason：任务如何转化为建筑需求、居民如何使用空间，构成明确的类型组合价值。
- evidence_basis：社区建造与探索均可能吸引，个人匹配度高，适合推荐。
- uncertainty：基于既有系列知识判断，未核验本作后期节奏、版本差异或战斗比重。
### candidate

- judgment：标题知识推断为方块建造与任务冒险结合，玩家收集材料、建造设施并帮助居民。
- experience_center：居民目标和岛屿发展可能驱动持续投入。
- mechanics：建造任务及资源收集循环；是否超出装修/采集套路未知。
- innovation：若居民需求改变建造目标，存在系统叙事价值，未核实。
- narrative_role：任务、社区和生活模拟有吸引力；重复收集与建造偏重是风险。
- personal_interest：居民与建造任务结合值得观察。
- research_value：系列编号对应版本细节未查；收集可能重复。
- reason：仅凭题名及既有知识推断；未联网核验。
- evidence_basis：本地化标题可识别，具体玩法比例未核验。
- uncertainty：根据标题和既有知识推断；具体版本、居民任务与收集重复度未经独立核验。

## legacy-20 · 司辰之书 BOOK OF HOURS

审核准则：{"title": "司辰之书 BOOK OF HOURS", "source": ["有意思"], "result_label": "推荐", "reason_types": ["值得研究"], "draft_confidence": "high", "reason_detail": "机制、叙事和图书馆概念融合得有趣，但交互可理解性和试错成本明显。"}

### baseline

- judgment：你接手一座神秘图书馆，通过整理书籍、学习知识和修复场所逐步理解其历史与隐秘秩序。
- experience_center：以时间/行动安排、资源、物品组合、读书研究和空间修复推进；接近知识管理与探索式经营，信息分类和配方理解是主要决策。
- mechanics：相较传统经营，知识本身可解锁行动和解释世界；物品组合与时间安排构成密集系统，但实际学习成本较高。
- innovation：阅读获得的知识可解锁行动与解释世界，使知识整理成为系统资源。
- narrative_role：图书馆、档案和神秘学氛围形成鲜明场所感，叙事依靠发现与文本。
- personal_interest：系统复杂、文本阅读多、引导有限；可能接近纯数值/配方优化的边缘。
- research_value：高；档案、探索、知识系统与氛围高度契合。
- reason：把阅读与知识整理做成行动资源，是值得研究的机制表达；需要确认自己能接受系统学习。
- evidence_basis：强氛围和独特知识循环值得细看，但复杂度和文本量构成明显门槛。
- uncertainty：基于既有知识判断，未核验更新后的系统、引导和实际节奏。
### candidate

- judgment：标题知识推断为神秘图书馆管理与文本/知识整理体验；主循环及时间资源规则未核实。
- experience_center：探索知识与维护场所可能是主要动力。
- mechanics：标题无法确认它是管理、解谜还是文本系统的具体权重。
- innovation：知识组织若影响行动决策可能值得研究，证据不足。
- narrative_role：氛围、档案式探索符合偏好；若只是复杂整理则有风险。
- personal_interest：形式与知识系统潜在研究价值。
- research_value：实际活动未知，保守评分。
- reason：仅凭题名及既有知识推断；未联网、未核验实机。
- evidence_basis：身份可识别，具体机制未经核验。
- uncertainty：根据标题和既有知识推断；知识系统、时间规则及管理循环未经独立核验。

## legacy-21 · 密教模拟器 Cultist Simulator

审核准则：{"title": "密教模拟器 Cultist Simulator", "source": ["有意思"], "result_label": "推荐", "reason_types": ["值得研究"], "draft_confidence": "high", "reason_detail": "把卡牌外形转化为独特对象和组合关系，是体验引擎设计的研究案例。"}

### baseline

- judgment：你在神秘伦敦经营一套隐秘生活，通过工作、阅读和仪式追逐知识，同时承担饥饿、危险与暴露风险。
- experience_center：以卡牌槽位、定时行动、资源组合和文本事件构成循环；接近叙事驱动的资源管理/卡牌桌面模拟。
- mechanics：卡牌并非传统对战，而是把时间、工作、欲望与知识编排成行动流程；发现配方和后果需要试错。
- innovation：卡牌槽位用于编排时间、工作和知识行动，而非传统卡牌对战。
- narrative_role：神秘氛围、文本碎片和隐秘社群是核心表达。
- personal_interest：信息不透明、失败惩罚和反复试验可能令人挫败；主题晦涩，玩法偏资源组合。
- research_value：中；氛围与体验引擎相合，但可读性和挫败感明显。
- reason：将叙事线索与卡牌行动组合，值得分析其信息揭示和试错结构。
- evidence_basis：卡牌用于非战斗资源安排是有趣差异，但不透明系统使个人体验不确定。
- uncertainty：基于既有知识判断，未核验难度调整、版本和具体失败循环。
### candidate

- judgment：标题知识推断为卡牌/槽位驱动的神秘学资源与时间管理，玩家组合行动、承担风险并追寻秘密。
- experience_center：发现和系统实验推动投入。
- mechanics：卡牌槽位的时间资源管理不同于常规战斗卡牌，但具体体验未经核验。
- innovation：以卡牌组织行动和叙事信息可能构成形式变奏。
- narrative_role：神秘氛围和系统探索有吸引力；不透明规则与重复试错是风险。
- personal_interest：机制表达及叙事系统值得研究。
- research_value：学习成本、不透明和重复循环可能摩擦明显。
- reason：仅凭题名及既有知识推断；未联网核验。
- evidence_basis：玩法形态高层可识别，细节未查。
- uncertainty：根据标题和既有知识推断；卡牌行动、试错和叙事结构未经独立核验。

## legacy-22 · 肖普叔叔的火箭商店 Uncle Chop's Rocket Shop

审核准则：{"title": "肖普叔叔的火箭商店 Uncle Chop's Rocket Shop", "source": ["有意思"], "result_label": "推荐", "reason_types": ["值得研究"], "draft_confidence": "high", "reason_detail": "小店交互、工具质感、声音和经济结构的累积具有直接设计参考价值。"}

### baseline

- judgment：你在荒诞太空维修店接待顾客、拆解故障并在时间与资金压力下完成修理，日常劳动逐渐显出怪诞气质。
- experience_center：据标题的既有知识，循环涉及检查故障、使用工具维修部件、处理订单和管理时间/金钱；接近维修模拟与轻度经营。
- mechanics：若维修操作要求诊断部件状态并按步骤拆装，会不同于普通点选经营；本轮未核实具体故障规则和决策变化。
- innovation：维修活动可能包含故障诊断和工具操作，但本轮无法确认具体规则是否构成结构创新。
- narrative_role：反复工作、顾客和荒诞科幻背景可能形成黑色幽默与生活感。
- personal_interest：太空题材触及用户顾虑，时间压力和重复维修可能成为摩擦。
- research_value：中；维修工作和经营压力可能契合，但太空背景与循环重复有风险。
- reason：值得核验维修诊断是否形成新的操作问题；不能只凭商店题材断言创新。
- evidence_basis：有潜在的实质操作活动和情境价值，保守推荐并要求先看实际流程。
- uncertainty：仅凭标题及既有知识推测，未联网核验循环、规则细节或内容质量；置信度低。
### candidate

- judgment：仅凭标题无法可靠确认具体游戏身份及经营/维修循环。
- experience_center：未知。
- mechanics：未知。
- innovation：证据不足。
- narrative_role：无法判断。
- personal_interest：暂不能判断。
- research_value：不得根据名字猜测维修玩法。
- reason：title_only，无外部查询；身份及实际主循环未核实。
- evidence_basis：输入仅提供中英文标题，没有玩法描述或出处；标题不能独立证实经营/维修循环，本项身份和循环判断均未核验。
- uncertainty：标题不能可靠确认具体作品或维修循环；判断仅基于给定案例描述，未独立核验。

## legacy-23 · 俄勒冈之旅 The Oregon Trail

审核准则：{"title": "俄勒冈之旅 The Oregon Trail", "source": ["有意思"], "result_label": "推荐", "reason_types": ["值得研究"], "draft_confidence": "high", "reason_detail": "机制清晰地把旅途、资源、事件和人物故事组织在一起。"}

### baseline

- judgment：你带领一支队伍穿越漫长路线，在食物、时间、疾病、天气和行进速度之间做取舍，旅途事件决定生存状态。
- experience_center：以路线推进、资源分配、事件选择和队伍状态管理为核心；接近旅行生存模拟与历史教育游戏。
- mechanics：旅途资源与随机事件让时间、补给和风险互相牵连；不同版本可能有显著差异，不能确定具体规则。
- innovation：补给、队伍状态和随机事件形成旅程资源决策；不同版本设计可能不同。
- narrative_role：队伍成员和旅途经历形成小型故事，旅行本身是体验框架。
- personal_interest：旧版可能表现简陋或主要依靠数值管理；版本未知，无法判断美术和重复程度。
- research_value：中；旅行、资源选择和事件叙事合拍，但版本不确定。
- reason：旅程中资源决策与事件故事的结合值得关注，具体设计价值需按版本判断。
- evidence_basis：有明确题材和选择价值，但版本差异及实际呈现限制优先推荐。
- uncertainty：标题指向多个历史版本/新作，未核实用户所指具体作品；判断置信度低。
### candidate

- judgment：标题对应多个版本；通常以迁徙旅程中的补给、风险和事件选择为核心，但具体版本未知。
- experience_center：旅途推进与队伍存续带来目标感。
- mechanics：资源管理和随机事件可能产生选择后果；版本差异大。
- innovation：无法将某版本的设计变化归于此标题。
- narrative_role：旅行、资源取舍、历史生活处境有潜在匹配。
- personal_interest：系统叙事和历史游戏研究价值可能成立。
- research_value：版本不明，可能与传统教育游戏差异很大。
- reason：基于系列常识推断，未经核验；不视为具体版本实机资料。
- evidence_basis：标题同名版本繁多，结论置信度低。
- uncertainty：标题可能对应多个版本；判断仅基于系列层面的既有知识，未独立核验具体版本。

## legacy-24 · 苏丹的游戏 Sultan's Game

审核准则：{"title": "苏丹的游戏 Sultan's Game", "source": ["有意思"], "result_label": "推荐", "reason_types": ["值得研究", "明确雷区"], "draft_confidence": "high", "reason_detail": "虽然复杂、繁琐且不一定适合个人长期游玩，但它的故事结构、卡牌对象和组合设计具有明确研究价值，因此应该被推荐并注明主要限制。"}

### baseline

- judgment：你在宫廷权力环境中按周期完成苏丹下达的危险要求，在资源、角色命运和道德妥协间周旋。
- experience_center：据既有零散知识，玩法可能围绕卡牌/人物安排、周期目标和事件选择；传统战斗是否为核心及实际循环仍需验证。
- mechanics：可能通过限时任务与人物处境形成结构压力，但具体机制相对成熟还是有实质变化，标题不足以判定。
- innovation：周期目标和人物处境可能形成决策压力，具体规则差异尚未确认。
- narrative_role：宫廷生活、权力压力和人物选择可能提供叙事与制度情境。
- personal_interest：若主要采用传统卡牌战斗或重复数值构筑，将触及用户雷区；实际占比未知。
- research_value：中；制度选择和人物处境可能合拍，但玩法与战斗比重不确定。
- reason：有待观察卡牌/任务如何影响人物和后果，不能只因题材黑暗就认定创新。
- evidence_basis：保守推荐以便点开了解，但尚无依据判断是否适合实际游玩。
- uncertainty：基于标题和有限既有知识判断，未核验规则、版本或核心玩法，置信度低。
### candidate

- judgment：仅凭标题不能可靠确认其当前具体玩法与身份细节。
- experience_center：未知。
- mechanics：未知，不凭题名推断卡牌/选择循环。
- innovation：证据不足。
- narrative_role：无法判断。
- personal_interest：暂不能判断。
- research_value：不据可能的宣传描述猜测。
- reason：title_only，未联网核验；主循环未确认。
- evidence_basis：输入仅提供中英文标题，没有玩法证据；对身份和实际循环不作确定判断，且未独立核验。
- uncertainty：标题不能可靠确认具体作品和玩法；判断仅基于给定案例描述，未独立核验。

## legacy-25 · 勇者斗恶龙7 重制版

审核准则：{"title": "勇者斗恶龙7 重制版", "source": ["有意思"], "result_label": "推荐", "reason_types": ["值得研究", "画风启发"], "draft_confidence": "high", "reason_detail": "叙事节奏存在问题，但画面、UI、手感和局部故事仍具有启发性，属于应该推荐但必须说明限制的案例。"}

### baseline

- judgment：你在一系列岛屿与时代中寻找失落世界并帮助当地居民，长篇冒险与区域故事推动进程。
- experience_center：据系列/原作知识，属于传统日式RPG，含队伍成长、探索、任务与回合制战斗；重制版细节可能调整。
- mechanics：区域/时代故事与世界逐步展开是结构亮点，但战斗模板仍传统；不能凭重制名称推断创新。
- innovation：长篇区域故事与时代推进提供结构，但传统回合制战斗仍是成熟模板。
- narrative_role：地方故事、伙伴旅程和长线世界探索可能提供叙事牵引。
- personal_interest：传统回合制战斗与长流程是明显摩擦；用户对故事和世界质量接受度可提高兴趣。
- research_value：中；探索与章节故事有匹配，战斗模式和时长降低投入意愿。
- reason：可关注重制如何调整经典长篇结构与区域叙事，但版本玩法差异未知。
- evidence_basis：有叙事和探索价值，可能值得细看；传统战斗不支持强推荐。
- uncertainty：基于原作与系列知识推测，重制版具体内容、发行状态和改动未核验。
### candidate

- judgment：标题指向重制作品，但无法从冻结输入确认具体发行版本及其玩法改动。
- experience_center：原作系列身份不足以确认重制版体验。
- mechanics：未知重制版是否调整战斗、探索或结构。
- innovation：不能把原版机制直接当作重制版证据。
- narrative_role：传统回合战斗可能有摩擦，但不能据此定论版本。
- personal_interest：暂不能判断重制版价值。
- research_value：身份/版本与改动未知。
- reason：仅凭标题；无联网核验，明确保留不确定性。
- evidence_basis：输入只有《勇者斗恶龙7 重制版》标题；没有发行方、平台或重制内容说明，无法确认具体版本和玩法改动。
- uncertainty：无法确认重制版的具体发行版本及改动；判断仅基于给定案例描述，未独立核验。

## legacy-26 · Gathera

审核准则：{"title": "Gathera", "source": ["taste", "游戏库"], "result_label": "不推荐", "reason_types": ["明确雷区"], "draft_confidence": "high", "reason_detail": "温馨主题无法改变生存、制作、建造和多人沙盒的核心。"}

### baseline

- judgment：标题无法可靠指向具体作品，无法描述玩家处境或体验驱动力。
- experience_center：主循环、成熟模板和决策方式均无法从名称确认。
- mechanics：无从判断是否改变玩家活动或决策，不对创新作推断。
- innovation：无法确认具体游戏和规则，不能判断活动或决策是否有实质创新。
- narrative_role：题材、叙事和氛围未知。
- personal_interest：同名可能性与类型未知，无法评估限制。
- research_value：无法判断个人匹配度。
- reason：无法指出可研究的设计对象。
- evidence_basis：仅凭名称不足以作出有依据的推荐判断。
- uncertainty：仅凭标题无法确认具体游戏或玩法；本轮未联网核验。
### candidate

- judgment：标题无法唯一对应已知游戏，不能判断玩家活动。
- experience_center：未知。
- mechanics：未知。
- innovation：证据不足。
- narrative_role：无法判断。
- personal_interest：暂不能判断。
- research_value：不虚构玩法或证据。
- reason：title_only，无外部查询；身份不确定。
- evidence_basis：输入仅提供“Gathera”标题，无平台、开发者或玩法描述；无法据此唯一识别作品，未独立核验。
- uncertainty：标题无法唯一确认作品身份；判断仅基于给定案例描述，未独立核验。

## legacy-27 · Project Cobalt

审核准则：{"title": "Project Cobalt", "source": ["taste", "游戏库"], "result_label": "不推荐", "reason_types": ["明确雷区"], "draft_confidence": "high", "reason_detail": "采集、制作、狩猎和基地建设构成典型生存沙盒。"}

### baseline

- judgment：这是项目代号式标题，不能确认对应的具体作品或玩家体验。
- experience_center：实际操作循环、玩法类型和决策结构未知。
- mechanics：无依据判断规则差异或创新。
- innovation：项目代号无法确认具体游戏，创新与玩法均未知。
- narrative_role：人物、叙事与氛围未知。
- personal_interest：正式名称、发行状态和玩法均未确认。
- research_value：无法判断。
- reason：无法确认研究对象。
- evidence_basis：项目代号可能对应不同作品，不能以猜测代替判断。
- uncertainty：仅凭标题无法确认具体游戏或实际主循环；本轮未联网核验。
### candidate

- judgment：项目代号可能对应多个项目；冻结输入没有平台或开发者信息。
- experience_center：未知。
- mechanics：未知。
- innovation：证据不足。
- narrative_role：无法判断。
- personal_interest：暂不能判断。
- research_value：不把项目代号当作已发行游戏。
- reason：title_only，身份和发行状态均未核实。
- evidence_basis：输入仅提供“Project Cobalt”项目名称，无平台、开发者或描述；项目身份、发行状态和玩法均未核验。
- uncertainty：项目代号无法确认作品身份、发行状态或玩法；判断仅基于给定案例描述，未独立核验。

## legacy-28 · 元素巫师 Elemental Witches

审核准则：{"title": "元素巫师 Elemental Witches", "source": ["taste", "游戏库"], "result_label": "不推荐", "reason_types": ["明确雷区"], "draft_confidence": "high", "reason_detail": "本质是幸存者式自动攻击、敌潮和数值构筑，题材包装不改变核心。"}

### baseline

- judgment：名称可能对应多种游戏，无法确认玩家处境和体验驱动力。
- experience_center：无法确定它是动作、策略、卡牌、叙事或其他类型。
- mechanics：不能从元素/巫师题材推断实际规则创新。
- innovation：不能从元素/巫师题材推断新的活动或决策问题。
- narrative_role：故事与氛围未知。
- personal_interest：核心玩法、战斗比重和美术质量均未核实。
- research_value：无法判断。
- reason：暂无可确认的设计问题可供研究。
- evidence_basis：题材名称不足以支撑推荐。
- uncertainty：仅凭标题无法确认具体作品和循环；未联网核验。
### candidate

- judgment：标题不足以确认具体作品或其实际主循环。
- experience_center：未知。
- mechanics：未知。
- innovation：证据不足。
- narrative_role：无法判断。
- personal_interest：暂不能判断。
- research_value：不能从题材词推出玩法。
- reason：title_only，未联网；身份与玩法待确认。
- evidence_basis：输入仅提供中英文标题，无来源或玩法描述；题材词不能证实具体作品及其主循环，未独立核验。
- uncertainty：标题不足以确认作品身份和主循环；判断仅基于给定案例描述，未独立核验。

## legacy-29 · 噬血代码II 终极版

审核准则：{"title": "噬血代码II 终极版", "source": ["taste", "游戏库"], "result_label": "不推荐", "reason_types": ["明确雷区"], "draft_confidence": "high", "reason_detail": "类魂战斗、闪避、Boss攻坚和重复试错是不可绕开的主循环。"}

### baseline

- judgment：标题指向以吸血鬼/末世战斗为题材的动作角色扮演续作，玩家大概率主要面对近战战斗与强敌。
- experience_center：据系列既有知识，核心接近类魂动作RPG：观察敌人、闪避/防御、掌握攻击时机、升级装备并反复挑战。
- mechanics：伙伴或职业系统可能调整战斗配置，但未见证据表明它改变类魂核心活动和失败循环。
- innovation：按系列知识，伙伴或职业配置可能调整战斗方式，但未确认改变类魂核心循环。
- narrative_role：末世世界观与角色故事可能有表现价值。
- personal_interest：类魂战斗是用户明确的无条件否决项；数值成长与Boss挑战无法抵消。
- research_value：极低；核心操作正中明确雷区。
- reason：系列战斗与伙伴系统可作类型研究，但不构成足够强的独立理由。
- evidence_basis：核心战斗循环命中无条件否决项，明确不推荐游玩。
- uncertainty：仅基于标题和系列知识判断；未核实本作是否为正式作品、版本名称或实际玩法。
### candidate

- judgment：标题包含续作/版本称谓，但无法确认其为正式发行游戏或具体版本。
- experience_center：未知。
- mechanics：未知；不能因系列名推断战斗循环。
- innovation：证据不足。
- narrative_role：若是类魂战斗会触及硬雷区，但当前不能确认。
- personal_interest：暂不能判断。
- research_value：标题身份和发行信息不明。
- reason：title_only，未联网核验；不当作真实发行游戏或实机资料。
- evidence_basis：输入仅提供包含续作/版本称谓的标题，无发行或版本依据；未确认其为正式作品，也未据系列联想推断玩法。
- uncertainty：无法确认作品身份、发行状态或具体版本；判断仅基于给定案例描述，未独立核验。

## legacy-30 · 书店增量 Bookstore Incremental

审核准则：{"title": "书店增量 Bookstore Incremental", "source": ["taste", "游戏库"], "result_label": "不推荐", "reason_types": ["明确雷区"], "draft_confidence": "high", "reason_detail": "书店只是增量放置的表现层，核心是等待收益和优化数值。"}

### baseline

- judgment：你经营一家书店并逐步扩大收入，但从标题看，体验可能以持续增长数字和升级为主。
- experience_center：若名称准确，核心会是点击/放置增量、收益购买升级与自动增长；决策可能集中于收益效率。
- mechanics：目前看不出新的书店活动或经营问题，题材本身不等于实质玩法变化。
- innovation：标题可能指向增量循环，暂未发现具体新活动或决策结构的证据。
- narrative_role：书店主题可能带来轻松氛围，但人物、故事和社区价值未确认。
- personal_interest：增量放置和纯收益优化与用户明确不喜欢的模式接近。
- research_value：低；题材潜力无法弥补可能的数字增长主循环。
- reason：若实际引入读者、书目或社区决策会值得再看，目前无证据。
- evidence_basis：标题指向的循环很可能主要是数值增长，缺少独立价值。
- uncertainty：基于标题作保守推断，未联网核验玩法；如名称对应特殊作品，判断可能改变。
### candidate

- judgment：标题只能暗示增量类书店题材，不能确认其是否为具体可识别作品或实际玩法。
- experience_center：未知。
- mechanics：未知；不据“增量”一词推断完整循环。
- innovation：证据不足。
- narrative_role：纯数值增量可能不合口味，但尚无确认依据。
- personal_interest：暂不能判断。
- research_value：身份、内容与重复程度不明。
- reason：title_only，未联网；标题暗示不等于事实。
- evidence_basis：输入仅提供中英文标题；“Incremental”一词不能单独证实作品身份、玩法内容或循环，均未独立核验。
- uncertainty：标题不足以确认具体作品及其循环；判断仅基于给定案例描述，未独立核验。

## legacy-31 · 破碎怪谈 切勿欺骗

审核准则：{"title": "破碎怪谈 切勿欺骗", "source": ["taste", "游戏库"], "result_label": "不推荐", "reason_types": ["明确雷区"], "draft_confidence": "high", "reason_detail": "第一人称心理恐怖和求生调查直接命中明确雷区。"}

### baseline

- judgment：标题像一款以恐怖悬疑和欺骗为主题的叙事/解谜作品，玩家可能在不可靠信息中推进故事。
- experience_center：无法确认具体视角和操作；若为常见恐怖叙事冒险，循环可能以探索线索、解谜和揭示真相为主。
- mechanics：具体规则是否改变玩家判断和信息处理尚未确认，不能只凭标题称为创新。
- innovation：无法确认游戏与机制；恐怖主题标题不能作为玩法创新证据。
- narrative_role：恐怖悬疑似乎是核心题材，叙事可能依赖秘密与危险。
- personal_interest：用户明确厌恶纯恐怖悬疑互动影游及第一人称恐怖；视角和恐怖强度未知。
- research_value：低；潜在题材雷区明显，且玩法信息不足。
- reason：不可靠信息可能形成值得研究的叙事手法，但目前只是标题联想。
- evidence_basis：在无法确认主题强度和玩法的情况下，不应推荐用户冒险尝试。
- uncertainty：仅据标题推断，未确认同一作品、视角或实际循环。
### candidate

- judgment：标题不足以确认具体作品、视角或是否属于恐怖互动影游。
- experience_center：未知。
- mechanics：未知。
- innovation：证据不足。
- narrative_role：若为纯恐怖/第一人称恐怖会触及雷区，但不可据标题定性。
- personal_interest：暂不能判断。
- research_value：身份和玩法未确认。
- reason：title_only，未联网核验；保留不确定性。
- evidence_basis：输入仅提供标题，没有平台、视角或玩法描述；无法确认作品身份及是否属于恐怖互动影游，未独立核验。
- uncertainty：标题不足以确认作品身份、视角或恐怖类型；判断仅基于给定案例描述，未独立核验。

## legacy-32 · 武林对决

审核准则：{"title": "武林对决", "source": ["taste", "游戏库"], "result_label": "不推荐", "reason_types": ["明确雷区"], "draft_confidence": "high", "reason_detail": "武侠美术无法抵消传统回合制卡牌战斗和重复首领挑战。"}

### baseline

- judgment：标题过于泛化，可能是多种游戏或项目名称，无法确认玩家体验。
- experience_center：实际玩法、对战形式、战斗系统及单人/多人情境均未知。
- mechanics：不能从武林和对决字样判断是传统格斗、卡牌战斗、策略或其他玩法。
- innovation：名称无法对应具体作品，玩法差异未知。
- narrative_role：叙事、氛围和人物未知。
- personal_interest：是否属于用户不喜欢的泛武侠、传统战斗或多人游戏无法确认。
- research_value：无法判断。
- reason：无法确认可研究的具体设计。
- evidence_basis：名称歧义导致无法形成可靠推荐结论。
- uncertainty：仅凭标题无法确认具体游戏或实际循环；本轮未联网核验。
### candidate

- judgment：标题过于通用，无法唯一确认作品身份及其是否为传统战斗或其他玩法。
- experience_center：未知。
- mechanics：未知。
- innovation：证据不足。
- narrative_role：武侠题材不是单独否决，但无玩法依据。
- personal_interest：暂不能判断。
- research_value：标题歧义大。
- reason：title_only，未联网；未作身份猜测。
- evidence_basis：输入仅提供通用中文标题，无平台或出处；无法唯一识别游戏，也不能由“武林”推断战斗类型。
- uncertainty：标题过于通用，无法唯一确认作品身份与玩法；判断仅基于给定案例描述，未独立核验。

## legacy-33 · 无为修仙传

审核准则：{"title": "无为修仙传", "source": ["taste", "游戏库"], "result_label": "不推荐", "reason_types": ["明确雷区"], "draft_confidence": "high", "reason_detail": "泛修仙、放置、自动战斗和境界成长构成完整的低兴趣循环。"}

### baseline

- judgment：标题暗示修仙题材，但仅凭名称不能确定具体作品；若按常见同名类型理解，体验可能围绕修炼成长和资源积累。
- experience_center：可能接近文字/放置修仙模拟，以时间、资源、境界或事件推进；具体是否需要玩家持续决策未知。
- mechanics：题材名称无法证明其提供新活动或有意义的选择结构。
- innovation：仅凭修仙题材无法确认新活动或新的决策问题。
- narrative_role：东方题材潜在氛围未知，人物与叙事没有可确认信息。
- personal_interest：泛修仙、挂机和放置均属于用户明确低兴趣模式。
- research_value：低；只有题材联想，未见支持匹配的独立价值。
- reason：若其玩法实际改变修仙模拟的决策结构可再评估，目前无证据。
- evidence_basis：按题名最自然的类型理解，其主要循环可能落入明确不喜欢模式。
- uncertainty：标题驱动的保守推断，未核验游戏身份和玩法；评分置信度低。
### candidate

- judgment：标题可能暗示修仙题材，但无法确认身份或是否挂机/放置。
- experience_center：未知。
- mechanics：未知。
- innovation：证据不足。
- narrative_role：若为泛修仙挂机会不合偏好，但不能仅凭名字判定。
- personal_interest：暂不能判断。
- research_value：主循环与作品身份都未确认。
- reason：title_only，未联网；题材暗示不是证据。
- evidence_basis：输入仅提供中文标题，无玩法或出处；题名可能暗示修仙，但不足以确认作品身份或挂机/放置循环。
- uncertainty：标题不足以确认作品身份及是否为挂机放置玩法；判断仅基于给定案例描述，未独立核验。
