"""
world.py - 절차적 월드 생성, 청크 관리, 타일맵
"""
import random
import math
from settings import TILE_SIZE, CHUNK_SIZE, BIOMES, Colors
from utils import SimplexNoise, seeded_random, hash_position


# ============================================================
# 타일 타입
# ============================================================
class TileType:
    GRASS = "grass"
    DIRT = "dirt"
    ROAD = "road"
    CONCRETE = "concrete"
    WATER = "water"
    SAND = "sand"
    FLOOR_WOOD = "floor_wood"
    FLOOR_TILE = "floor_tile"


# ============================================================
# 월드 오브젝트 (나무, 바위, 상자 등)
# ============================================================
class WorldObject:
    def __init__(self, obj_type, x, y, variant=0, data=None):
        self.obj_type = obj_type  # "tree_oak", "tree_pine", "tree_dead", "rock", "bush", "car", "crate", "barrel"
        self.x = x
        self.y = y
        self.variant = variant
        self.data = data or {}
        self.interactable = obj_type in ("crate", "barrel", "car")
        self.looted = False
        self.destructible = obj_type in ("crate", "barrel")
        self.hp = self.data.get("hp", 30)
        self.solid = obj_type not in ("bush",) and not obj_type.startswith("tree_")

    def to_dict(self):
        return {
            "type": self.obj_type, "x": self.x, "y": self.y,
            "variant": self.variant, "looted": self.looted,
            "hp": self.hp, "data": self.data,
        }

    @classmethod
    def from_dict(cls, d):
        obj = cls(d["type"], d["x"], d["y"], d.get("variant", 0), d.get("data"))
        obj.looted = d.get("looted", False)
        obj.hp = d.get("hp", 30)
        return obj


# ============================================================
# 건물 데이터
# ============================================================
class Building:
    def __init__(self, building_type, x, y, width, height, variant=0):
        self.building_type = building_type
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.variant = variant
        self.explored = False
        self.loot_points = []
        self.door_x = x + width // 2
        self.door_y = y + height - 1
        self.interior_generated = False

    @property
    def center(self):
        return (self.x + self.width / 2, self.y + self.height / 2)

    def contains(self, tx, ty):
        return self.x <= tx < self.x + self.width and self.y <= ty < self.y + self.height

    def is_near_door(self, px, py, radius=1.5):
        dx = abs(px - self.door_x)
        dy = abs(py - self.door_y)
        return dx <= radius and dy <= radius

    def to_dict(self):
        return {
            "type": self.building_type, "x": self.x, "y": self.y,
            "w": self.width, "h": self.height, "variant": self.variant,
            "explored": self.explored,
        }

    @classmethod
    def from_dict(cls, d):
        b = cls(d["type"], d["x"], d["y"], d["w"], d["h"], d.get("variant", 0))
        b.explored = d.get("explored", False)
        return b


# ============================================================
# 청크
# ============================================================
class Chunk:
    def __init__(self, cx, cy):
        self.cx = cx
        self.cy = cy
        self.tiles = [[TileType.GRASS for _ in range(CHUNK_SIZE)] for _ in range(CHUNK_SIZE)]
        self.variants = [[0 for _ in range(CHUNK_SIZE)] for _ in range(CHUNK_SIZE)]
        self.objects = []
        self.buildings = []
        self.items_on_ground = []  # (item_name, x, y)
        self.generated = False
        
        # 캐싱을 위한 플래그 및 서피스 참조
        self.dirty = True
        self.surface = None

    @property
    def world_x(self):
        return self.cx * CHUNK_SIZE

    @property
    def world_y(self):
        return self.cy * CHUNK_SIZE

    def get_tile(self, local_x, local_y):
        if 0 <= local_x < CHUNK_SIZE and 0 <= local_y < CHUNK_SIZE:
            return self.tiles[local_y][local_x]
        return TileType.GRASS

    def set_tile(self, local_x, local_y, tile_type, variant=0):
        if 0 <= local_x < CHUNK_SIZE and 0 <= local_y < CHUNK_SIZE:
            self.tiles[local_y][local_x] = tile_type
            self.variants[local_y][local_x] = variant
            self.dirty = True

    def to_dict(self):
        return {
            "cx": self.cx, "cy": self.cy,
            "tiles": self.tiles, "variants": self.variants,
            "objects": [o.to_dict() for o in self.objects],
            "buildings": [b.to_dict() for b in self.buildings],
            "items": self.items_on_ground,
            "generated": self.generated,
        }


# ============================================================
# 월드 생성기
# ============================================================
class WorldGenerator:
    """절차적 월드 생성"""

    def __init__(self, seed=None, world_settings=None):
        self.seed = seed or random.randint(0, 2**31)
        self.settings = world_settings or {}
        self.noise = SimplexNoise(self.seed)
        self.biome_noise = SimplexNoise(self.seed + 1)
        self.detail_noise = SimplexNoise(self.seed + 2)
        self.rng = random.Random(self.seed)

        self.resource_density = self.settings.get("resource_density", 1.0)
        self.building_density = self.settings.get("building_density", 1.0)

        # 바이옴 목록 (키 리스트)
        self.biome_keys = list(BIOMES.keys())

    def get_biome(self, wx, wy):
        """월드 좌표에서 바이옴 결정"""
        scale = 0.008
        n = self.biome_noise.octave_noise(wx * scale, wy * scale, octaves=3, persistence=0.5)
        m = self.detail_noise.octave_noise(wx * scale * 1.5, wy * scale * 1.5, octaves=2)

        # 중심부는 도시 (0,0 근처)
        dist = math.sqrt(wx * wx + wy * wy)

        if dist < 15:
            return "주거지"  # 시작 지점 (은신처 근처)
        elif dist < 40:
            if n > 0.3:
                return "도시"
            elif n < -0.3:
                return "공장단지"
            else:
                return "주거지"
        elif dist < 60:
            if n > 0.4:
                return "병원구역"
            elif n > 0:
                return "도시"
            elif n < -0.4:
                return "밀밭"
            else:
                return "공장단지"
        elif dist < 100:
            if n > 0.4:
                return "군사기지"
            elif n > 0.1:
                return "산림"
            elif n < -0.3:
                return "호수"
            else:
                return "황무지"
        else:
            if m > 0.3:
                return "군사기지"
            elif n > 0:
                return "산림"
            elif n < -0.3:
                return "호수"
            else:
                return "황무지"

    def _is_road(self, wx, wy, biome_name):
        """해당 좌표가 도로인지 판정"""
        biome = BIOMES.get(biome_name, {})
        interval = biome.get("road_interval", 0)
        if interval <= 0:
            return False
        return wx % interval < 2 or wy % interval < 2

    def _is_sidewalk(self, wx, wy, biome_name):
        """도로 옆 인도 (도로 바로 옆 1타일)"""
        biome = BIOMES.get(biome_name, {})
        interval = biome.get("road_interval", 0)
        if interval <= 0:
            return False
        rx = wx % interval
        ry = wy % interval
        return rx == 2 or ry == 2 or rx == interval - 1 or ry == interval - 1

    def generate_chunk(self, cx, cy):
        """청크 생성"""
        chunk = Chunk(cx, cy)

        for ly in range(CHUNK_SIZE):
            for lx in range(CHUNK_SIZE):
                wx = cx * CHUNK_SIZE + lx
                wy = cy * CHUNK_SIZE + ly
                biome_name = self.get_biome(wx, wy)
                biome = BIOMES.get(biome_name, BIOMES["산림"])

                # 타일 결정
                base_tile = biome["base_tile"]
                variant = hash_position(wx, wy, self.seed) % 4

                # 도로 생성 (바이옴별 간격)
                if self._is_road(wx, wy, biome_name):
                    base_tile = TileType.ROAD
                    interval = biome.get("road_interval", 12)
                    if (wx % interval == 0 and wy % 4 == 0) or (wy % interval == 0 and wx % 4 == 0):
                        variant = 1  # 도로 마킹
                elif self._is_sidewalk(wx, wy, biome_name):
                    if biome_name in ("도시", "병원구역", "군사기지"):
                        base_tile = TileType.CONCRETE

                # 물가 주변 모래
                if base_tile == TileType.WATER:
                    neighbors_water = 0
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nb = self.get_biome(wx + dx, wy + dy)
                        if nb == "호수":
                            neighbors_water += 1
                    if neighbors_water < 4:
                        base_tile = TileType.SAND

                chunk.set_tile(lx, ly, base_tile, variant)

                # 환경 오브젝트 생성
                obj_roll = seeded_random(wx, wy, self.seed + 10)

                if base_tile not in (TileType.WATER, TileType.ROAD, TileType.SAND, TileType.CONCRETE):
                    # 나무
                    if obj_roll < biome.get("tree_chance", 0) * self.resource_density:
                        tree_type = "oak"
                        if biome_name == "산림":
                            tree_type = ["oak", "pine", "oak"][variant % 3]
                        elif biome_name in ("황무지",):
                            tree_type = "dead"
                        chunk.objects.append(WorldObject(
                            f"tree_{tree_type}", wx, wy, variant
                        ))
                    # 바위
                    elif obj_roll < biome.get("tree_chance", 0) + 0.03:
                        chunk.objects.append(WorldObject("rock", wx, wy, variant))
                    # 관목
                    elif obj_roll < biome.get("tree_chance", 0) + 0.06:
                        chunk.objects.append(WorldObject("bush", wx, wy, variant))

        # 건물 생성
        self._generate_buildings(chunk, cx, cy)

        # 은신처 (시작 지점)
        if cx == 0 and cy == 0:
            self._place_shelter(chunk)

        # 특수 건물
        dist_from_center = math.sqrt(cx * cx + cy * cy)
        if dist_from_center >= 3 and hash_position(cx * 7, cy * 13, self.seed + 50) % 20 == 0:
            self._place_radio_tower(chunk)

        chunk.generated = True
        return chunk

    def _can_place_building(self, chunk, bx, by, bw, bh):
        """건물 배치 가능 여부 (겹침, 물, 도로 검사)"""
        wx_base = chunk.world_x
        wy_base = chunk.world_y

        for dy in range(bh):
            for dx in range(bw):
                tx = bx - wx_base + dx
                ty = by - wy_base + dy
                if tx < 0 or tx >= CHUNK_SIZE or ty < 0 or ty >= CHUNK_SIZE:
                    return False  # 청크 밖
                tile = chunk.get_tile(tx, ty)
                if tile in (TileType.WATER, TileType.ROAD, TileType.SAND):
                    return False  # 물/도로/모래 위 금지

        # 기존 건물과 겹침 검사 (1타일 여유)
        for existing in chunk.buildings:
            if (bx - 1 < existing.x + existing.width and
                bx + bw + 1 > existing.x and
                by - 1 < existing.y + existing.height and
                by + bh + 1 > existing.y):
                return False

        return True

    def _generate_buildings(self, chunk, cx, cy):
        """청크 내 건물 생성 (도로변 배치, 겹침 방지)"""
        wx_base = cx * CHUNK_SIZE
        wy_base = cy * CHUNK_SIZE

        rng = random.Random(hash_position(cx, cy, self.seed + 100))
        biome_name = self.get_biome(wx_base + CHUNK_SIZE // 2, wy_base + CHUNK_SIZE // 2)
        biome = BIOMES.get(biome_name, {})
        
        # 중앙 집중형 밀도 계산 (0,0 에 가까울 수록 빌딩 출현 확률 증가, 멀수록 감소)
        dist_factor = max(0.2, 1.5 - (math.hypot(cx, cy) / 40.0))
        building_chance = biome.get("building_chance", 0) * self.building_density * dist_factor
        road_interval = biome.get("road_interval", 0)

        if rng.random() > building_chance:
            return

        num_buildings = rng.randint(1, 3) if building_chance > 0.3 else 1
        attempts = 0
        placed = 0

        for _ in range(num_buildings):
            # 공장이나 학교는 더 크게 지정
            is_large = rng.random() < 0.2 and biome_name in ("공장단지", "도시", "병원구역")
            bw = rng.randint(5, 7) if is_large else rng.randint(3, 5)
            bh = rng.randint(5, 7) if is_large else rng.randint(3, 5)

            # 도로가 있는 바이옴이면 도로변에 배치 시도
            for attempt in range(8):
                attempts += 1
                if road_interval > 0:
                    # 도로 옆에 배치 (도로 2타일 + 인도 1타일 뒤)
                    side = rng.choice(["h", "v"])  # 수평/수직 도로
                    if side == "h":
                        bx = wx_base + rng.randint(3, max(3, CHUNK_SIZE - bw - 1))
                        road_y = wy_base + (rng.randint(0, max(1, CHUNK_SIZE // road_interval)) * road_interval)
                        by = road_y + 3  # 도로(2) + 인도(1) 뒤
                        if rng.random() < 0.5:
                            by = road_y - bh - 1  # 도로 위쪽
                    else:
                        road_x = wx_base + (rng.randint(0, max(1, CHUNK_SIZE // road_interval)) * road_interval)
                        bx = road_x + 3
                        if rng.random() < 0.5:
                            bx = road_x - bw - 1
                        by = wy_base + rng.randint(3, max(3, CHUNK_SIZE - bh - 1))
                else:
                    # 도로 없는 바이옴: 랜덤 배치
                    bx = wx_base + rng.randint(1, max(1, CHUNK_SIZE - bw - 1))
                    by = wy_base + rng.randint(1, max(1, CHUNK_SIZE - bh - 1))

                if self._can_place_building(chunk, bx, by, bw, bh):
                    break
            else:
                continue  # 배치 실패

            # 건물 타입 결정
            if biome_name == "병원구역":
                btype = rng.choice(["hospital", "hospital", "store"])
            elif biome_name == "공장단지":
                btype = rng.choice(["factory", "factory", "warehouse"])
            elif biome_name == "군사기지":
                btype = rng.choice(["military", "military", "police"])
            elif biome_name == "도시":
                btype = rng.choice(["store", "store", "school", "police", "hospital"])
            elif biome_name == "주거지":
                btype = rng.choice(["house", "house", "house", "store", "school"])
            elif biome_name == "밀밭":
                btype = rng.choice(["house", "barn"])
            else:
                btype = "house"

            building = Building(btype, bx, by, bw, bh, rng.randint(0, 100))

            # 건물 바닥 타일
            for bly in range(bh):
                for blx in range(bw):
                    local_x = bx - wx_base + blx
                    local_y = by - wy_base + bly
                    if 0 <= local_x < CHUNK_SIZE and 0 <= local_y < CHUNK_SIZE:
                        chunk.set_tile(local_x, local_y, TileType.CONCRETE, 0)

            # 건물 영역의 오브젝트 제거
            chunk.objects = [
                obj for obj in chunk.objects
                if not building.contains(obj.x, obj.y)
            ]

            chunk.buildings.append(building)
            placed += 1

    def _place_shelter(self, chunk):
        """시작 은신처 배치 (0,0 청크)"""
        sx, sy = CHUNK_SIZE // 2, CHUNK_SIZE // 2
        wx = chunk.world_x + sx
        wy = chunk.world_y + sy

        shelter = Building("shelter", wx - 3, wy - 3, 6, 6, 0)
        shelter.door_x = wx
        shelter.door_y = wy + 3 - 1  # 남쪽 중앙

        # 은신처 영역 정리 + 주변 안전 구역
        for ly in range(-4, 5):
            for lx in range(-4, 5):
                tx = sx + lx
                ty = sy + ly
                if 0 <= tx < CHUNK_SIZE and 0 <= ty < CHUNK_SIZE:
                    if -3 <= lx < 3 and -3 <= ly < 3:
                        chunk.set_tile(tx, ty, TileType.FLOOR_WOOD, 0)
                    elif chunk.get_tile(tx, ty) not in (TileType.ROAD,):
                        chunk.set_tile(tx, ty, TileType.DIRT, 0)

        # 은신처 주변 오브젝트 삭제
        clear_range = 5
        chunk.objects = [
            obj for obj in chunk.objects
            if abs(obj.x - wx) > clear_range or abs(obj.y - wy) > clear_range
        ]
        
        # 겹치는 기존 생성물 삭제
        chunk.buildings = [
            b for b in chunk.buildings
            if not (shelter.x - 1 < b.x + b.width and shelter.x + shelter.width + 1 > b.x and
                    shelter.y - 1 < b.y + b.height and shelter.y + shelter.height + 1 > b.y)
        ]
        chunk.buildings.append(shelter)

    def _place_radio_tower(self, chunk):
        """통신 중계소 배치"""
        rng = random.Random(hash_position(chunk.cx * 3, chunk.cy * 7, self.seed + 200))
        rx = chunk.world_x + rng.randint(3, CHUNK_SIZE - 4)
        ry = chunk.world_y + rng.randint(3, CHUNK_SIZE - 4)
        tower = Building("military", rx, ry, 3, 3, 999)

        # 겹치는 기존 생성물 및 오브젝트 삭제
        chunk.buildings = [
            b for b in chunk.buildings
            if not (tower.x - 1 < b.x + b.width and tower.x + tower.width + 1 > b.x and
                    tower.y - 1 < b.y + b.height and tower.y + tower.height + 1 > b.y)
        ]
        chunk.objects = [
            obj for obj in chunk.objects
            if not tower.contains(obj.x, obj.y)
        ]
        chunk.buildings.append(tower)


# ============================================================
# 월드 (청크 관리)
# ============================================================
class World:
    """게임 월드 (청크 기반)"""

    def __init__(self, seed=None, world_settings=None):
        self.world_settings = world_settings or {}
        self.generator = WorldGenerator(seed, world_settings)
        self.chunks = {}  # (cx, cy) -> Chunk
        self.unloaded_deltas = {}  # (cx, cy) -> delta dict (변경 데이터만 보존)
        self.seed = self.generator.seed

    def get_chunk(self, cx, cy):
        """청크 가져오기 (없으면 생성, 델타가 있으면 적용)"""
        key = (cx, cy)
        if key not in self.chunks:
            chunk = self.generator.generate_chunk(cx, cy)
            if key in self.unloaded_deltas:
                self._apply_delta(chunk, self.unloaded_deltas.pop(key))
            self.chunks[key] = chunk
        return self.chunks[key]

    def get_tile(self, wx, wy):
        """월드 좌표에서 타일 가져오기"""
        cx = wx // CHUNK_SIZE
        cy = wy // CHUNK_SIZE
        lx = wx % CHUNK_SIZE
        ly = wy % CHUNK_SIZE
        chunk = self.get_chunk(cx, cy)
        return chunk.get_tile(lx, ly)

    def get_biome(self, wx, wy):
        return self.generator.get_biome(wx, wy)

    def get_nearby_objects(self, wx, wy, radius=2):
        """주변 오브젝트 가져오기"""
        objects = []
        cx_min = int((wx - radius)) // CHUNK_SIZE
        cx_max = int((wx + radius)) // CHUNK_SIZE
        cy_min = int((wy - radius)) // CHUNK_SIZE
        cy_max = int((wy + radius)) // CHUNK_SIZE

        for cx in range(cx_min, cx_max + 1):
            for cy in range(cy_min, cy_max + 1):
                chunk = self.get_chunk(cx, cy)
                for obj in chunk.objects:
                    dx = obj.x - wx
                    dy = obj.y - wy
                    if dx * dx + dy * dy <= radius * radius:
                        objects.append(obj)
        return objects

    def get_nearby_buildings(self, wx, wy, radius=5):
        """주변 건물 가져오기"""
        buildings = []
        cx_min = int((wx - radius)) // CHUNK_SIZE
        cx_max = int((wx + radius)) // CHUNK_SIZE
        cy_min = int((wy - radius)) // CHUNK_SIZE
        cy_max = int((wy + radius)) // CHUNK_SIZE

        for cx in range(cx_min, cx_max + 1):
            for cy in range(cy_min, cy_max + 1):
                chunk = self.get_chunk(cx, cy)
                for b in chunk.buildings:
                    bx, by = b.center
                    if abs(bx - wx) <= radius and abs(by - wy) <= radius:
                        buildings.append(b)
        return buildings

    def get_ground_items_near(self, wx, wy, radius=2):
        """주변 바닥 아이템"""
        items = []
        cx_min = int((wx - radius)) // CHUNK_SIZE
        cx_max = int((wx + radius)) // CHUNK_SIZE
        cy_min = int((wy - radius)) // CHUNK_SIZE
        cy_max = int((wy + radius)) // CHUNK_SIZE

        for cx in range(cx_min, cx_max + 1):
            for cy in range(cy_min, cy_max + 1):
                chunk = self.get_chunk(cx, cy)
                for item in chunk.items_on_ground:
                    ix, iy = item[1], item[2]
                    if abs(ix - wx) <= radius and abs(iy - wy) <= radius:
                        items.append((item, chunk))
        return items

    def drop_item(self, item_name, wx, wy):
        """아이템을 바닥에 떨어뜨림"""
        cx = int(wx) // CHUNK_SIZE
        cy = int(wy) // CHUNK_SIZE
        chunk = self.get_chunk(cx, cy)
        chunk.items_on_ground.append((item_name, wx, wy))

    def is_walkable(self, wx, wy):
        """해당 위치가 이동 가능한지"""
        tile = self.get_tile(int(wx), int(wy))
        if tile == TileType.WATER:
            return False

        iwx = int(wx)
        iwy = int(wy)

        # 건물 벽 체크 - 문 앞은 통과 허용
        buildings = self.get_nearby_buildings(iwx, iwy, 8)
        for b in buildings:
            if b.contains(iwx, iwy):
                # 문 타일과 문 바로 앞 1타일은 통과 허용
                if abs(iwx - b.door_x) <= 1 and (iwy == b.door_y or iwy == b.door_y + 1):
                    continue
                return False

        # 오브젝트 체크 (나무, 바위 등 solid) - 판정 완화
        near_objects = self.get_nearby_objects(iwx, iwy, 1)
        for obj in near_objects:
            # 나무나 수풀은 이동 편의를 위해 통과 허용
            if obj.obj_type.startswith("tree_") or obj.obj_type == "bush":
                continue
                
            if obj.solid and abs(obj.x - wx) < 0.5 and abs(obj.y - wy) < 0.5:
                return False

        return True

    def get_loaded_chunk_count(self):
        return len(self.chunks)

    def _extract_delta(self, chunk):
        """청크에서 변경된 데이터만 추출"""
        delta = {}
        changed_objects = []
        for obj in chunk.objects:
            if obj.looted or obj.hp < 30:
                changed_objects.append({
                    "x": obj.x, "y": obj.y, "type": obj.obj_type,
                    "looted": obj.looted, "hp": obj.hp
                })
        if changed_objects:
            delta["objects"] = changed_objects

        explored_buildings = []
        for b in chunk.buildings:
            if b.explored:
                explored_buildings.append({
                    "x": b.x, "y": b.y, "type": b.building_type,
                    "explored": b.explored
                })
        if explored_buildings:
            delta["buildings"] = explored_buildings

        if chunk.items_on_ground:
            delta["items"] = list(chunk.items_on_ground)

        return delta if delta else None

    def _apply_delta(self, chunk, delta):
        """절차적 생성된 청크에 델타를 적용하여 상태 복원"""
        for obj_delta in delta.get("objects", []):
            for obj in chunk.objects:
                if obj.x == obj_delta["x"] and obj.y == obj_delta["y"]:
                    obj.looted = obj_delta.get("looted", False)
                    obj.hp = obj_delta.get("hp", 30)
                    break

        for b_delta in delta.get("buildings", []):
            for b in chunk.buildings:
                if b.x == b_delta["x"] and b.y == b_delta["y"]:
                    b.explored = b_delta.get("explored", False)
                    break

        chunk.items_on_ground = delta.get("items", [])

    def unload_far_chunks(self, center_cx, center_cy, max_distance=6):
        """먼 청크 언로드 (델타만 보존하여 메모리 절약)"""
        to_remove = []
        for key in self.chunks:
            cx, cy = key
            if abs(cx - center_cx) > max_distance or abs(cy - center_cy) > max_distance:
                to_remove.append(key)
        for key in to_remove:
            chunk = self.chunks.pop(key)
            delta = self._extract_delta(chunk)
            if delta:
                self.unloaded_deltas[key] = delta
