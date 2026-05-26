"""
building_interior.py - 건물 내부 탐색 시스템 (프로젝트 좀보이드 스타일)
건물 문에서 E키 → 내부 맵 진입 → 가구 탐색 → 루팅
"""
import random
import math
from settings import TILE_SIZE, Colors
from items import ITEM_DATABASE, generate_loot

# ============================================================
# 가구 루트 테이블 (건물 컨텍스트별)
# ============================================================
FURNITURE_LOOT_TABLES = {
    "냉장고": {
        "items": [
            ("생수", 0.6), ("식량통조림", 0.4), ("마른 빵", 0.3),
            ("에너지 드링크", 0.15),
        ],
        "min_items": 0, "max_items": 3,
    },
    "선반": {
        "items": [
            ("붕대", 0.3), ("비상용 배터리", 0.2), ("천", 0.25),
            ("못", 0.2), ("못", 0.15),
        ],
        "min_items": 0, "max_items": 2,
    },
    "서랍장": {
        "items": [
            ("붕대", 0.2), ("못", 0.25), ("비상용 배터리", 0.2),
            ("천", 0.3), ("못", 0.15), ("고철", 0.1),
        ],
        "min_items": 0, "max_items": 2,
    },
    "침대밑": {
        "items": [
            ("야구방망이", 0.1), ("천", 0.25), ("못", 0.15),
            ("손전등", 0.08),
        ],
        "min_items": 0, "max_items": 1,
    },
    "약품장": {
        "items": [
            ("붕대", 0.5), ("진통제", 0.3), ("진통제", 0.35),
            ("구급상자", 0.15), ("붕대", 0.25),
        ],
        "min_items": 1, "max_items": 3,
    },
    "진열대": {
        "items": [
            ("식량통조림", 0.4), ("생수", 0.5), ("비상용 배터리", 0.2),
            ("못", 0.15), ("고철", 0.1), ("못", 0.15),
        ],
        "min_items": 0, "max_items": 3,
    },
    "카운터": {
        "items": [
            ("식량통조림", 0.2), ("고철", 0.15), ("천", 0.2),
        ],
        "min_items": 0, "max_items": 1,
    },
    "사물함": {
        "items": [
            ("천", 0.3), ("못", 0.2), ("고철", 0.25),
            ("레버액션 소총", 0.03),
        ],
        "min_items": 0, "max_items": 2,
    },
    "무기함": {
        "items": [
            ("권총", 0.2), ("탄약", 0.5), ("나이프", 0.15),
            ("방탄조끼", 0.1), ("레버액션 소총", 0.08),
        ],
        "min_items": 1, "max_items": 2,
    },
    "군용상자": {
        "items": [
            ("탄약", 0.5), ("구급상자", 0.3), ("방탄조끼", 0.12),
            ("라디오 부품", 0.08), ("비상용 배터리", 0.15),
        ],
        "min_items": 1, "max_items": 3,
    },
    "통신장비": {
        "items": [
            ("라디오 부품", 0.4), ("비상용 배터리", 0.3), ("비상용 배터리", 0.2),
        ],
        "min_items": 0, "max_items": 1,
    },
}

# ============================================================
# 건물 내부 방 레이아웃 프리셋
# ============================================================
ROOM_PRESETS = {
    "주방": {
        "furniture": [("냉장고", 0, 0), ("선반", 2, 0)],
        "floor_color": Colors.FLOOR_TILE,
    },
    "거실": {
        "furniture": [("서랍장", 0, 0), ("선반", 3, 0)],
        "floor_color": Colors.FLOOR_WOOD,
    },
    "침실": {
        "furniture": [("침대", 1, 0), ("서랍장", 3, 0)],
        "floor_color": Colors.FLOOR_WOOD,
    },
    "욕실": {
        "furniture": [("선반", 0, 0)],
        "floor_color": Colors.FLOOR_TILE,
    },
    "상점홀": {
        "furniture": [("진열대", 0, 0), ("진열대", 2, 0), ("카운터", 4, 2)],
        "floor_color": Colors.FLOOR_TILE,
    },
    "창고": {
        "furniture": [("선반", 0, 0), ("선반", 2, 0), ("사물함", 0, 2)],
        "floor_color": Colors.CONCRETE,
    },
    "진료실": {
        "furniture": [("약품장", 0, 0), ("약품장", 2, 0), ("선반", 4, 0)],
        "floor_color": Colors.FLOOR_TILE,
    },
    "병실": {
        "furniture": [("약품장", 0, 0), ("침대", 3, 0)],
        "floor_color": Colors.FLOOR_TILE,
    },
    "무기고": {
        "furniture": [("무기함", 0, 0), ("무기함", 2, 0), ("군용상자", 0, 2)],
        "floor_color": Colors.CONCRETE,
    },
    "통신실": {
        "furniture": [("통신장비", 0, 0), ("군용상자", 3, 0)],
        "floor_color": Colors.CONCRETE,
    },
    "사무실": {
        "furniture": [("서랍장", 0, 0), ("사물함", 3, 0), ("선반", 0, 2)],
        "floor_color": Colors.FLOOR_TILE,
    },
    "교실": {
        "furniture": [("서랍장", 0, 0), ("선반", 3, 0), ("사물함", 5, 0)],
        "floor_color": Colors.FLOOR_WOOD,
    },
    "기계실": {
        "furniture": [("사물함", 0, 0), ("선반", 2, 0), ("카운터", 4, 0)],
        "floor_color": Colors.CONCRETE,
    },
}

# 건물 타입별 방 구성
BUILDING_LAYOUTS = {
    "house": {
        "rooms": ["주방", "거실", "침실"],
        "optional_rooms": ["욕실", "침실"],
        "default_zombie_chance": 0.2,
    },
    "store": {
        "rooms": ["상점홀"],
        "optional_rooms": ["창고", "사무실"],
        "default_zombie_chance": 0.3,
    },
    "hospital": {
        "rooms": ["진료실", "병실"],
        "optional_rooms": ["진료실", "창고"],
        "default_zombie_chance": 0.5,
    },
    "police": {
        "rooms": ["사무실", "무기고"],
        "optional_rooms": ["사무실", "창고"],
        "default_zombie_chance": 0.4,
    },
    "military": {
        "rooms": ["무기고", "통신실"],
        "optional_rooms": ["창고", "사무실"],
        "default_zombie_chance": 0.6,
    },
    "school": {
        "rooms": ["교실", "교실"],
        "optional_rooms": ["사무실", "창고", "교실"],
        "default_zombie_chance": 0.4,
    },
    "factory": {
        "rooms": ["기계실", "창고"],
        "optional_rooms": ["기계실", "사무실"],
        "default_zombie_chance": 0.5,
    },
    "warehouse": {
        "rooms": ["창고", "창고"],
        "optional_rooms": ["사무실", "창고"],
        "default_zombie_chance": 0.4,
    },
    "barn": {
        "rooms": ["창고"],
        "optional_rooms": ["창고"],
        "default_zombie_chance": 0.2,
    },
}


class Furniture:
    """가구 오브젝트"""

    def __init__(self, ftype, x, y):
        self.type = ftype
        self.x = x      # 내부 타일 좌표
        self.y = y
        self.searched = False
        self.loot = []   # 발견된 아이템 리스트

    def search(self, loot_quality=1.0):
        """가구 탐색 → 아이템 반환"""
        if self.searched:
            return []
        self.searched = True

        table = FURNITURE_LOOT_TABLES.get(self.type, {})
        items_list = table.get("items", [])
        min_items = table.get("min_items", 0)
        max_items = table.get("max_items", 2)

        found = []
        for item_name, chance in items_list:
            if random.random() < chance * loot_quality:
                found.append(item_name)

        # 아이템 수 제한
        if len(found) < min_items:
            # 최소 보장
            for item_name, chance in items_list:
                if item_name not in found:
                    found.append(item_name)
                if len(found) >= min_items:
                    break

        found = found[:max_items]
        self.loot = found
        return found

    def to_dict(self):
        return {
            "type": self.type, "x": self.x, "y": self.y,
            "searched": self.searched,
        }

    @classmethod
    def from_dict(cls, data):
        f = cls(data["type"], data["x"], data["y"])
        f.searched = data.get("searched", False)
        return f


class InteriorRoom:
    """건물 내부의 방"""

    def __init__(self, name, x, y, width, height, furniture_list=None):
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.furniture = furniture_list or []
        self.floor_color = ROOM_PRESETS.get(name, {}).get("floor_color", Colors.FLOOR_WOOD)

    def contains(self, tx, ty):
        return self.x <= tx < self.x + self.width and self.y <= ty < self.y + self.height


class BuildingInterior:
    """건물 내부 맵"""

    def __init__(self, building_type, exterior_width, exterior_height, seed=0):
        self.building_type = building_type
        # 내부 크기 = 외관 비례 (각 타일을 2배 확대)
        self.width = max(8, exterior_width * 2 + 2)   # 벽 포함
        self.height = max(8, exterior_height * 2 + 2)
        self.seed = seed

        self.rooms = []
        self.furniture = []
        self.tiles = []    # 2D 타일맵 (벽/바닥/문/window)
        self.zombies = []  # 내부 좀비 위치
        self.items_on_ground = []  # 내부 바닥 아이템 [(item_name, x, y)]
        self.door_pos = (self.width // 2, self.height - 1)  # 출입구
        self.windows = []  # 창문 리스트: [{"x", "y", "dir_x", "dir_y"}]

        self._generate(seed)

    def _generate(self, seed):
        """절차적 내부 생성"""
        rng = random.Random(seed)

        # 타일맵 초기화 (벽으로 채움)
        self.tiles = [["wall" for _ in range(self.width)] for _ in range(self.height)]

        # 바닥 (벽 안쪽)
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                self.tiles[y][x] = "floor"

        # 출입구
        dx, dy = self.door_pos
        if 0 <= dx < self.width and 0 <= dy < self.height:
            self.tiles[dy][dx] = "door"
            if dx + 1 < self.width:
                self.tiles[dy][dx + 1] = "door"

        # 레이아웃 결정
        layout = BUILDING_LAYOUTS.get(self.building_type, BUILDING_LAYOUTS["house"])
        rooms_needed = list(layout["rooms"])

        # 외관 크기에 따라 추가 방
        extra_rooms_count = max(0, (self.width * self.height) // 30 - len(rooms_needed))
        optional = layout.get("optional_rooms", [])
        for _ in range(min(extra_rooms_count, len(optional))):
            rooms_needed.append(rng.choice(optional))

        # 방 배치
        available_width = self.width - 2
        available_height = self.height - 2
        room_x = 1
        room_y = 1

        for i, room_name in enumerate(rooms_needed):
            preset = ROOM_PRESETS.get(room_name)
            if not preset:
                continue

            # 방 크기 계산
            rw = min(available_width - room_x + 1, max(4, available_width // max(1, len(rooms_needed) - i)))
            rh = max(3, available_height // 2)

            if room_x + rw > self.width - 1:
                room_x = 1
                room_y += rh + 1
            if room_y + rh > self.height - 1:
                break

            # 방 내벽 (마지막 열만)
            if i < len(rooms_needed) - 1 and room_x + rw < self.width - 1:
                for ry in range(room_y, min(room_y + rh, self.height - 1)):
                    self.tiles[ry][room_x + rw - 1] = "wall"
                # 문
                door_y = room_y + rh // 2
                if door_y < self.height - 1:
                    self.tiles[door_y][room_x + rw - 1] = "floor"

            # 가구 배치
            room_furniture = []
            for f_type, fx, fy in preset["furniture"]:
                abs_x = room_x + 1 + fx
                abs_y = room_y + 1 + fy
                if abs_x < room_x + rw - 1 and abs_y < room_y + rh - 1:
                    furn = Furniture(f_type, abs_x, abs_y)
                    room_furniture.append(furn)
                    self.furniture.append(furn)
                    self.tiles[abs_y][abs_x] = "furniture"

            room = InteriorRoom(room_name, room_x, room_y, rw, rh, room_furniture)
            self.rooms.append(room)
            room_x += rw

        # 창문 배치 (상단/좌측/우측 외벽에 1~3개)
        self.windows = []
        wall_candidates = []
        # 상단 벽 (y=0), 방향: 위(0, -1)
        for wx in range(2, self.width - 2):
            if self.tiles[0][wx] == "wall":
                wall_candidates.append((wx, 0, 0, -1))
        # 좌측 벽 (x=0), 방향: 왼쪽(-1, 0)
        for wy in range(2, self.height - 2):
            if self.tiles[wy][0] == "wall":
                wall_candidates.append((0, wy, -1, 0))
        # 우측 벽 (x=width-1), 방향: 오른쪽(1, 0)
        for wy in range(2, self.height - 2):
            if self.tiles[wy][self.width - 1] == "wall":
                wall_candidates.append((self.width - 1, wy, 1, 0))

        num_windows = min(len(wall_candidates), rng.randint(1, 3))
        if wall_candidates:
            chosen = rng.sample(wall_candidates, num_windows)
            for wx, wy, dx, dy in chosen:
                self.tiles[wy][wx] = "window"
                self.windows.append({"x": wx, "y": wy, "dir_x": dx, "dir_y": dy})

        # 은신형 좀비 스폰
        zombie_chance = layout.get("default_zombie_chance", 0.2)
        for _ in range(rng.randint(0, 3)):
            if rng.random() < zombie_chance:
                zx = rng.randint(2, self.width - 3)
                zy = rng.randint(2, self.height - 3)
                if self.tiles[zy][zx] == "floor":
                    self.zombies.append({"x": zx, "y": zy, "type": "stealth"})

    def get_tile(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return "wall"

    def is_walkable(self, x, y):
        tile = self.get_tile(int(x), int(y))
        return tile in ("floor", "door")  # window는 벽과 동일하게 이동 불가

    def get_nearby_window(self, px, py, radius=1.5):
        """플레이어 근처 창문 반환 (가장 가까운 것)"""
        best = None
        best_dist = radius + 1
        for w in self.windows:
            d = abs(w["x"] - px) + abs(w["y"] - py)
            if d <= radius and d < best_dist:
                best_dist = d
                best = w
        return best

    def get_furniture_at(self, x, y, radius=1.0):
        """좌표 근처의 가구 반환"""
        for f in self.furniture:
            if abs(f.x - x) <= radius and abs(f.y - y) <= radius:
                return f
        return None

    def get_unsearched_furniture_near(self, x, y, radius=1.5):
        """탐색되지 않은 근처 가구"""
        for f in self.furniture:
            if not f.searched and abs(f.x - x) <= radius and abs(f.y - y) <= radius:
                return f
        return None

    def is_at_exit(self, x, y):
        """출구(문) 위치인지 확인"""
        dx, dy = self.door_pos
        return abs(x - dx) <= 1.5 and abs(y - dy) <= 0.5

    def drop_item(self, item_name, wx, wy):
        """건물 내부 바닥에 아이템 드롭"""
        # 좌표를 내부 범위로 클램프
        x = max(1, min(self.width - 2, float(wx)))
        y = max(1, min(self.height - 2, float(wy)))
        self.items_on_ground.append((item_name, x, y))

    def get_ground_items_near(self, x, y, radius=2):
        """근처 바닥 아이템 반환 (World 인터페이스와 동일한 형태)"""
        result = []
        for item_tuple in self.items_on_ground:
            item_name, ix, iy = item_tuple
            if abs(ix - x) <= radius and abs(iy - y) <= radius:
                result.append(item_tuple)
        return result

    def get_nearby_objects(self, wx, wy, radius=2):
        """다형성 스텁: 내부에는 나무/바위 등 월드 오브젝트가 없음"""
        return []

    def to_dict(self):
        return {
            "type": self.building_type,
            "width": self.width,
            "height": self.height,
            "seed": self.seed,
            "furniture": [f.to_dict() for f in self.furniture],
            "items_on_ground": list(self.items_on_ground),
            "zombies": getattr(self, 'zombies', []),
            "windows": getattr(self, 'windows', []),
        }

    @classmethod
    def from_dict(cls, data, ext_w=4, ext_h=4):
        interior = cls(data["type"], ext_w, ext_h, data.get("seed", 0))
        # 탐색 상태 복원
        saved_furniture = data.get("furniture", [])
        for sf in saved_furniture:
            for f in interior.furniture:
                if f.x == sf["x"] and f.y == sf["y"] and f.type == sf["type"]:
                    f.searched = sf.get("searched", False)
                    break
        # 바닥 아이템 복원
        interior.items_on_ground = [tuple(item) for item in data.get("items_on_ground", [])]
        # 좀비 상태 복원
        interior.zombies = data.get("zombies", [])
        # 창문 복원
        interior.windows = data.get("windows", getattr(interior, 'windows', []))
        return interior
