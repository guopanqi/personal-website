import sys
import csv
import json
from pathlib import Path

# Add cli src to path
sys.path.append(str(Path(__file__).parent.parent / "gamer520_cli/src"))
from gamer520_cli.normalize import normalize_title_key, normalize_title_for_search, extract_link_id, normalize_url

PC_CANDIDATES = [
  {"title": "奇迹时代4 高级版|豪华中文|V.1.015.002.122980+大法师的秘辛DLC-全扩展+全季票+全DLC+修改器|解压即撸|", "url": "https://www.gamer520.com/57234.html", "date": "2026-06-17"},
  {"title": "亡命迪斯科 Dead as Disco|豪华中文|Build.23726858+全DLC|解压即撸|", "url": "https://www.gamer520.com/113045.html", "date": "2026-06-17"},
  {"title": "神话时代 重述高级版|中字-国语|V19.15437.0+黑曜石之镜DLC-全季票-新纪元+全DLC+季票|解压即撸|", "url": "https://www.gamer520.com/81402.html", "date": "2026-06-17"},
  {"title": "战锤40K 行商浪人|官方中文|V1.6.0.475- 无限缪斯翁DLC+季票+预购特典+全DLC+修改器|解压即撸|", "url": "https://www.gamer520.com/47313.html", "date": "2026-06-17"},
  {"title": "群星 银河版|官方中文|V4.4.2+游牧民族DLC+全DLC+修改器|解压即撸|", "url": "https://www.gamer520.com/43143.html", "date": "2026-06-17"},
  {"title": "极限竞速 地平线6 传奇版|豪华中文|V375.327-黑域疾掠-寒流破界+预购特典+全DLC-支持手柄|解压即撸|Forza Horizon 6", "url": "https://www.gamer520.com/113322.html", "date": "2026-06-17"},
  {"title": "死亡细胞|豪华中文|Build.23473434-天罡-烈焰战士&虚空伙伴+全DLC-支持手柄|解压即撸|", "url": "https://www.gamer520.com/22593.html", "date": "2026-06-17"},
  {"title": "无人深空|豪华中文|V6.45+全新内容:虫群-黯域归尘-烬海迷途+全DLC+修改器|解压即撸|", "url": "https://www.gamer520.com/13570.html", "date": "2026-06-17"},
  {"title": "团战经理2|豪华中文|Build.23764322+全DLC|解压即撸|", "url": "https://www.gamer520.com/114271.html", "date": "2026-06-17"},
  {"title": "无尽猎杀|豪华中文|Build.23764210-暗潮灭绝-深渊猎魂+全DLC|解压即撸|", "url": "https://www.gamer520.com/110436.html", "date": "2026-06-17"},
  {"title": "星火燎原|豪华中文|Build.23758659-叛神纪元-黑誓王庭+全DLC|解压即撸|", "url": "https://www.gamer520.com/112453.html", "date": "2026-06-17"},
  {"title": "女巫史诗 支持者版|官方中文|Build.23752592+全DLC|解压即撸|", "url": "https://www.gamer520.com/50156.html", "date": "2026-06-17"},
  {"title": "受折磨的灵魂2|豪华中文|Build.23699798+预购特典+全DLC|解压即撸|", "url": "https://www.gamer520.com/101195.html", "date": "2026-06-17"},
  {"title": "我的修仙日志|官方中文|Build.23565729+全DLC解压即撸|", "url": "https://www.gamer520.com/115977.html", "date": "2026-06-17"},
  {"title": "吾皇万岁|官方中文|Build.23762146+全DLC|解压即撸|", "url": "https://www.gamer520.com/114949.html", "date": "2026-06-17"},
  {"title": "放置模拟国|官方中文|Build.23280389+全DLC|解压即撸|", "url": "https://www.gamer520.com/115974.html", "date": "2026-06-17"},
  {"title": "哇咔纳传说|官方中文|Build.23772531+全DLC|解压即撸|", "url": "https://www.gamer520.com/115968.html", "date": "2026-06-17"},
  {"title": "破晓|豪华中文|Build.23759433-崩界余生-深渊回响+全DLC|解压即撸|", "url": "https://www.gamer520.com/111582.html", "date": "2026-06-17"},
  {"title": "霓虹深渊2 支持者版|豪华中文|Build.23741948-惊奇不断重大更新+宿敌再临DLC+全DLC|解压即撸|", "url": "https://www.gamer520.com/96266.html", "date": "2026-06-17"},
  {"title": "龟龟潜海记 Shelldiver|豪华中文|Build.23767205-逆袭黑马-爆冷成名+全DLC|解压即撸|", "url": "https://www.gamer520.com/102559.html", "date": "2026-06-17"},
  {"title": "邪恶推币机|官方中文|Build.23758927+全DLC|解压即撸|", "url": "https://www.gamer520.com/115408.html", "date": "2026-06-17"},
  {"title": "深入绝地|豪华中文|Build.23764975+全DLC|解压即撸|", "url": "https://www.gamer520.com/115173.html", "date": "2026-06-17"},
  {"title": "种呱得呱|豪华中文|Build.23755701-沼歌天书-泽界轮回+全DLC|解压即撸|", "url": "https://www.gamer520.com/99541.html", "date": "2026-06-17"},
  {"title": "逐鹿汉末 三国|豪华中文|Build.23757006+全DLC|解压即撸|", "url": "https://www.gamer520.com/106239.html", "date": "2026-06-17"},
  {"title": "杀手精神病兔子… 在太空！新星拓荒|官方中文|Build.23741138+全DLC|解压即撸|", "url": "https://www.gamer520.com/114951.html", "date": "2026-06-17"},
  {"title": "沙滩防线 僵尸来袭|官方中文|Build.23760367+全DLC|解压即撸|", "url": "https://www.gamer520.com/115549.html", "date": "2026-06-17"},
  {"title": "桌面战争 兵团乱斗|官方中文|Build.23756563+全DLC|解压即撸|", "url": "https://www.gamer520.com/91416.html", "date": "2026-06-17"},
  {"title": "挂机升级打怪兽|官方中文|Build.23760557+全DLC|解压即撸|", "url": "https://www.gamer520.com/113956.html", "date": "2026-06-17"},
  {"title": "帕格尼物语|豪华中文|Build.23740151+草原之歌DLC-部落联盟-繁荣之路-沙盒|解压即撸|", "url": "https://www.gamer520.com/67792.html", "date": "2026-06-17"},
  {"title": "少女终端|官方中文|Build.23771936+全DLC|解压即撸|", "url": "https://www.gamer520.com/115546.html", "date": "2026-06-17"},
  {"title": "我来自江湖|官方中文|Build.23733894-剑舞千山-画皮幻影+全DLC|解压即撸|", "url": "https://www.gamer520.com/81917.html", "date": "2026-06-17"},
  {"title": "罗马拓荒录|豪华中文|Build.23762225+全DLC|解压即撸|", "url": "https://www.gamer520.com/114360.html", "date": "2026-06-17"},
  {"title": "雷霆孤影 VOIN|官方中文|Build.23761858-摧天裂地-破碎荣耀+全DLC|解压即撸|", "url": "https://www.gamer520.com/86124.html", "date": "2026-06-17"},
  {"title": "我自成道|豪华中文|Build.23753974-破邪长阶-魔刃轮回+全DLC|解压即撸|", "url": "https://www.gamer520.com/113536.html", "date": "2026-06-17"},
  {"title": "黑纱掠袭 |官方中文|Build.23706694+全DLC|解压即撸|", "url": "https://www.gamer520.com/115934.html", "date": "2026-06-17"},
  {"title": "魔药小铺|豪华中文|Build.23194172+全DLC|解压即撸|", "url": "https://www.gamer520.com/100719.html", "date": "2026-06-17"},
  {"title": "美国卡车模拟|官方中文|Build.23741757+伊利诺伊州DLC+全DLC|解压即撸|", "url": "https://www.gamer520.com/47624.html", "date": "2026-06-17"},
  {"title": "突袭者 RAIDBORN|官方中文|Build.23764666+全DLC|解压即撸|", "url": "https://www.gamer520.com/114770.html", "date": "2026-06-17"},
  {"title": "混音带 Mixtape|官方中文|Build.22998691+全DLC|解压即撸|", "url": "https://www.gamer520.com/113245.html", "date": "2026-06-17"},
  {"title": "叛军指挥官 Rogue Command|官方中文|Build.23358873+全DLC|解压即撸|", "url": "https://www.gamer520.com/85643.html", "date": "2026-06-17"},
  {"title": "穿越时空2|豪华中文|Build.21312552+全DLC|解压即撸|", "url": "https://www.gamer520.com/115918.html", "date": "2026-06-16"}
]

SWITCH_CANDIDATES = [
  {"title": "EA SPORTS FC 26|中字-国语|本体+1.88.DFF9升补+1DLC|NSP|", "url": "https://www.gamer520.com/101397.html", "date": "2026-06-17"},
  {"title": "搭建赛道 Make Way|官方中文|本体+1.4.0.6升补+1DLC|NSZ|", "url": "https://www.gamer520.com/113618.html", "date": "2026-06-17"},
  {"title": "穿越时空2|汉化中文|NSP|", "url": "https://www.gamer520.com/115921.html", "date": "2026-06-16"}
]

def main():
    csv_path = Path(__file__).parent.parent / "gamer520-games.csv"
    
    # Read CSV
    db = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            db.append(row)
            
    # Indexes for quick search
    db_by_link_id = {}
    db_by_title_key = {}
    for row in db:
        url = row.get("链接", "")
        link_id = extract_link_id(url)
        if link_id:
            db_by_link_id[link_id] = row
            
        title = row.get("标题", "")
        title_key = normalize_title_key(title)
        if title_key:
            db_by_title_key[title_key] = row
            
    # Process candidates
    all_candidates = []
    for c in PC_CANDIDATES:
        c["platform"] = "PC"
        all_candidates.append(c)
    for c in SWITCH_CANDIDATES:
        c["platform"] = "Switch"
        all_candidates.append(c)
        
    new_games = []
    cross_platform_merge = []
    skipped = []
    
    # Group candidates by normalized title to check if they are the same game in this batch
    candidates_by_title_key = {}
    for c in all_candidates:
        tk = normalize_title_key(c["title"])
        search_key = normalize_title_for_search(c["title"])
        candidates_by_title_key.setdefault(search_key, []).append(c)
        
    for search_key, group in candidates_by_title_key.items():
        # Let's see if this game exists in DB
        matched_row = None
        # Check by link ID first
        for c in group:
            cid = extract_link_id(c["url"])
            if cid in db_by_link_id:
                matched_row = db_by_link_id[cid]
                break
        
        # Check by title key
        if not matched_row:
            for c in group:
                tk = normalize_title_key(c["title"])
                if tk in db_by_title_key:
                    matched_row = db_by_title_key[tk]
                    break
                    
        # Check by search key in DB
        if not matched_row:
            for row in db:
                db_sk = normalize_title_for_search(row.get("标题", ""))
                if db_sk == search_key:
                    matched_row = row
                    break
                    
        # Aggregate platforms of the current group
        group_platforms = set(c["platform"] for c in group)
        
        if matched_row:
            # Game exists in DB
            db_platform = matched_row["平台"]
            # Check if all group platforms are already in db_platform
            missing_platforms = []
            for gp in group_platforms:
                if gp not in db_platform:
                    missing_platforms.append(gp)
            
            if missing_platforms:
                # Needs cross-platform merge
                cross_platform_merge.append({
                    "title": matched_row["标题"],
                    "db_platform": db_platform,
                    "target_platform": "PC/Switch",
                    "link": matched_row["链接"],
                    "group": group
                })
            else:
                for c in group:
                    skipped.append(c)
        else:
            # New game
            # If group has both PC and Switch, target platform is PC/Switch
            target_platform = "PC/Switch" if len(group_platforms) > 1 else list(group_platforms)[0]
            pc_candidate = next((c for c in group if c["platform"] == "PC"), None)
            main_candidate = pc_candidate if pc_candidate else group[0]
            
            new_games.append({
                "title": main_candidate["title"],
                "url": main_candidate["url"],
                "date": main_candidate["date"],
                "platform": target_platform,
                "group": group
            })

    print(f"Total processed search keys: {len(candidates_by_title_key)}")
    print(f"Skipped count: {len(skipped)}")
    print(f"Cross platform merge count: {len(cross_platform_merge)}")
    print(f"New games count: {len(new_games)}")
    
    print("\n--- Cross Platform Merge Details ---")
    for cp in cross_platform_merge:
        print(f"- {cp['title']}: DB Platform '{cp['db_platform']}' -> '{cp['target_platform']}'")
        
    print("\n--- New Games List ---")
    for i, ng in enumerate(new_games, 1):
        print(f"{i}. [{ng['platform']}] {ng['title']} ({ng['url']}) Date: {ng['date']}")

if __name__ == "__main__":
    main()
