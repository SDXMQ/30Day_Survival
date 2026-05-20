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
        "start_world": "Start World",
        "back": "◀ Back",

        # Settings
        "settings_title": "Settings",
        "resolution": "Resolution:",
        "screen_mode": "Screen Mode:",
        "fullscreen": "Fullscreen",
        "windowed": "Windowed",
        "particle_quality": "Particle Quality:",
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
        "weight": "Weight",
        "left_click_use": "LMB: Use",
        "right_click_equip": "RMB: Equip",

        # Crafting
        "crafting": "Crafting",

        # Interaction
        "press_e_interact": "E: Interact",
        "press_e_enter": "E: Enter Building",
        "press_e_exit": "E: Exit",
        "press_e_search": "E: Search",
        "controls_hint": "E:Interact  I:Inventory  C:Craft  Tab:Map  ESC:Menu",

        # Building Interior
        "entering_building": "Entering building...",
        "exiting_building": "Leaving building...",
        "searched_already": "Already searched.",
        "found_nothing": "Found nothing.",
        "found_items": "Found: ",

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
    text = STRINGS.get(_current_lang, STRINGS["ko"]).get(key)
    if text is None:
        # 폴백: 한국어 → 키 이름
        text = STRINGS.get("ko", {}).get(key, key)
    if args:
        try:
            return text.format(*args)
        except (IndexError, KeyError):
            return text
    return text


def get_available_languages():
    return list(STRINGS.keys())


def get_language_name(lang):
    names = {"ko": "한국어", "en": "English"}
    return names.get(lang, lang)
