"""
settings.py - 게임 설정, 상수, 색상 팔레트
확장 용이성을 위해 모든 게임 데이터를 데이터 드리븐 방식으로 관리
"""
import json
import os

# ============================================================
# 화면 설정
# ============================================================
RESOLUTION_OPTIONS = [
    (1280, 720),
    (1366, 768),
    (1600, 900),
    (1920, 1080),
]
DEFAULT_RESOLUTION = (1280, 720)
FPS = 60
FULLSCREEN = False

# ============================================================
# 타일 & 청크 설정
# ============================================================
TILE_SIZE = 32
CHUNK_SIZE = 16  # 청크 하나 = 16x16 타일
RENDER_DISTANCE = 3  # 플레이어 주변 청크 렌더 거리

# ============================================================
# 색상 팔레트 (모던하고 세련된 색상)
# ============================================================
class Colors:
    # 기본
    BLACK = (10, 10, 15)
    WHITE = (240, 240, 245)
    GRAY = (128, 128, 135)
    DARK_GRAY = (45, 45, 55)
    LIGHT_GRAY = (180, 180, 190)

    # UI 색상
    UI_BG = (20, 22, 30, 200)
    UI_BG_SOLID = (20, 22, 30)
    UI_BORDER = (60, 65, 80)
    UI_ACCENT = (80, 180, 255)
    UI_ACCENT_WARM = (255, 160, 60)
    UI_DANGER = (255, 70, 70)
    UI_SUCCESS = (70, 220, 100)
    UI_WARNING = (255, 200, 50)
    UI_TEXT = (220, 225, 235)
    UI_TEXT_DIM = (140, 145, 160)
    UI_PANEL = (30, 32, 42, 220)
    UI_HIGHLIGHT = (100, 200, 255, 40)

    # 하늘 색상 (시간대별)
    SKY_DAWN = (255, 180, 120)
    SKY_DAY = (135, 200, 255)
    SKY_DUSK = (200, 100, 80)
    SKY_NIGHT = (15, 15, 40)

    # 바이옴 타일 색상
    GRASS_1 = (65, 130, 55)
    GRASS_2 = (75, 145, 60)
    GRASS_3 = (55, 120, 50)
    DIRT_1 = (140, 110, 70)
    DIRT_2 = (155, 120, 75)
    ROAD = (80, 80, 90)
    ROAD_LINE = (200, 200, 60)
    CONCRETE = (160, 160, 165)
    WATER_1 = (40, 100, 180)
    WATER_2 = (50, 120, 200)
    SAND = (210, 190, 140)
    MUD = (100, 80, 50)

    # 건물 색상
    WALL_BRICK = (150, 80, 60)
    WALL_CONCRETE = (140, 140, 145)
    WALL_WOOD = (130, 95, 55)
    ROOF_1 = (100, 60, 45)
    ROOF_2 = (70, 70, 80)
    DOOR = (90, 65, 40)
    WINDOW = (150, 200, 230, 150)
    FLOOR_WOOD = (160, 120, 70)
    FLOOR_TILE = (170, 170, 175)

    # 캐릭터 색상
    PLAYER_SKIN = (220, 185, 150)
    PLAYER_SHIRT = (60, 90, 60)
    PLAYER_PANTS = (50, 55, 65)
    PLAYER_HAIR = (60, 40, 25)

    ZOMBIE_SKIN = (120, 155, 100)
    ZOMBIE_SKIN_DARK = (90, 120, 75)
    ZOMBIE_CLOTHES = (80, 70, 65)
    ZOMBIE_BLOOD = (150, 30, 30)

    NPC_MERCHANT_CLOAK = (100, 75, 55)
    NPC_SURVIVOR_SHIRT = (70, 80, 120)
    NPC_SOLDIER_UNIFORM = (80, 95, 60)

    # 자연물 색상
    TREE_TRUNK = (90, 65, 40)
    TREE_LEAVES_1 = (45, 110, 40)
    TREE_LEAVES_2 = (55, 130, 45)
    TREE_LEAVES_3 = (35, 95, 35)
    TREE_PINE = (30, 80, 35)
    ROCK_1 = (130, 130, 135)
    ROCK_2 = (110, 110, 115)
    BUSH = (50, 100, 45)

    # 이펙트 색상
    FIRE_1 = (255, 200, 50)
    FIRE_2 = (255, 130, 30)
    FIRE_3 = (255, 80, 20)
    BLOOD = (180, 25, 25)
    SMOKE = (100, 100, 110, 150)
    RAIN = (150, 180, 220, 180)
    SNOW = (230, 235, 245, 200)
    FOG = (180, 185, 195, 80)
    MUZZLE_FLASH = (255, 255, 180)

    # 메뉴/타이틀
    TITLE_GLOW = (255, 100, 50)
    MENU_BG = (12, 14, 22)
    EMBER = (255, 130, 40)

# ============================================================
# 난이도 프리셋
# ============================================================
DIFFICULTY_PRESETS = {
    "평화로움": {
        "id": "peaceful",
        "description": "좀비가 거의 출현하지 않고 자원이 풍부합니다. 탐험과 건설에 집중할 수 있습니다.",
        "zombie_spawn_rate": 0.1,
        "resource_multiplier": 3.0,
        "damage_multiplier": 0.3,
        "hunger_rate": 0.5,
        "thirst_rate": 0.5,
        "stress_rate": 0.3,
        "night_danger": 0.2,
        "loot_quality": 1.5,
        "zombie_hp_mult": 0.5,
        "zombie_damage_mult": 0.3,
        "zombie_speed_mult": 0.7,
        "max_zombies": 5,
        "raid_chance": 0.02,
    },
    "쉬움": {
        "id": "easy",
        "description": "좀비 수가 적고 자원이 넉넉합니다. 서바이벌 입문자에게 적합합니다.",
        "zombie_spawn_rate": 0.3,
        "resource_multiplier": 2.0,
        "damage_multiplier": 0.6,
        "hunger_rate": 0.7,
        "thirst_rate": 0.7,
        "stress_rate": 0.5,
        "night_danger": 0.5,
        "loot_quality": 1.3,
        "zombie_hp_mult": 0.7,
        "zombie_damage_mult": 0.6,
        "zombie_speed_mult": 0.85,
        "max_zombies": 10,
        "raid_chance": 0.05,
    },
    "보통": {
        "id": "normal",
        "description": "균형 잡힌 난이도. 전략적 플레이가 필요합니다.",
        "zombie_spawn_rate": 0.6,
        "resource_multiplier": 1.0,
        "damage_multiplier": 1.0,
        "hunger_rate": 1.0,
        "thirst_rate": 1.0,
        "stress_rate": 1.0,
        "night_danger": 1.0,
        "loot_quality": 1.0,
        "zombie_hp_mult": 1.0,
        "zombie_damage_mult": 1.0,
        "zombie_speed_mult": 1.0,
        "max_zombies": 20,
        "raid_chance": 0.1,
    },
    "어려움": {
        "id": "hard",
        "description": "좀비가 강하고 자원이 부족합니다. 숙련된 생존자만 도전하세요.",
        "zombie_spawn_rate": 0.85,
        "resource_multiplier": 0.6,
        "damage_multiplier": 1.5,
        "hunger_rate": 1.3,
        "thirst_rate": 1.3,
        "stress_rate": 1.3,
        "night_danger": 1.5,
        "loot_quality": 0.7,
        "zombie_hp_mult": 1.5,
        "zombie_damage_mult": 1.5,
        "zombie_speed_mult": 1.15,
        "max_zombies": 30,
        "raid_chance": 0.18,
    },
    "하드코어": {
        "id": "hardcore",
        "description": "자원 극도로 부족. 좀비가 매우 빠르고 강합니다. 사망 시 세이브 삭제.",
        "zombie_spawn_rate": 1.0,
        "resource_multiplier": 0.35,
        "damage_multiplier": 2.0,
        "hunger_rate": 1.6,
        "thirst_rate": 1.6,
        "stress_rate": 1.6,
        "night_danger": 2.0,
        "loot_quality": 0.5,
        "zombie_hp_mult": 2.0,
        "zombie_damage_mult": 2.0,
        "zombie_speed_mult": 1.3,
        "max_zombies": 40,
        "raid_chance": 0.25,
        "permadeath": True,
    },
    "챌린지": {
        "id": "challenge",
        "description": "극한의 도전. 모든 것이 당신을 죽이려 합니다. 진정한 서바이버만.",
        "zombie_spawn_rate": 1.2,
        "resource_multiplier": 0.2,
        "damage_multiplier": 3.0,
        "hunger_rate": 2.0,
        "thirst_rate": 2.0,
        "stress_rate": 2.0,
        "night_danger": 3.0,
        "loot_quality": 0.3,
        "zombie_hp_mult": 3.0,
        "zombie_damage_mult": 2.5,
        "zombie_speed_mult": 1.5,
        "max_zombies": 60,
        "raid_chance": 0.35,
        "permadeath": True,
    },
}

# ============================================================
# 월드 생성 기본값
# ============================================================
DEFAULT_WORLD_SETTINGS = {
    "seed": None,  # None = 랜덤
    "difficulty": "보통",
    "day_length_minutes": 12,  # 실시간 분
    "resource_density": 1.0,  # 0.2 ~ 3.0
    "weather_variability": 1.0,  # 0.0 ~ 2.0
    "world_name": "월드 1",
    "zombie_activity": 1.0,  # 0.0 ~ 2.0
    "building_density": 1.0,  # 0.5 ~ 2.0
    "starting_items": True,
    "enable_events": True,
    "total_days": 30,
    "sandbox": False,  # 샌드박스 모드 (개발용)
}

# ============================================================
# 플레이어 기본 스탯
# ============================================================
PLAYER_MAX_HP = 100
PLAYER_MAX_HUNGER = 100
PLAYER_MAX_THIRST = 100
PLAYER_MAX_STRESS = 100
PLAYER_MAX_STAMINA = 100
PLAYER_SPEED = 3.0  # 타일/초
PLAYER_SPRINT_SPEED = 5.0
PLAYER_INTERACT_RANGE = 1.5  # 타일

# ============================================================
# 게임 타이밍
# ============================================================
GAME_HOURS_PER_DAY = 24
DAWN_HOUR = 5
DAY_HOUR = 7
DUSK_HOUR = 18
NIGHT_HOUR = 20

# ============================================================
# 전투 설정
# ============================================================
MELEE_RANGE = 1.2
RANGED_MAX_RANGE = 12.0
ATTACK_COOLDOWN = 0.5  # 초
KNOCKBACK_FORCE = 3.0
INVINCIBILITY_FRAMES = 30  # 프레임 수

# ============================================================
# 바이옴 정의 (확장 가능)
# ============================================================
BIOMES = {
    "도시": {
        "id": "city",
        "base_tile": "concrete",
        "building_chance": 0.7,
        "tree_chance": 0.01,
        "zombie_density": 1.5,
        "loot_modifier": 1.2,
        "road_interval": 8,
        "colors": {
            "ground": Colors.CONCRETE,
            "accent": Colors.ROAD,
        },
    },
    "주거지": {
        "id": "residential",
        "base_tile": "grass",
        "building_chance": 0.5,
        "tree_chance": 0.08,
        "zombie_density": 1.0,
        "loot_modifier": 1.0,
        "road_interval": 12,
        "colors": {
            "ground": Colors.GRASS_1,
            "accent": Colors.ROAD,
        },
    },
    "산림": {
        "id": "forest",
        "base_tile": "grass",
        "building_chance": 0.01,
        "tree_chance": 0.35,
        "zombie_density": 0.5,
        "loot_modifier": 0.5,
        "road_interval": 0,
        "colors": {
            "ground": Colors.GRASS_2,
            "accent": Colors.DIRT_1,
        },
    },
    "병원구역": {
        "id": "hospital",
        "base_tile": "concrete",
        "building_chance": 0.4,
        "tree_chance": 0.02,
        "zombie_density": 1.8,
        "loot_modifier": 1.5,
        "road_interval": 10,
        "colors": {
            "ground": Colors.CONCRETE,
            "accent": Colors.WHITE,
        },
    },
    "군사기지": {
        "id": "military",
        "base_tile": "concrete",
        "building_chance": 0.5,
        "tree_chance": 0.01,
        "zombie_density": 2.0,
        "loot_modifier": 2.0,
        "road_interval": 10,
        "colors": {
            "ground": Colors.DIRT_2,
            "accent": Colors.DARK_GRAY,
        },
    },
    "호수": {
        "id": "lake",
        "base_tile": "water",
        "building_chance": 0.0,
        "tree_chance": 0.0,
        "zombie_density": 0.0,
        "loot_modifier": 0.0,
        "colors": {
            "ground": Colors.WATER_1,
            "accent": Colors.WATER_2,
        },
    },
    "황무지": {
        "id": "wasteland",
        "base_tile": "dirt",
        "building_chance": 0.02,
        "tree_chance": 0.01,
        "zombie_density": 0.8,
        "loot_modifier": 0.4,
        "road_interval": 0,
        "colors": {
            "ground": Colors.DIRT_1,
            "accent": Colors.SAND,
        },
    },
    "공장단지": {
        "id": "factory_district",
        "base_tile": "concrete",
        "building_chance": 0.8,
        "tree_chance": 0.0,
        "zombie_density": 2.0,
        "loot_modifier": 1.5,
        "road_interval": 8,
        "colors": {
            "ground": (70, 70, 75),
            "accent": (50, 50, 50),
        },
    },
    "밀밭": {
        "id": "farm",
        "base_tile": "dirt",
        "building_chance": 0.1,
        "tree_chance": 0.02,
        "zombie_density": 0.5,
        "loot_modifier": 0.8,
        "road_interval": 0,
        "colors": {
            "ground": (190, 160, 80),
            "accent": (150, 120, 50),
        },
    },
}

# ============================================================
# 설정 관리 (파일 기반 영속화)
# ============================================================
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "game_settings.json")

class GameSettings:
    """게임 설정 관리 클래스 (싱글톤 패턴)"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.resolution = list(DEFAULT_RESOLUTION)
        self.fullscreen = FULLSCREEN
        self.master_volume = 0.7
        self.sfx_volume = 0.8
        self.music_volume = 0.5
        self.show_fps = False
        self.screen_shake = True
        self.particles_quality = 2  # 0=끔, 1=낮음, 2=보통, 3=높음
        self.language = "ko"
        self.load()

    def save(self):
        data = {
            "resolution": self.resolution,
            "fullscreen": self.fullscreen,
            "master_volume": self.master_volume,
            "sfx_volume": self.sfx_volume,
            "music_volume": self.music_volume,
            "show_fps": self.show_fps,
            "screen_shake": self.screen_shake,
            "particles_quality": self.particles_quality,
        }
        try:
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def load(self):
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.resolution = data.get("resolution", list(DEFAULT_RESOLUTION))
                self.fullscreen = data.get("fullscreen", FULLSCREEN)
                self.master_volume = data.get("master_volume", 0.7)
                self.sfx_volume = data.get("sfx_volume", 0.8)
                self.music_volume = data.get("music_volume", 0.5)
                self.show_fps = data.get("show_fps", False)
                self.screen_shake = data.get("screen_shake", True)
                self.particles_quality = data.get("particles_quality", 2)
        except Exception:
            pass

    @property
    def width(self):
        return self.resolution[0]

    @property
    def height(self):
        return self.resolution[1]
