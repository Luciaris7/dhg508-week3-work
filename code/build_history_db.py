import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

SRC_GB = ('Loss of the Steamship "Titanic" (British Wreck Commissioner\'s '
          'Inquiry Report, 1912), Project Gutenberg eBook #39415')
SRC_BE = ('Lawrence Beesley, The Loss of the S. S. Titanic: Its Story and Its '
          'Lessons (1912), Project Gutenberg eBook #6675')


def gb(section, lines):
    return "%s, %s, %s" % (SRC_GB, section, lines)


def be(lines):
    return "%s, %s" % (SRC_BE, lines)


ROWS = [
    {
        "id": 1, "year": 1912, "date": "1912",
        "event": "泰坦尼克号为 46,328 总吨 / 21,831 净登记吨；由 Harland & Wolff 建造；在利物浦登记，官方编号 131,428。",
        "place": "贝尔法斯特 / 利物浦", "people": "",
        "source": gb('§I "Description of the Ship"', "L476-480"), "note": "",
    },
    {
        "id": 2, "year": 1912, "date": "1912",
        "event": "登记尺寸：长 852.50 英尺、宽 92.50 英尺；吃水 34 英尺 7 英寸时排水量 52,310 吨。",
        "place": "", "people": "",
        "source": gb('§I "Description of the Ship"', "L482-495"), "note": "",
    },
    {
        "id": 3, "year": 1912, "date": "1912",
        "event": "动力：两组四缸往复式蒸汽机驱动两舷螺旋桨，中间螺旋桨由蒸汽轮机驱动；登记马力 50,000，实际可输出至少 55,000。",
        "place": "", "people": "",
        "source": gb('§I "Description of the Ship"', "L497-501"), "note": "",
    },
    {
        "id": 4, "year": 1912, "date": "1912",
        "event": "船体由 15 道横向水密舱壁分为 16 个舱室（A–P）；水密性仅到 D 或 E 甲板，舱壁顶部未封闭。",
        "place": "", "people": "",
        "source": gb('§I "Description of the Ship"', "L546-554"),
        "note": "舱壁未到顶，进水后越顶漫入相邻舱室，是关键弱点",
    },
    {
        "id": 5, "year": 1912, "date": "1912",
        "event": "全船共 20 艘救生艇：14 艘木制救生艇（各载 65 人）、2 艘应急艇（各载 40 人）、4 艘 Engelhardt 折叠艇（各载 47 人）；总容量 1,178 人。",
        "place": "泰坦尼克号", "people": "",
        "source": gb('§I "Lifeboats"', "L1360-1381"), "note": "远少于船上 2,201 人",
    },
    {
        "id": 6, "year": 1912, "date": "10 April 1912",
        "event": "泰坦尼克号于星期三离开南安普敦，停靠瑟堡后驶往皇后镇，并于 4 月 11 日星期四下午自皇后镇启程。",
        "place": "Southampton; Cherbourg; Queenstown", "people": "",
        "source": gb('§II "The Route Followed"', "L1870-1872"), "note": "",
    },
    {
        "id": 7, "year": 1912, "date": "11 April 1912",
        "event": "离开皇后镇时船上共有 885 名船员：甲板部 66、轮机部 325、事务部 494。",
        "place": "Queenstown", "people": "Edward Charles Smith",
        "source": gb('§I "Crew and Passengers"', "L1772-1781"), "note": "",
    },
    {
        "id": 8, "year": 1912, "date": "11 April 1912",
        "event": "船上乘客 1,316 人：头等 325、二等 285、三等 706。",
        "place": "", "people": "",
        "source": gb('§I "Crew and Passengers"', "L1800-1810"), "note": "",
    },
    {
        "id": 9, "year": 1912, "date": "11 April 1912",
        "event": "船上人员总数 2,201 人；其中儿童 109 人（头等 6、二等 24、三等 79）。",
        "place": "", "people": "",
        "source": gb('§I "Crew and Passengers"', "L1813-1822"), "note": "",
    },
    {
        "id": 10, "year": 1912, "date": "1912",
        "event": "船东为 White Star Line（Oceanic Steam Navigation Co.），资本 750,000 英镑；董事包括 J. Bruce Ismay（主席）、Lord Pirrie、H. A. Sanderson。",
        "place": "利物浦", "people": "J. Bruce Ismay; Lord Pirrie; H. A. Sanderson",
        "source": gb('§I "The White Star Line"', "L428-431"), "note": "",
    },
    {
        "id": 11, "year": 1912, "date": "April 1912",
        "event": "所走航线为出港南线（outward southern track）：自爱尔兰 Fastnet Light 沿大圆航线至 42°N 47°W 转折点，再经 Nantucket Shoal 灯船附近驶向纽约。",
        "place": "北大西洋", "people": "",
        "source": gb('§II "The Route Followed"', "L1892-1898"), "note": "",
    },
    {
        "id": 12, "year": 1912, "date": "14 April 1912",
        "event": "全程维持高速；晚 10 点 Cherub 计程仪记为每两小时 45 海里；四副估计航速 22 节，主机持续运转 75 转/分。",
        "place": "北大西洋", "people": "",
        "source": gb('§II "Speed of the Ship"', "L2303-2313"), "note": "",
    },
    {
        "id": 13, "year": 1912, "date": "14 April 1912",
        "event": "自晚 6 点至撞击时天气晴朗无云、无月、有星；气温降至 32°F（约 0°C）。",
        "place": "北大西洋", "people": "",
        "source": gb('§II "The Weather Conditions"', "L2318-2322"),
        "note": "据航海指南，气温下降并不可靠地预示冰情",
    },
    {
        "id": 14, "year": 1912, "date": "14 April 1912 5:50 p.m.",
        "event": "船长 Smith 于下午 5:50 略微向南改变航向，但未减速；到 11:30 前又回到习惯航线约 2 海里范围内。",
        "place": "北大西洋", "people": "Edward Charles Smith",
        "source": gb('§II "Action that should have been taken"', "L2345-2349"), "note": "",
    },
    {
        "id": 15, "year": 1912, "date": "14 April 1912 约11:40 p.m.",
        "event": "撞击前片刻：瞭望员敲三下警钟并电话报告「Iceberg right ahead」；当值大副 Murdoch 下令「Hard-a-starboard」，随即传令机舱「Stop. Full speed astern」，并关闭水密门。",
        "place": "北大西洋 41°46'N 50°14'W 附近", "people": "William M. Murdoch",
        "source": gb('§II "The Collision"', "L2393-2405"),
        "note": "报告记事时间约 11.40，Beesley 则记 11.45",
    },
    {
        "id": 16, "year": 1912, "date": "14 April 1912 11:40 p.m.",
        "event": "与冰山相撞：右舷在龙骨以上约 10 英尺处受损；受损处含前尖舱、1–3 号货舱、5 与 6 号锅炉舱；破损延伸约 300 英尺。",
        "place": "北大西洋", "people": "",
        "source": gb('§III "Extent of the Damage"', "L2447-2455"), "note": "",
    },
    {
        "id": 17, "year": 1912, "date": "14 April 1912",
        "event": "碰撞后不久即从驾驶台远程关闭机舱与锅炉舱的水密门。",
        "place": "北大西洋", "people": "",
        "source": gb('§III "Flooding in first ten minutes"', "L2488-2490"), "note": "",
    },
    {
        "id": 18, "year": 1912, "date": "15 April 1912",
        "event": "船在碰撞后 2 小时 40 分钟沉没。",
        "place": "北大西洋", "people": "",
        "source": gb('§II "The Collision"', "L2432-2433"), "note": "",
    },
    {
        "id": 19, "year": 1912, "date": "15 April 1912 2:20 a.m.",
        "event": "船于凌晨 2:20 消失没入水中。",
        "place": "北大西洋", "people": "",
        "source": gb('§III "Final Effect of the Damage"', "L2628-2629"), "note": "",
    },
    {
        "id": 20, "year": 1912, "date": "15 April 1912",
        "event": "据二副 Lightoller 陈述，船未断成两截，而是逐渐竖起直至近乎垂直后缓缓下沉；船尾第二号烟囱一度触及水面。",
        "place": "北大西洋", "people": "C. H. Lightoller",
        "source": gb('§III "Final Effect of the Damage"', "L2616-2626"),
        "note": "此说与「断成两截」的流行说法冲突，属早期证词",
    },
    {
        "id": 21, "year": 1912, "date": "15 April 1912 约12:30–1:40 a.m.",
        "event": "四副 Boxall 在二号艇中先后发射约 8 枚火箭；其所见不明船只的灯光即 Californian 号。",
        "place": "北大西洋", "people": "J. G. Boxall; Californian",
        "source": gb('§IV "The Californian" 相关', "L3200-3205"),
        "note": "Californian 号仅一名无线电报员且已入睡，未听见求救",
    },
    {
        "id": 22, "year": 1912, "date": "15 April 1912",
        "event": "Carpathia 号救援：13,600 总吨，Cunard 公司，船长 Arthur Henry Rostron；由纽约驶往利物浦，载约 740 乘客、325 船员。收到求救后掉头，以最高 17.5 节赶赴。",
        "place": "北大西洋", "people": "Arthur Henry Rostron",
        "source": gb('§IV "The Rescue by the Steamship Carpathia"', "L3212-3219"), "note": "",
    },
    {
        "id": 23, "year": 1912, "date": "15 April 1912 4:05–8:00 a.m.",
        "event": "Carpathia 于约 4:05 停船、4:10 接起第一艘救生艇；共接起 13 艘救生艇、2 艘应急艇、2 艘折叠艇，救起 712 人（其中 1 人随后死亡）；至上午 8 点全部救起；位置 41°46'N 50°14'W。",
        "place": "北大西洋 41°46'N 50°14'W", "people": "Arthur Henry Rostron; J. G. Boxall",
        "source": gb('§IV "The Rescue by the Steamship Carpathia"', "L3220-3237"), "note": "",
    },
    {
        "id": 24, "year": 1912, "date": "14 April 1912",
        "event": "Californian 号：Leyland 公司，船长 Stanley Lord，由伦敦驶往波士顿，6,223 总吨，航速 12.5–13 节；船上仅 1 名 Marconi 电报员，其时已睡。",
        "place": "北大西洋", "people": "Stanley Lord",
        "source": gb('§V "The Circumstances in connection with the Steamship Californian"', "L3302-3308"),
        "note": "",
    },
    {
        "id": 25, "year": 1912, "date": "15 April 1912 12:30–1:40 a.m.",
        "event": "Californian 号在 12:30 至 1:40 之间看到 8 枚火箭，却未采取救援行动；调查庭裁定她若在见到第一枚火箭时尝试，本可赶到。",
        "place": "北大西洋", "people": "Stanley Lord",
        "source": gb('§VII "Finding of the Court", Q24', "L5687-5690"), "note": "",
    },
    {
        "id": 26, "year": 1912, "date": "15 April 1912",
        "event": "救生艇总容量本可载 1,178 人，但实际至少 8 艘艇未满载。",
        "place": "北大西洋", "people": "",
        "source": gb('§VII "Finding of the Court", Q20', "L5591-5601"),
        "note": "原因：乘客起初不信危险、部分艇奉命下放后再靠舷门上人等",
    },
    {
        "id": 27, "year": 1912, "date": "15 April 1912",
        "event": "获救总人数 711（占船上 2,201 人的 32.30%）：乘客 499 / 1,316、船员 212 / 885。",
        "place": "北大西洋", "people": "",
        "source": gb('§VII "Finding of the Court", Q21', "L3274-3291"),
        "note": "同一报告别处又记救起 712 人",
    },
    {
        "id": 28, "year": 1912, "date": "15 April 1912",
        "event": "调查庭裁决：沉没系与冰山相撞所致，而相撞源于船舶以过高速度航行。",
        "place": "伦敦（威斯敏斯特）", "people": "Lord Mersey",
        "source": gb('"Report of the Court"', "L168-176"),
        "note": "裁决日期 1912 年 7 月 30 日",
    },
    {
        "id": 29, "year": 1912, "date": "15 April 1912",
        "event": "第 23 问答复：船于 4 月 15 日凌晨 2:20（船时）在北纬 41°46'、西经 50°14' 沉没。",
        "place": "北大西洋", "people": "",
        "source": gb('§VII "Finding of the Court", Q23', "L5673-5676"), "note": "",
    },
    {
        "id": 30, "year": 1912, "date": "15 April 1912",
        "event": "第 24 问答复：失事原因为碰撞冰山及随之沉没；Californian 号本可施救却未作任何尝试。",
        "place": "北大西洋", "people": "Californian",
        "source": gb('§VII "Finding of the Court", Q24', "L5687-5690"), "note": "",
    },
    {
        "id": 31, "year": 1912, "date": "1912",
        "event": "调查庭记载此次事故造成 1,490 人丧生。",
        "place": "北大西洋", "people": "",
        "source": gb('"Introduction"', "L163-165"), "note": "",
    },
    {
        "id": 32, "year": 1909, "date": "31 March 1909 / 31 May 1911 / 31 March 1912 / 4 April 1912",
        "event": "Beesley 记述：龙骨于 1909 年 3 月 31 日铺设；1911 年 5 月 31 日下水；1912 年 3 月 31 日在贝尔法斯特通过 Board of Trade 试航；4 月 4 日抵达南安普敦。",
        "place": "贝尔法斯特 / 南安普敦", "people": "Lawrence Beesley",
        "source": be("L185-189"), "note": "作者为幸存乘客，叙述带亲历语气",
    },
    {
        "id": 33, "year": 1912, "date": "10 April 1912",
        "event": "Beesley 记述：泰坦尼克号 4 月 10 日星期三载 2,208 名乘客与船员自南安普敦首航纽约；同日停靠瑟堡，星期四停靠皇后镇。",
        "place": "Southampton; Cherbourg; Queenstown", "people": "Lawrence Beesley",
        "source": be("L189-192"), "note": "船上人数作 2,208，与官方 2,201 略有出入",
    },
    {
        "id": 34, "year": 1912, "date": "14 April 1912",
        "event": "Beesley 记述：船于星期日 11:45 P.M. 在北纬 41°46'、西经 50°14' 撞上冰山，约两个半小时后沉没；815 名乘客与 688 名船员溺亡，705 人被 Carpathia 救起。",
        "place": "北大西洋", "people": "Lawrence Beesley; Carpathia",
        "source": be("L193-196"),
        "note": "与官方报告（11.40、约 1,500 人遇难、712 人获救）数字有出入，属并存的史料差异",
    },
    {
        "id": 35, "year": 1912, "date": "15 April 1912",
        "event": "Beesley 记述：救生艇上众人起初以为 Olympic 号会来救援，并称另有 8 艘船位于 300 英里之内。",
        "place": "北大西洋", "people": "Olympic",
        "source": be("L1548-1566"), "note": "",
    },
    {
        "id": 36, "year": 1912, "date": "15 April 1912",
        "event": "Beesley 记述：离船不久，众人在泰坦尼克号左舷地平线看见船只灯光，遂向该方向划行，但灯光逐渐远去消失。",
        "place": "北大西洋", "people": "",
        "source": be("L1571-1576"), "note": "所指不明船只",
    },
]


IMAGES = [
    {
        "id": 1,
        "file": "rms-titanic-departing-southampton-1912-04-10.jpg",
        "caption": "泰坦尼克号 1912 年 4 月 10 日自南安普敦启航",
        "author": "F. G. O. Stuart",
        "date": "1912",
        "license": "Public domain",
        "commons_url": "https://commons.wikimedia.org/wiki/File:RMS_Titanic_3.jpg",
        "related_events": "6;33",
        "note": "",
    },
    {
        "id": 2,
        "file": "titanic-and-olympic-under-construction-belfast.jpg",
        "caption": "泰坦尼克号与奥林匹克号在贝尔法斯特 Harland & Wolff 船厂建造中，约 1910",
        "author": "Robert Welch",
        "date": "约 1910",
        "license": "Public domain",
        "commons_url": "https://commons.wikimedia.org/wiki/File:Construction_of_Titanic_and_Olympic.jpg",
        "related_events": "1;32",
        "note": "",
    },
    {
        "id": 3,
        "file": "iceberg-near-titanic-wreck-site-1912.jpg",
        "caption": "沉没地点附近的一座冰山，1912-12-14",
        "author": "Louis Ogden / NARA",
        "date": "1912-12-14",
        "license": "Public domain",
        "commons_url": "https://commons.wikimedia.org/wiki/File:A_Photograph_of_an_Iceberg_Floating_Near_the_Site_of_the_TITANIC_Sinking._-_NARA_-_278334.jpg",
        "related_events": "15;16",
        "note": "照片拍摄于沉没八个月之后，非失事当时之冰山",
    },
    {
        "id": 4,
        "file": "carpathia-with-titanic-lifeboats-1912.jpg",
        "caption": "泰坦尼克号救生艇靠泊 Carpathia 号，1912-04-18",
        "author": "The New York Times",
        "date": "1912-04-18",
        "license": "Public domain",
        "commons_url": "https://commons.wikimedia.org/wiki/File:Carpathia_-_Titanic_lifeboats.jpg",
        "related_events": "5;23;26",
        "note": "题注作「靠泊 Carpathia 号」，然图面所见为夜色中救生艇仍悬于吊艇架之上，题注与图面似有出入，并存待考",
    },
    {
        "id": 5,
        "file": "titanic-survivors-aboard-carpathia-1912.jpg",
        "caption": "获救者聚集于 Carpathia 号甲板，1912",
        "author": "Bain News Service",
        "date": "1912",
        "license": "Public domain",
        "commons_url": "https://commons.wikimedia.org/wiki/File:Survivors_of_TITANIC_on_CARPATHIA_LCCN2014691298.jpg",
        "related_events": "23;27",
        "note": "",
    },
    {
        "id": 6,
        "file": "titanic-paperboy-ned-parfett-1912.jpg",
        "caption": "报童 Ned Parfett 举「泰坦尼克号沉没」号外，1912-04-16",
        "author": "佚名",
        "date": "1912-04-16",
        "license": "Public domain",
        "commons_url": "https://commons.wikimedia.org/wiki/File:Titanic_paperboy_crop.jpg",
        "related_events": "19;31",
        "note": "",
    },
]


def write_records():
    path = os.path.join(ROOT, "records.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(ROWS, f, ensure_ascii=False, indent=1)
    return path


def build_db():
    db_path = os.path.join(ROOT, "history.db")
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE events (
            id     INTEGER PRIMARY KEY,
            year   INTEGER,
            date   TEXT,
            event  TEXT NOT NULL,
            place  TEXT,
            people TEXT,
            source TEXT,
            note   TEXT
        )
    """)
    cur.executemany(
        "INSERT INTO events (id, year, date, event, place, people, source, note) "
        "VALUES (:id, :year, :date, :event, :place, :people, :source, :note)",
        ROWS,
    )
    cur.execute("""
        CREATE TABLE images (
            id             INTEGER PRIMARY KEY,
            file           TEXT NOT NULL,
            caption        TEXT,
            author         TEXT,
            date           TEXT,
            license        TEXT,
            commons_url    TEXT,
            related_events TEXT,
            note           TEXT
        )
    """)
    cur.executemany(
        "INSERT INTO images (id, file, caption, author, date, license, "
        "commons_url, related_events, note) "
        "VALUES (:id, :file, :caption, :author, :date, :license, "
        ":commons_url, :related_events, :note)",
        IMAGES,
    )
    conn.commit()
    n = cur.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    m = cur.execute("SELECT COUNT(*) FROM images").fetchone()[0]
    conn.close()
    return db_path, n, m


if __name__ == "__main__":
    r = write_records()
    db, n, m = build_db()
    print("records.json ->", r)
    print("history.db   ->", db)
    print("rows inserted:", n, "events,", m, "images")
