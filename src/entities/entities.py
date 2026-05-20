"""
entities.py - 좀비, NPC, 동물 엔티티 시스템
"""
import math
import random
from settings import TILE_SIZE, CHUNK_SIZE, DIFFICULTY_PRESETS
from utils import distance, direction_to, clamp


# ============================================================
# 좀비 타입 정의 (확장 가능)
# ============================================================
ZOMBIE_TYPES = {
    "normal": {
        "name": "일반 좀비",
        "hp": 30,
        "damage": 8,
        "speed": 1.2,
        "detection_range": 6,
        "attack_range": 1.0,
        "attack_cooldown": 1.0,
        "xp": 10,
        "loot_chance": 0.3,
    },
    "runner": {
        "name": "러너 좀비",
        "hp": 20,
        "damage": 6,
        "speed": 2.5,
        "detection_range": 8,
        "attack_range": 0.8,
        "attack_cooldown": 0.6,
        "xp": 15,
        "loot_chance": 0.2,
    },
    "tank": {
        "name": "탱크 좀비",
        "hp": 100,
        "damage": 20,
        "speed": 0.7,
        "detection_range": 5,
        "attack_range": 1.3,
        "attack_cooldown": 1.5,
        "xp": 30,
        "loot_chance": 0.5,
    },
    "spider": {
        "name": "스파이더 좀비",
        "hp": 25,
        "damage": 10,
        "speed": 2.0,
        "detection_range": 7,
        "attack_range": 0.9,
        "attack_cooldown": 0.8,
        "xp": 20,
        "loot_chance": 0.25,
    },
}

# 좀비가 드롭하는 아이템 풀
ZOMBIE_LOOT = [
    ("천", 0.3), ("고철", 0.2), ("못", 0.15),
    ("식량통조림", 0.05), ("붕대", 0.1), ("탄약", 0.05),
]


class ZombieState:
    IDLE = "idle"
    WANDER = "wander"
    CHASE = "chase"
    ATTACK = "attack"
    HURT = "hurt"
    DEAD = "dead"


class Zombie:
    """좀비 엔티티"""

    def __init__(self, x, y, zombie_type="normal", difficulty_settings=None):
        self.x = float(x)
        self.y = float(y)
        self.zombie_type = zombie_type
        self.diff = difficulty_settings or DIFFICULTY_PRESETS["보통"]

        type_data = ZOMBIE_TYPES.get(zombie_type, ZOMBIE_TYPES["normal"])

        self.max_hp = type_data["hp"] * self.diff.get("zombie_hp_mult", 1.0)
        self.hp = self.max_hp
        self.damage = type_data["damage"] * self.diff.get("zombie_damage_mult", 1.0)
        self.speed = type_data["speed"] * self.diff.get("zombie_speed_mult", 1.0)
        self.detection_range = type_data["detection_range"]
        self.attack_range = type_data["attack_range"]
        self.attack_cooldown_time = type_data["attack_cooldown"]
        self.loot_chance = type_data["loot_chance"]
        self.xp = type_data["xp"]

        self.state = ZombieState.IDLE
        self.direction = 0
        self.animation_frame = 0
        self.animation_timer = 0

        self.attack_timer = 0
        self.idle_timer = random.uniform(0, 3)
        self.wander_target_x = x
        self.wander_target_y = y
        self.hurt_timer = 0
        self.death_timer = 0
        self.aggro_alert = 0.0  # 총성 어그로 느낌표 표시 잔여 시간

        self.active = True

    def update(self, dt, player_x, player_y, world, player_crouching=False):
        if not self.active:
            return

        if self.aggro_alert > 0:
            self.aggro_alert -= dt

        # 사망 처리
        if self.hp <= 0:
            if self.state != ZombieState.DEAD:
                self.state = ZombieState.DEAD
                self.death_timer = 1.5
            self.death_timer -= dt
            if self.death_timer <= 0:
                self.active = False
            return

        # 피격 상태
        if self.state == ZombieState.HURT:
            self.hurt_timer -= dt
            if self.hurt_timer <= 0:
                self.state = ZombieState.CHASE
            return

        # 플레이어와의 거리
        dist = distance(self.x, self.y, player_x, player_y)

        # 은신 시 감지 범위 50% 감소
        effective_detection = self.detection_range * 0.5 if player_crouching else self.detection_range

        # 상태 전이
        if dist <= self.attack_range:
            self.state = ZombieState.ATTACK
        elif dist <= effective_detection:
            self.state = ZombieState.CHASE
        elif self.state == ZombieState.CHASE and dist > effective_detection * 1.5:
            self.state = ZombieState.WANDER

        # 상태별 행동
        if self.state == ZombieState.IDLE:
            self.idle_timer -= dt
            if self.idle_timer <= 0:
                self.state = ZombieState.WANDER
                self.wander_target_x = self.x + random.uniform(-5, 5)
                self.wander_target_y = self.y + random.uniform(-5, 5)
                self.idle_timer = random.uniform(2, 5)

        elif self.state == ZombieState.WANDER:
            dx, dy = direction_to(self.x, self.y, self.wander_target_x, self.wander_target_y)
            move_speed = self.speed * 0.4 * dt
            new_x = self.x + dx * move_speed
            new_y = self.y + dy * move_speed

            if world.is_walkable(new_x, self.y):
                self.x = new_x
            if world.is_walkable(self.x, new_y):
                self.y = new_y

            if distance(self.x, self.y, self.wander_target_x, self.wander_target_y) < 0.5:
                self.state = ZombieState.IDLE
                self.idle_timer = random.uniform(1, 4)

        elif self.state == ZombieState.CHASE:
            dx, dy = direction_to(self.x, self.y, player_x, player_y)
            move_speed = self.speed * dt
            new_x = self.x + dx * move_speed
            new_y = self.y + dy * move_speed

            if world.is_walkable(new_x, self.y):
                self.x = new_x
            if world.is_walkable(self.x, new_y):
                self.y = new_y

        elif self.state == ZombieState.ATTACK:
            self.attack_timer -= dt

        # 방향 업데이트
        if self.state in (ZombieState.CHASE, ZombieState.ATTACK):
            dx = player_x - self.x
            dy = player_y - self.y
        elif self.state == ZombieState.WANDER:
            dx = self.wander_target_x - self.x
            dy = self.wander_target_y - self.y
        else:
            dx, dy = 0, 1

        if abs(dx) > 0.01 or abs(dy) > 0.01:
            angle = math.atan2(dy, dx)
            self.direction = int(((angle + math.pi) / (math.pi / 4) + 0.5)) % 8
            self.direction = (self.direction + 4) % 8

        # 애니메이션
        if self.state in (ZombieState.CHASE, ZombieState.WANDER):
            self.animation_timer += dt
            if self.animation_timer >= 0.15:
                self.animation_timer -= 0.15
                self.animation_frame = (self.animation_frame + 1) % 8

    def can_attack(self):
        return self.state == ZombieState.ATTACK and self.attack_timer <= 0

    def do_attack(self):
        self.attack_timer = self.attack_cooldown_time
        return self.damage

    def take_damage(self, amount, knockback_dir=None):
        self.hp -= amount
        self.state = ZombieState.HURT
        self.hurt_timer = 0.3

        if knockback_dir:
            self.x += knockback_dir[0] * 0.5
            self.y += knockback_dir[1] * 0.5

    def get_loot(self):
        """사망 시 루트"""
        loot = []
        if random.random() < self.loot_chance:
            for item_name, chance in ZOMBIE_LOOT:
                if random.random() < chance:
                    loot.append(item_name)
                    if len(loot) >= 2:
                        break
        return loot

    @property
    def is_dead(self):
        return self.hp <= 0

    def to_dict(self):
        return {
            "x": self.x, "y": self.y, "type": self.zombie_type,
            "hp": self.hp, "state": self.state, "active": self.active,
        }

    @classmethod
    def from_dict(cls, data):
        z = cls(data["x"], data["y"], data.get("type", "normal"))
        z.hp = data.get("hp", z.max_hp)
        z.state = data.get("state", "idle")
        z.active = data.get("active", True)
        return z


# ============================================================
# NPC 타입 정의
# ============================================================
NPC_TYPES = {
    "merchant": {
        "name": "떠돌이 상인",
        "dialogue_intro": "여어, 반가워! 좋은 물건 많이 있어.",
        "trade_items": [
            ("방독면", "식량통조림", 2),
            ("방탄조끼", "식량통조림", 3),
            ("비상용 배터리", "식량통조림", 1),
            ("구급상자", "생수", 2),
            ("탄약", "고철", 3),
        ],
    },
    "survivor": {
        "name": "생존자",
        "dialogue_intro": "살아있는 사람이라니... 도와줄 수 있나요?",
        "quest_types": ["rescue", "fetch", "defend"],
    },
    "soldier": {
        "name": "군인",
        "dialogue_intro": "생존자인가? 이 지역 정보를 공유할 수 있소.",
        "provides": ["map_info", "military_loot"],
    },
}


class NPCState:
    IDLE = "idle"
    TALKING = "talking"
    TRADING = "trading"
    MOVING = "moving"


class NPC:
    """NPC 엔티티"""

    def __init__(self, x, y, npc_type="merchant"):
        self.x = float(x)
        self.y = float(y)
        self.npc_type = npc_type
        self.state = NPCState.IDLE
        self.direction = 0
        self.animation_frame = 0
        self.animation_timer = 0
        self.active = True
        self.met = False

        type_data = NPC_TYPES.get(npc_type, {})
        self.name = type_data.get("name", "NPC")
        self.dialogue_intro = type_data.get("dialogue_intro", "...")

        # 상인 전용
        self.trade_items = type_data.get("trade_items", [])

        # 퀘스트 주는 NPC 전용 (survivor, soldier 등)
        if npc_type == "soldier":
            self.quest_req = ("식량통조림", random.randint(1, 3))
            self.quest_reward = ("권총", 1) if random.random() < 0.5 else ("탄약", random.randint(5, 15))
        elif npc_type == "survivor":
            self.quest_req = ("붕대", random.randint(1, 2)) if random.random() < 0.5 else ("생수", random.randint(1, 3))
            self.quest_reward = ("가방", 1) if random.random() < 0.2 else ("고철", random.randint(3, 8))
        else:
            self.quest_req = (None, 0)
            self.quest_reward = (None, 0)

        self.idle_timer = random.uniform(0, 3)
        self.wander_target_x = x
        self.wander_target_y = y

    def update(self, dt, world):
        if not self.active:
            return

        if self.state == NPCState.IDLE:
            self.idle_timer -= dt
            if self.idle_timer <= 0:
                self.state = NPCState.MOVING
                self.wander_target_x = self.x + random.uniform(-3, 3)
                self.wander_target_y = self.y + random.uniform(-3, 3)
                self.idle_timer = random.uniform(3, 8)

        elif self.state == NPCState.MOVING:
            dx, dy = direction_to(self.x, self.y, self.wander_target_x, self.wander_target_y)
            speed = 0.8 * dt
            new_x = self.x + dx * speed
            new_y = self.y + dy * speed

            if world.is_walkable(new_x, self.y):
                self.x = new_x
            if world.is_walkable(self.x, new_y):
                self.y = new_y

            if distance(self.x, self.y, self.wander_target_x, self.wander_target_y) < 0.3:
                self.state = NPCState.IDLE
                self.idle_timer = random.uniform(2, 6)

            # 애니메이션
            self.animation_timer += dt
            if self.animation_timer >= 0.2:
                self.animation_timer -= 0.2
                self.animation_frame = (self.animation_frame + 1) % 8

    def is_near(self, px, py, radius=2.0):
        return distance(self.x, self.y, px, py) <= radius

    def to_dict(self):
        return {
            "x": self.x, "y": self.y, "type": self.npc_type,
            "active": self.active,
            "met": getattr(self, "met", False),
            "quest_req": list(self.quest_req) if hasattr(self, "quest_req") else [None, 0],
            "quest_reward": list(self.quest_reward) if hasattr(self, "quest_reward") else [None, 0],
        }

    @classmethod
    def from_dict(cls, data):
        n = cls(data["x"], data["y"], data.get("type", "survivor"))
        n.active = data.get("active", True)
        n.met = data.get("met", False)
        if "quest_req" in data:
            n.quest_req = tuple(data["quest_req"])
        if "quest_reward" in data:
            n.quest_reward = tuple(data["quest_reward"])
        return n


# ============================================================
# 엔티티 관리자
# ============================================================
class EntityManager:
    """모든 엔티티 관리"""

    def __init__(self, difficulty_settings=None):
        self.zombies = []
        self.npcs = []
        self.diff = difficulty_settings or DIFFICULTY_PRESETS["보통"]
        self.spawn_timer = 0
        self.spawn_interval = 5.0 / max(0.1, self.diff.get("zombie_spawn_rate", 1.0))
        self.max_zombies = self.diff.get("max_zombies", 20)
        self.npc_spawn_timer = 0
        self.despawn_distance = 120  # 플레이어로부터 120타일 초과 시 디스폰

    def update(self, dt, player, world):
        # 거리 기반 엔티티 동면/디스폰
        self._cull_distant_entities(player.x, player.y)

        # 좀비 업데이트 (활성 상태만)
        for zombie in self.zombies:
            if zombie.active:
                zombie.update(dt, player.x, player.y, world, player.is_crouching)

        # 비활성 좀비 제거
        self.zombies = [z for z in self.zombies if z.active]

        # NPC 업데이트 (활성 상태만)
        for npc in self.npcs:
            if npc.active:
                npc.update(dt, world)

        # 좀비 스폰
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval and len(self.zombies) < self.max_zombies:
            self.spawn_timer = 0
            self._spawn_zombies(player, world)

        # NPC 랜덤 스폰
        self.npc_spawn_timer += dt
        if self.npc_spawn_timer >= 60 and len(self.npcs) < 3:
            self.npc_spawn_timer = 0
            if random.random() < 0.3:
                self._spawn_npc(player, world)

    def _cull_distant_entities(self, px, py):
        """플레이어에서 먼 엔티티 비활성화 (청크 무한 재생성 방지)"""
        for zombie in self.zombies:
            if zombie.active and not zombie.is_dead:
                d = distance(zombie.x, zombie.y, px, py)
                if d > self.despawn_distance:
                    zombie.active = False

        for npc in self.npcs:
            if npc.active:
                d = distance(npc.x, npc.y, px, py)
                if d > self.despawn_distance:
                    npc.active = False

    def _spawn_zombies(self, player, world):
        """플레이어 주변에 좀비 스폰"""
        player_biome = world.get_biome(int(player.x), int(player.y))
        
        if player_biome in ("도시", "병원구역"):
            spawn_count = random.randint(3, 7)
        elif player_biome == "군사기지":
            spawn_count = random.randint(4, 8)
        elif player_biome in ("산림", "황무지", "호수"):
            spawn_count = random.randint(0, 1)
        else:
            spawn_count = random.randint(1, 3)

        for _ in range(spawn_count):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(8, 15)
            sx = player.x + math.cos(angle) * dist
            sy = player.y + math.sin(angle) * dist

            if not world.is_walkable(sx, sy):
                continue

            # 바이옴에 따른 좀비 타입
            biome = world.get_biome(int(sx), int(sy))
            if biome in ("군사기지",):
                ztype = random.choice(["normal", "runner", "tank"])
            elif biome in ("병원구역",):
                ztype = random.choice(["normal", "spider", "runner"])
            elif biome in ("산림",):
                ztype = random.choice(["normal", "normal", "runner"])
            elif biome in ("호수", "황무지"):
                ztype = "normal"
            else:
                ztype = random.choice(["normal", "normal", "normal", "runner"])

            zombie = Zombie(sx, sy, ztype, self.diff)
            self.zombies.append(zombie)

    def _spawn_npc(self, player, world):
        """NPC 스폰"""
        angle = random.uniform(0, math.pi * 2)
        dist = random.uniform(5, 10)
        sx = player.x + math.cos(angle) * dist
        sy = player.y + math.sin(angle) * dist

        if world.is_walkable(sx, sy):
            biome = world.get_biome(int(sx), int(sy))
            
            # 바이옴 특화 NPC 스폰 확률 조정
            if biome == "군사기지":
                types = ["soldier"] * 7 + ["merchant", "survivor", "survivor"]
            elif biome in ("도시", "공장단지"):
                types = ["merchant"] * 6 + ["survivor"] * 3 + ["soldier"]
            elif biome == "병원구역":
                types = ["survivor"] * 6 + ["merchant"] * 3 + ["soldier"]
            else:
                types = ["merchant", "survivor", "soldier"]
                
            npc_type = random.choice(types)
            npc = NPC(sx, sy, npc_type)
            self.npcs.append(npc)

    def get_nearby_zombies(self, x, y, radius):
        return [z for z in self.zombies if distance(z.x, z.y, x, y) <= radius and not z.is_dead]

    def get_nearby_npcs(self, x, y, radius):
        return [n for n in self.npcs if n.is_near(x, y, radius) and n.active]

    def remove_dead_zombies(self, world):
        """사망 좀비에서 루트 드롭"""
        drops = []
        for z in self.zombies:
            if z.is_dead and z.active:
                loot = z.get_loot()
                for item in loot:
                    world.drop_item(item, z.x, z.y)
                    drops.append((item, z.x, z.y))
        return drops
