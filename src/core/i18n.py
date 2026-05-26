"""
i18n.py - 다국어 지원 시스템
언어 키를 통해 모든 UI 텍스트를 관리합니다.
"""

_current_lang = "ko"

STRINGS = {
    "ko": {
        # 메인 메뉴
        "game_title": "30일간의 생존",
        "game_subtitle": "좀비 아포칼립스 오픈월드 서바이벌",
        "new_game": "새 게임",
        "load_game": "이어하기",
        "settings": "설정",
        "quit": "종료",
        "version_info": "v1.1  |  Python + Pygame",

        # 월드 생성
        "world_creation_title": "새 월드 생성",
        "world_name": "월드 이름:",
        "difficulty": "난이도:",
        "day_length": "하루 길이(분)",
        "resource_density": "자원 밀도",
        "weather_variability": "날씨 변동성",
        "zombie_activity": "좀비 활동량",
        "building_density": "건물 밀도",
        "survival_days": "생존 일수",
        "start_world": "월드 생성 시작",
        "back": "◀ 뒤로",

        # 설정
        "settings_title": "설정",
        "resolution": "해상도:",
        "screen_mode": "화면 모드:",
        "fullscreen": "전체화면",
        "windowed": "창 모드",
        "particle_quality": "파티클 품질:",
        "particle_none": "끔",
        "particle_low": "낮음",
        "particle_normal": "보통",
        "particle_high": "높음",
        "language": "언어:",
        "apply": "적용",

        # HUD
        "hp": "HP",
        "hunger": "배고픔",
        "thirst": "갈증",
        "stress": "스트레스",
        "stamina": "스태미나",
        "defense": "방어도",
        "kills": "처치",
        "day": "일차",
        "fist": "주먹",
        "exhausted": "탈진!",

        # 인벤토리
        "inventory": "인벤토리",
        "equipment": "장비",
        "weight": "무게",
        "left_click_use": "좌클릭: 사용",
        "right_click_equip": "우클릭: 장착",

        # 크래프팅
        "crafting": "크래프팅",

        # 상호작용
        "press_e_interact": "E: 상호작용",
        "press_e_enter": "E: 건물 진입",
        "press_e_exit": "E: 나가기",
        "press_e_search": "E: 탐색",
        "controls_hint": "E:상호작용  I:인벤토리  C:크래프팅  Tab:지도  ESC:메뉴",

        # 건물 내부
        "entering_building": "건물에 진입합니다...",
        "exiting_building": "건물에서 나갑니다...",
        "searched_already": "이미 탐색한 가구입니다.",
        "found_nothing": "아무것도 발견하지 못했습니다.",
        "found_items": "발견: ",
        "zombie_intrusion": "좀비가 건물 안으로 침입했습니다!",
        "zombie_followed": "좀비가 따라 들어왔습니다!",
        "zombie_followed_outside": "좀비가 문을 열고 밖으로 쫓아나왔습니다!",

        # 일시정지
        "paused": "일시정지",
        "resume": "계속하기",
        "save_game": "저장하기",
        "save_and_quit": "저장 후 종료",
        "quit_no_save": "저장하지 않고 종료",

        # 이벤트
        "game_saved": "게임이 저장되었습니다.",
        "new_day": "{}일차가 밝았습니다.",
        "zombie_horde": "좀비 무리가 접근합니다!",
        "found_survivor": "생존자를 발견했습니다!",

        # 난이도
        "peaceful": "평화로움",
        "easy": "쉬움",
        "normal": "보통",
        "hard": "어려움",
        "hardcore": "하드코어",
        "challenge": "챌린지",

        # 엔딩
        "ending_survived": "생존 성공!",
        "ending_died": "사망...",

        # 가구
        "furniture_냉장고": "냉장고",
        "furniture_선반": "선반",
        "furniture_서랍장": "서랍장",
        "furniture_침대밑": "침대 밑",
        "furniture_약품장": "약품장",
        "furniture_진열대": "진열대",
        "furniture_카운터": "카운터",
        "furniture_사물함": "사물함",
        "furniture_무기함": "무기함",
        "furniture_군용상자": "군용 상자",
        "furniture_통신장비": "통신 장비",

        # 추가 라벨 및 힌트
        "equip_head": "머리",
        "equip_body": "상의",
        "equip_feet": "신발",
        "equip_weapon": "무기",
        "inventory_hint": "좌클릭: 사용  |  드래그: 장착/해제  |  우클릭: 버리기",
        "defense_label": "방어도: {}",
        "kills_label": "처치: {}",
        "stealth_mode": "◆ 은신 중 ◆",
        "weather_label": "날씨: {}",
        "hud_controls_hint": "E:상호작용  I:인벤토리  C:크래프팅  Tab:지도  LCTRL:앉기  ESC:메뉴",
        "click_to_main": "클릭하여 메인 메뉴로 돌아가기",
        "sandbox_mode": "🔧 샌드박스 모드 (모든 아이템 지급)",
        "world_name_default": "월드 1",

        # 날씨
        "weather_맑음": "맑음",
        "weather_비": "비",
        "weather_안개": "안개",
        "weather_눈": "눈",
        "weather_폭풍우": "폭풍우",

        # 시간대
        "period_새벽": "새벽",
        "period_낮": "낮",
        "period_황혼": "황혼",
        "period_밤": "밤",

        # 바이옴
        "도시": "도시",
        "주거지": "주거지",
        "산림": "산림",
        "병원구역": "병원구역",
        "군사기지": "군사기지",
        "호수": "호수",
        "황무지": "황무지",
        "공장단지": "공장단지",
        "밀밭": "밀밭",

        # 난이도 세부 설명
        "desc_peaceful": "좀비가 거의 출현하지 않고 자원이 풍부합니다. 탐험과 건설에 집중할 수 있습니다.",
        "desc_easy": "좀비 수가 적고 자원이 넉넉합니다. 서바이벌 입문자에게 적합합니다.",
        "desc_normal": "균형 잡힌 난이도. 전략적 플레이가 필요합니다.",
        "desc_hard": "좀비가 강하고 자원이 부족합니다. 숙련된 생존자만 도전하세요.",
        "desc_hardcore": "자원 극도로 부족. 좀비가 매우 빠르고 강합니다. 사망 시 세이브 삭제.",
        "desc_challenge": "극한의 도전. 모든 것이 당신을 죽이려 합니다. 진정한 서바이버만.",

        # 아이템 이름
        "item_식량통조림": "식량 통조림",
        "item_마른 빵": "마른 빵",
        "item_에너지바": "에너지바",
        "item_고기 구이": "고기 구이",
        "item_전투 식량": "전투 식량",
        "item_에너지 드링크": "에너지 드링크",
        "item_생수": "생수",
        "item_탄산음료": "탄산음료",
        "item_커피": "커피",
        "item_구급상자": "구급상자",
        "item_진통제": "진통제",
        "item_고급 치료킷": "고급 치료킷",
        "item_약초": "약초",
        "item_붕대": "붕대",
        "item_무기": "무기",
        "item_파이프": "파이프",
        "item_나이프": "나이프",
        "item_도끼": "도끼",
        "item_야구방망이": "야구방망이",
        "item_권총": "권총",
        "item_레버액션 소총": "레버액션 소총",
        "item_탄약": "탄약",
        "item_가방": "가방",
        "item_방독면": "방독면",
        "item_방탄조끼": "방탄조끼",
        "item_운동화": "운동화",
        "item_손전등": "손전등",
        "item_비상용 배터리": "비상용 배터리",
        "item_지도": "지도",
        "item_개조 손전등": "개조 손전등",
        "item_나무": "나무",
        "item_못": "못",
        "item_천": "천",
        "item_고철": "고철",
        "item_바리케이드 재료": "바리케이드 재료",
        "item_라디오 부품": "라디오 부품",
        "item_장거리 무전기": "장거리 무전기",
        "item_군사 문서": "군사 문서",
        "item_사진": "사진",
        "item_기계 부품": "기계 부품",
        "item_농작물": "농작물",
        "item_횃불": "횃불",
        "item_함정": "함정",

        # 아이템 설명
        "desc_식량통조림": "밀봉된 고기 통조림. 유통기한은 이미 지났지만 아직 먹을 수 있다.",
        "desc_마른 빵": "딱딱하게 굳은 빵. 배는 채울 수 있다.",
        "desc_에너지바": "고칼로리 에너지바. 빠르게 에너지를 보충할 수 있다.",
        "desc_고기 구이": "불에 구운 고기. 영양가가 높다.",
        "desc_전투 식량": "군용 전투 식량. 포만감을 크게 채워주고 에너지를 제공한다.",
        "desc_에너지 드링크": "고농축 카페인 음료. 갈증을 해소하고 스태미나를 대폭 회복한다.",
        "desc_생수": "깨끗한 생수 한 병.",
        "desc_탄산음료": "따끈한 탄산음료. 갈증 해소와 기분 전환에 좋다.",
        "desc_커피": "인스턴트 커피. 졸음을 쫓아준다.",
        "desc_구급상자": "기본적인 응급 처치 키트.",
        "desc_진통제": "강력한 진통제. 통증을 잠시 잊게 해준다.",
        "desc_고급 치료킷": "전문 의료 키트. 중상도 치료 가능.",
        "desc_약초": "야생에서 채집한 약초. 크래프팅 재료.",
        "desc_붕대": "깨끗한 붕대. 출혈을 멈출 수 있다.",
        "desc_무기": "쇠파이프. 기본적인 근접 무기.",
        "desc_파이프": "녹슨 쇠파이프.",
        "desc_나이프": "날카로운 사냥용 나이프.",
        "desc_도끼": "목재 벌목용 도끼. 강력하지만 느리다.",
        "desc_야구방망이": "알루미늄 야구방망이. 넓은 타격 범위.",
        "desc_권총": "9mm 권총. 탄약 필요.",
        "desc_레버액션 소총": "클래식한 레버액션 소총. 강력하지만 재장전이 느리다.",
        "desc_탄약": "9mm 탄약.",
        "desc_가방": "튼튼한 배낭. 인벤토리 최대 무게를 +15.0kg 늘려준다.",
        "desc_방독면": "오염된 공기를 차단하는 방독면.",
        "desc_방탄조끼": "방탄 재질의 조끼. 대미지를 크게 줄여준다.",
        "desc_운동화": "가볍고 튼튼한 운동화. 이동 속도가 빨라진다.",
        "desc_손전등": "LED 손전등. 밤에 시야를 밝혀준다.",
        "desc_비상용 배터리": "충전식 비상 배터리. 여러 장비에 사용 가능.",
        "desc_지도": "이 지역의 약도. 미니맵 범위가 넓어진다.",
        "desc_개조 손전등": "초강력 개조 손전등. 밤에도 낮처럼 볼 수 있다.",
        "desc_나무": "건축 및 크래프팅용 목재.",
        "desc_못": "건축용 못. 바리케이드 제작에 필요.",
        "desc_천": "찢어진 천 조각. 다양한 용도.",
        "desc_고철": "재활용 가능한 금속 조각.",
        "desc_바리케이드 재료": "바리케이드 구축에 사용되는 재료 묶음.",
        "desc_라디오 부품": "장거리 무전기 조립에 필요한 핵심 부품. 3개를 모으면 구조 신호를 보낼 수 있다.",
        "desc_장거리 무전기": "조립 완료된 장거리 무전기! 구조 신호를 보낼 수 있다.",
        "desc_군사 문서": "기밀 등급의 군사 문서. 감염의 원인에 대한 단서가 적혀있다.",
        "desc_사진": "누군가의 가족 사진. 뒷면에 메시지가 적혀있다.",
        "desc_기계 부품": "복잡한 기계의 부품. 정밀 장비 개조에 필수적이다.",
        "desc_농작물": "밭에서 자란 싱싱한 농작물. 배를 든든하게 채운다.",
        "desc_횃불": "나무와 천으로 만든 횃불. 주변을 밝혀준다.",
        "desc_함정": "고철와 못으로 만든 트랩. 좀비를 잡을 수 있다.",

        # 상호작용 로그 및 NPC 메시지
        "acquired_item": "'{0}'을(를) 획득했습니다!",
        "trade_possible": "[가능] 획득: {0}  |  지불: {1} x{2} (보유: {3})",
        "trade_impossible": "[부족] 획득: {0}  |  지불: {1} x{2} (보유: {3})",
        "trade_close": "거래 종료",
        "quest_registered": "★ 임무 등록: {0}에게 {1} {2}개 전달",
        "quest_can_complete": "[완료 가능] 전달: {0} x{1}  |  보상: {2} x{3} (현재: {4})",
        "quest_in_progress": "[진행 중] 필요: {0} x{1}  |  보상: {2} x{3} (현재: {4})",
        "quest_later": "나중에",
        "quest_ready": "완료 가능",
        "quest_dialogue": "이봐 생존자. {0} {1}개만 좀 가져다 주겠나? 대가로 {2} {3}개를 주지. (필요: {0} {1}개 | 보상: {2} {3}개)",
        "log_gather_wood": "나무를 채집했습니다!",
        "log_gather_herb": "약초를 발견했습니다!",
        "log_gather_nothing": "관목을 뒤졌지만 아무것도 없었습니다.",
        "log_trade_complete": "거래 완료: {0} x{1} → {2}",
        "log_item_lacking": "{0}이(가) 부족합니다.",
        "log_quest_complete": "임무 완료: {0} x{1} 획득",
        "log_sleep_daytime": "낮에는 수면이 불가능합니다. (18:00 ~ 6:00 가능)",
        "log_sleep_start": "잠자리에 듭니다... (다음 날 아침 6시가 됩니다)",
        "log_bag_full": " (가방 꽉참: 바닥에 떨굼)",

        # main.py 로그 메시지
        "log_sandbox_started": "★ [샌드박스 모드] 모든 아이템이 지급되었습니다!",
        "log_survival_started": "★ 30일간의 생존이 시작됩니다. 구조대가 올 때까지 살아남으세요!",
        "log_game_loaded": "★ Day {0} - 게임을 불러왔습니다.",
        "log_game_saved": "✓ 게임이 저장되었습니다.",
        "log_barricade_installed": "바리케이드를 설치했습니다! (방어도 +10 → {0})",
        "log_barricade_only_inside": "바리케이드 재료는 은신처 내부에서만 사용할 수 있습니다.",
        "log_item_used": "'{0}'을(를) 사용했습니다.",
        "log_item_equipped": "'{0}'을(를) 장착했습니다.",
        "log_item_dropped": "'{0}'을(를) 버렸습니다.",
        "log_item_unequipped": "'{0}'을(를) 해제했습니다.",
        "log_inventory_full": "인벤토리 빈 공간이 부족합니다!",
        "log_crafting_started": "'{0}' 제작을 시작합니다...",
        "log_craft_success": "✓ '{0}' 제작을 완료했습니다!",
        "log_zombie_killed": "좀비를 처치했습니다!",
        "log_item_dropped_by_zombie": "  [{0}] 드롭!",
        "log_ammo_lacking": "탄약이 부족합니다!",
        "log_stealth_zombie_damage": "은신형 좀비에게 {0} 피해!",
        "log_day_header": "═══ Day {0} ═══",
        "log_new_biome": "새로운 지역 발견: {0}",
        "log_horde_warning": "⚠ [호드 경고] 오늘 밤 대규모 좀비 습격이 예상됩니다! ({0}마리)",
        "log_raid_warning": "⚠ [습격 경고] 오늘 밤 좀비 무리가 접근하고 있습니다... ({0}마리)",
        "notify_raid_forecast": "⚠ 습격 예보! 방어를 준비하세요!",
        "log_raid_defended": "★ 습격 방어 완료: 좀비 무리를 모두 물리쳤습니다! ★",
        "notify_raid_defended": "★ 습격 방어 성공! ★",
        "log_raid_started": "⚔ 습격 시작! {0}마리의 좀비가 은신처를 공격합니다!",
        "log_barricade_blocked": "★ 바리케이드가 습격을 막아냈습니다! (방어도 -{0})",
        "log_barricade_breached": "✕ 바리케이드가 돌파되었습니다! (HP -{0}, 방어도 → 0)",

        # NPC 및 좀비 타입 번역
        "떠돌이 상인": "떠돌이 상인",
        "생존자": "생존자",
        "군인": "군인",
        "여어, 반가워! 좋은 물건 많이 있어.": "여어, 반가워! 좋은 물건 많이 있어.",
        "살아있는 사람이라니... 도와줄 수 있나요?": "살아있는 사람이라니... 도와줄 수 있나요?",
        "생존자인가? 이 지역 정보를 공유할 수 있소.": "생존자인가? 이 지역 정보를 공유할 수 있소.",
        "일반 좀비": "일반 좀비",
        "러너 좀비": "러너 좀비",
        "탱크 좀비": "탱크 좀비",
        "스파이더 좀비": "스파이더 좀비",
        "은신형 좀비": "은신형 좀비",
        "stealth_zombie": "은신형 좀비",
    },
    "en": {
        # Main Menu
        "game_title": "30 Days to Survive",
        "game_subtitle": "Zombie Apocalypse Open-World Survival",
        "new_game": "New Game",
        "load_game": "Continue",
        "settings": "Settings",
        "quit": "Quit",
        "version_info": "v1.1  |  Python + Pygame",

        # World Creation
        "world_creation_title": "Create New World",
        "world_name": "World Name:",
        "difficulty": "Difficulty:",
        "day_length": "Day Length (min)",
        "resource_density": "Resource Density",
        "weather_variability": "Weather Variability",
        "zombie_activity": "Zombie Activity",
        "building_density": "Building Density",
        "survival_days": "Survival Days",
        "start_world": "Create World",
        "back": "◀ Back",

        # Settings
        "settings_title": "Settings",
        "resolution": "Resolution:",
        "screen_mode": "Screen Mode:",
        "fullscreen": "Fullscreen",
        "windowed": "Windowed",
        "particle_quality": "Particles:",
        "particle_none": "Off",
        "particle_low": "Low",
        "particle_normal": "Medium",
        "particle_high": "High",
        "language": "Language:",
        "apply": "Apply",

        # HUD
        "hp": "HP",
        "hunger": "Hunger",
        "thirst": "Thirst",
        "stress": "Stress",
        "stamina": "Stamina",
        "defense": "Defense",
        "kills": "Kills",
        "day": "Day",
        "fist": "Fist",
        "exhausted": "Exhausted!",

        # Inventory
        "inventory": "Inventory",
        "equipment": "Equipment",
        "weight": "Weight",
        "left_click_use": "LMB: Use",
        "right_click_equip": "RMB: Equip",

        # Crafting
        "crafting": "Crafting",

        # Interaction
        "press_e_interact": "E: Interact",
        "press_e_enter": "E: Enter",
        "press_e_exit": "E: Exit",
        "press_e_search": "E: Search",
        "controls_hint": "E:Interact  I:Inventory  C:Craft  Tab:Map  ESC:Menu",

        # Building Interior
        "entering_building": "Entering building...",
        "exiting_building": "Leaving building...",
        "searched_already": "Already searched.",
        "found_nothing": "Found nothing.",
        "found_items": "Found: ",
        "zombie_intrusion": "A zombie has broken into the building!",
        "zombie_followed": "A zombie followed you inside!",
        "zombie_followed_outside": "A zombie followed you outside!",

        # Pause
        "paused": "Paused",
        "resume": "Resume",
        "save_game": "Save Game",
        "save_and_quit": "Save & Quit",
        "quit_no_save": "Quit Without Saving",

        # Events
        "game_saved": "Game saved.",
        "new_day": "Day {} has dawned.",
        "zombie_horde": "A zombie horde approaches!",
        "found_survivor": "You found a survivor!",

        # Difficulty
        "peaceful": "Peaceful",
        "easy": "Easy",
        "normal": "Normal",
        "hard": "Hard",
        "hardcore": "Hardcore",
        "challenge": "Challenge",

        # Ending
        "ending_survived": "You Survived!",
        "ending_died": "You Died...",

        # Furniture
        "furniture_냉장고": "Refrigerator",
        "furniture_선반": "Shelf",
        "furniture_서랍장": "Dresser",
        "furniture_침대밑": "Under Bed",
        "furniture_약품장": "Medicine Cabinet",
        "furniture_진열대": "Display Shelf",
        "furniture_카운터": "Counter",
        "furniture_사물함": "Locker",
        "furniture_무기함": "Weapon Locker",
        "furniture_군용상자": "Military Crate",
        "furniture_통신장비": "Radio Equipment",

        # Extra Labels & Hints
        "equip_head": "Head",
        "equip_body": "Body",
        "equip_feet": "Feet",
        "equip_weapon": "Weapon",
        "inventory_hint": "LMB: Use  |  Drag: Equip/Unequip  |  RMB: Drop",
        "defense_label": "Defense: {}",
        "kills_label": "Kills: {}",
        "stealth_mode": "◆ Stealth ◆",
        "weather_label": "Weather: {}",
        "hud_controls_hint": "E:Interact  I:Inventory  C:Craft  Tab:Map  LCTRL:Sneak  ESC:Menu",
        "click_to_main": "Click to return to main menu",
        "sandbox_mode": "🔧 Sandbox Mode (All Items Granted)",
        "world_name_default": "World 1",

        # Weather
        "weather_맑음": "Sunny",
        "weather_비": "Rainy",
        "weather_안개": "Foggy",
        "weather_눈": "Snowy",
        "weather_폭풍우": "Stormy",

        # Periods
        "period_새벽": "Dawn",
        "period_낮": "Day",
        "period_황혼": "Dusk",
        "period_밤": "Night",

        # 바이옴
        "도시": "City",
        "주거지": "Residential Area",
        "산림": "Forest",
        "병원구역": "Hospital District",
        "군사기지": "Military Base",
        "호수": "Lake",
        "황무지": "Wasteland",
        "공장단지": "Factory District",
        "밀밭": "Wheat Field",

        # Difficulty Preset Descriptions
        "desc_peaceful": "Zombies rarely spawn and resources are abundant. Good for exploring and building.",
        "desc_easy": "Fewer zombies and plenty of resources. Suitable for beginners.",
        "desc_normal": "Balanced difficulty. Requires strategic gameplay.",
        "desc_hard": "Stronger zombies and scarce resources. For experienced survivors only.",
        "desc_hardcore": "Extremely scarce resources. Zombies are fast and lethal. Permadeath enabled.",
        "desc_challenge": "Ultimate challenge. Everything wants to kill you. For true survivors.",

        # Item Names
        "item_식량통조림": "Canned Food",
        "item_마른 빵": "Dry Bread",
        "item_에너지바": "Energy Bar",
        "item_고기 구이": "Roasted Meat",
        "item_전투 식량": "MRE",
        "item_에너지 드링크": "Energy Drink",
        "item_생수": "Water",
        "item_탄산음료": "Soda",
        "item_커피": "Coffee",
        "item_구급상자": "First Aid Kit",
        "item_진통제": "Painkillers",
        "item_고급 치료킷": "Medkit",
        "item_약초": "Herbs",
        "item_붕대": "Bandage",
        "item_무기": "Weapon",
        "item_파이프": "Pipe",
        "item_나이프": "Knife",
        "item_도끼": "Axe",
        "item_야구방망이": "Baseball Bat",
        "item_권총": "Pistol",
        "item_레버액션 소총": "Rifle",
        "item_탄약": "Ammo",
        "item_가방": "Backpack",
        "item_방독면": "Gas Mask",
        "item_방탄조끼": "Body Armor",
        "item_운동화": "Sneakers",
        "item_손전등": "Flashlight",
        "item_비상용 배터리": "Battery",
        "item_지도": "Map",
        "item_개조 손전등": "Modified Flashlight",
        "item_나무": "Wood",
        "item_못": "Nails",
        "item_천": "Cloth",
        "item_고철": "Scrap Metal",
        "item_바리케이드 재료": "Barricade Material",
        "item_라디오 부품": "Radio Parts",
        "item_장거리 무전기": "Long-range Radio",
        "item_군사 문서": "Military Document",
        "item_사진": "Photo",
        "item_기계 부품": "Mechanical Parts",
        "item_농작물": "Crops",
        "item_횃불": "Torch",
        "item_함정": "Trap",

        # Item Descriptions
        "desc_식량통조림": "Sealed canned meat. Expired, but still edible.",
        "desc_마른 빵": "Stale, dry bread. Good enough to fill your stomach.",
        "desc_에너지바": "High-calorie energy bar. Quickly replenishes energy.",
        "desc_고기 구이": "Flame-grilled meat. Highly nutritious.",
        "desc_전투 식량": "Military MRE. Greatly fills hunger and provides energy.",
        "desc_에너지 드링크": "High-caffeine drink. Quenches thirst and restores stamina.",
        "desc_생수": "A clean bottle of water.",
        "desc_탄산음료": "Warm soda. Good for quenching thirst and lifting mood.",
        "desc_커피": "Instant coffee. Keeps sleepiness away.",
        "desc_구급상자": "A basic emergency first aid kit.",
        "desc_진통제": "Strong painkillers. Temporarily eases pain.",
        "desc_고급 치료킷": "Professional medical kit. Can treat severe injuries.",
        "desc_약초": "Herbs gathered from the wild. Crafting material.",
        "desc_붕대": "Clean bandage. Can stop bleeding.",
        "desc_무기": "Iron pipe. A basic melee weapon.",
        "desc_파이프": "A rusty iron pipe.",
        "desc_나이프": "A sharp hunting knife.",
        "desc_도끼": "A lumber axe. Strong but slow.",
        "desc_야구방망이": "An aluminum baseball bat. Wide swing radius.",
        "desc_권총": "A 9mm pistol. Requires ammo.",
        "desc_레버액션 소총": "A classic lever-action rifle. Strong but slow reload.",
        "desc_탄약": "9mm ammunition.",
        "desc_가방": "A sturdy backpack. Increases max weight capacity by +15.0kg.",
        "desc_방독면": "A gas mask that blocks contaminated air.",
        "desc_방탄조끼": "Bulletproof armor vest. Greatly reduces incoming damage.",
        "desc_운동화": "Lightweight, durable sneakers. Increases movement speed.",
        "desc_손전등": "An LED flashlight. Lights up the night.",
        "desc_비상용 배터리": "Rechargeable emergency battery. Can be used for various gear.",
        "desc_지도": "A sketch map of this area. Expands minimap range.",
        "desc_개조 손전등": "Ultra-powerful modified flashlight. Lights up the night like day.",
        "desc_나무": "Timber for construction and crafting.",
        "desc_못": "Construction nails. Needed for building barricades.",
        "desc_천": "Torn piece of cloth. Various uses.",
        "desc_고철": "Recyclable pieces of metal.",
        "desc_바리케이드 재료": "A bundle of materials used to build barricades.",
        "desc_라디오 부품": "Key parts for building a long-range radio. Collect 3 to call for rescue.",
        "desc_장거리 무전기": "Assembled long-range radio! Ready to call for rescue.",
        "desc_군사 문서": "Classified military documents. Contains clues about the outbreak.",
        "desc_사진": "Someone's family photo. A message is written on the back.",
        "desc_기계 부품": "Complex mechanical parts. Vital for modifying precision gear.",
        "desc_농작물": "Fresh crops from the field. Fills your stomach nicely.",
        "desc_횃불": "A torch made of wood and cloth. Illuminates your surroundings.",
        "desc_함정": "A trap made of scrap metal and nails. Can catch zombies.",

        # Interaction Logs and NPC Messages
        "acquired_item": "Acquired '{0}'!",
        "trade_possible": "[Available] Get: {0}  |  Pay: {1} x{2} (Own: {3})",
        "trade_impossible": "[Lacking] Get: {0}  |  Pay: {1} x{2} (Own: {3})",
        "trade_close": "Close Trade",
        "quest_registered": "★ Quest Registered: Deliver {2} of {1} to {0}",
        "quest_can_complete": "[Complete] Hand in: {0} x{1}  |  Reward: {2} x{3} (Own: {4})",
        "quest_in_progress": "[In Progress] Need: {0} x{1}  |  Reward: {2} x{3} (Own: {4})",
        "quest_later": "Later",
        "quest_ready": "Ready",
        "quest_dialogue": "Hey survivor. Could you bring me {1} of {0}? I will give you {3} of {2} in return. (Need: {0} x{1} | Reward: {2} x{3})",
        "log_gather_wood": "Gathered wood!",
        "log_gather_herb": "Found herbs!",
        "log_gather_nothing": "Searched the bush but found nothing.",
        "log_trade_complete": "Trade complete: {0} x{1} → {2}",
        "log_item_lacking": "Not enough {0}.",
        "log_quest_complete": "Quest complete: Acquired {0} x{1}",
        "log_sleep_daytime": "Cannot sleep during the day. (Available from 18:00 to 6:00)",
        "log_sleep_start": "Going to sleep... (Time skips to 6:00 AM next day)",
        "log_bag_full": " (Bag full: Dropped on the ground)",

        # main.py Log Messages
        "log_sandbox_started": "★ [Sandbox Mode] All items granted!",
        "log_survival_started": "★ Survival of 30 days begins. Survive until rescue arrives!",
        "log_game_loaded": "★ Day {0} - Game loaded.",
        "log_game_saved": "✓ Game saved.",
        "log_barricade_installed": "Installed barricade! (Defense +10 → {0})",
        "log_barricade_only_inside": "Barricade materials can only be used inside the shelter.",
        "log_item_used": "Used '{0}'.",
        "log_item_equipped": "Equipped '{0}'.",
        "log_item_dropped": "Dropped '{0}'.",
        "log_item_unequipped": "Unequipped '{0}'.",
        "log_inventory_full": "Not enough inventory space!",
        "log_crafting_started": "Started crafting '{0}'...",
        "log_craft_success": "✓ Crafted '{0}' successfully!",
        "log_zombie_killed": "Zombie defeated!",
        "log_item_dropped_by_zombie": "  [{0}] dropped!",
        "log_ammo_lacking": "Not enough ammo!",
        "log_stealth_zombie_damage": "Inflicted {0} damage to stealthy zombie!",
        "log_day_header": "═══ Day {0} ═══",
        "log_new_biome": "Discovered new area: {0}",
        "log_horde_warning": "⚠ [Horde Warning] Large scale zombie raid expected tonight! ({0} zombies)",
        "log_raid_warning": "⚠ [Raid Warning] A zombie swarm is approaching tonight... ({0} zombies)",
        "notify_raid_forecast": "⚠ Raid forecast! Prepare your defense!",
        "log_raid_defended": "★ Raid defense complete: Swarm defeated! ★",
        "notify_raid_defended": "★ Raid Defended Successfully! ★",
        "log_raid_started": "⚔ Raid started! {0} zombies are attacking the shelter!",
        "log_barricade_blocked": "★ Barricade blocked the raid! (Defense -{0})",
        "log_barricade_breached": "✕ Barricade breached! (HP -{0}, Defense → 0)",

        # NPC and Zombie Type Translations
        "떠돌이 상인": "Wandering Merchant",
        "생존자": "Survivor",
        "군인": "Soldier",
        "여어, 반가워! 좋은 물건 많이 있어.": "Hello, nice to meet you! I have good items.",
        "살아있는 사람이라니... 도와줄 수 있나요?": "A living person... can you help me?",
        "생존자인가? 이 지역 정보를 공유할 수 있소.": "Survivor? I can share some regional info.",
        "일반 좀비": "Normal Zombie",
        "러너 좀비": "Runner Zombie",
        "탱크 좀비": "Tank Zombie",
        "스파이더 좀비": "Spider Zombie",
        "은신형 좀비": "Stealthy Zombie",
        "stealth_zombie": "Stealthy Zombie",
    },
}


def set_language(lang):
    """언어 설정 (ko/en)"""
    global _current_lang
    if lang in STRINGS:
        _current_lang = lang


def get_language():
    return _current_lang


def t(key, *args):
    """번역 문자열 조회. args가 있으면 format 적용"""
    if key is None:
        return ""
        
    # 1단계: 직접 키 조회
    text = STRINGS.get(_current_lang, STRINGS["ko"]).get(key)
    
    # 2단계: 아이템 이름 조회를 위해 item_ 접두사를 붙여서 조회
    if text is None and not key.startswith("item_") and not key.startswith("desc_") and not key.startswith("furniture_"):
        text = STRINGS.get(_current_lang, STRINGS["ko"]).get(f"item_{key}")
    
    # 3단계: 여전히 없으면 한국어 사전에서 조회
    if text is None:
        text = STRINGS.get("ko", {}).get(key)
        if text is None and not key.startswith("item_"):
            text = STRINGS.get("ko", {}).get(f"item_{key}", key)
            
    if args:
        # args 내부의 문자열들도 번역(아이템 이름 등이 포함되어 있을 수 있음)
        translated_args = [t(str(arg)) if isinstance(arg, str) else arg for arg in args]
        try:
            return text.format(*translated_args)
        except (IndexError, KeyError):
            return text
    return text


def get_available_languages():
    return list(STRINGS.keys())


def get_language_name(lang):
    names = {"ko": "한국어", "en": "English"}
    return names.get(lang, lang)
