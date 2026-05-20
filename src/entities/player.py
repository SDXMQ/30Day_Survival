"""
player.py - 플레이어 캐릭터 시스템
"""
import pygame
import math
from settings import (PLAYER_MAX_HP, PLAYER_MAX_HUNGER, PLAYER_MAX_THIRST,
                       PLAYER_MAX_STRESS, PLAYER_MAX_STAMINA,
                       PLAYER_SPEED, PLAYER_SPRINT_SPEED, TILE_SIZE,
                       CHUNK_SIZE, DIFFICULTY_PRESETS)
from items import Inventory, ITEM_DATABASE
from crafting import CraftingSystem
from utils import clamp, distance, CooldownManager


class Player:
    """플레이어 캐릭터"""

    def __init__(self, x=0, y=0, difficulty_settings=None):
        # 위치 (월드 타일 좌표)
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0

        # 스탯
        self.hp = PLAYER_MAX_HP
        self.max_hp = PLAYER_MAX_HP
        self.hunger = PLAYER_MAX_HUNGER
        self.thirst = PLAYER_MAX_THIRST
        self.stress = 0
        self.stamina = PLAYER_MAX_STAMINA
        self.defense = 0
        self.shelter_defense = 10

        # 난이도 설정
        self.diff = difficulty_settings or DIFFICULTY_PRESETS["보통"]

        # 이동
        self.speed = PLAYER_SPEED
        self.sprint_speed = PLAYER_SPRINT_SPEED
        self.is_sprinting = False
        self.is_crouching = False
        self.direction = 0  # 0~7 (하, 좌하, 좌, 좌상, 상, 우상, 우, 우하)
        self.moving = False
        self.animation_frame = 0
        self.animation_timer = 0

        # 전투
        self.equipped_weapon = None
        self.attack_cooldown = CooldownManager()
        self.invincible_timer = 0
        self.combo_count = 0

        # 인벤토리 & 크래프팅
        self.inventory = Inventory(slots=24)
        self.crafting = CraftingSystem()

        # 장비 슬롯
        self.equipped = {
            "head": None,
            "body": None,
            "feet": None,
            "weapon": None,
        }

        # 내부/외부 상태 관리 (인테리어)
        self.is_interior = False
        self.exterior_x = 0.0
        self.exterior_y = 0.0

        # 상태
        self.alive = True
        self.cause_of_death = ""
        self.exhausted = False  # 탈진 상태 (스태미나 0 도달 시)
        self.footstep_timer = 0

        # 퀘스트/진행 추적
        self.discovered_biomes = set()
        self.killed_zombies = 0
        self.buildings_explored = 0
        self.items_crafted = 0
        self.days_survived = 0

    def enter_interior(self, ix, iy):
        """건물 내부 진입 시 좌표 전환"""
        self.is_interior = True
        self.exterior_x = self.x
        self.exterior_y = self.y
        self.x = float(ix)
        self.y = float(iy)
        self.moving = False
        self.is_sprinting = False

    def exit_interior(self):
        """건물 외부 퇴장 시 좌표 복구"""
        self.is_interior = False
        self.x = self.exterior_x
        self.y = self.exterior_y
        self.moving = False

    def update(self, dt, current_world, weather_type=None):
        """플레이어 업데이트 (world 혹은 interior를 받아 다형성 적용)"""
        if not self.alive:
            return

        # 이동 처리
        self._handle_movement(dt, current_world)

        # 애니메이션
        self._update_animation(dt)

        # 쿨다운
        self.attack_cooldown.update(dt)

        # 무적 타이머
        if self.invincible_timer > 0:
            self.invincible_timer -= dt

        # 스탯 감소 (시간 경과)
        # 주의: current_world가 BuildingInterior일 경우를 대비해 속성 접근 안전 처리
        world_settings = getattr(current_world, 'world_settings', {})
        self._update_stats(dt, world_settings, weather_type)

        # 크래프팅 진행
        # 크래프팅 시 좌표는 현재 좌표를 넘김
        result = self.crafting.update(dt, self.inventory, current_world, self.x, self.y)
        if result:
            self.items_crafted += 1

        # 상태 확인
        self._check_status()

        # 발자국 타이머
        if self.moving:
            self.footstep_timer += dt

    def _handle_movement(self, dt, world):
        """키 입력 기반 이동"""
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1

        # 스프린트 (탈진 상태면 30% 회복될 때까지 금지)
        wants_sprint = keys[pygame.K_LSHIFT]
        if self.exhausted:
            if self.stamina >= PLAYER_MAX_STAMINA * 0.3:
                self.exhausted = False
            else:
                wants_sprint = False

        # 은신 (앉기) - LCTRL 토글
        self.is_crouching = keys[pygame.K_LCTRL]
        if self.is_crouching:
            wants_sprint = False  # 은신 중에는 스프린트 불가
        self.is_sprinting = wants_sprint and self.stamina > 0

        # 정규화
        if dx != 0 or dy != 0:
            length = math.sqrt(dx * dx + dy * dy)
            dx /= length
            dy /= length
            self.moving = True

            # 방향 계산 (8방향)
            angle = math.atan2(dy, dx)
            self.direction = int(((angle + math.pi) / (math.pi / 4) + 0.5)) % 8
            self.direction = (self.direction + 4) % 8  # 보정
        else:
            self.moving = False

        # 속도 결정
        current_speed = self.sprint_speed if self.is_sprinting else self.speed
        if self.is_crouching:
            current_speed *= 0.5  # 은신 시 50% 감속

        # 장비 보너스 (속도 및 가방 무게)
        if self.equipped.get("feet"):
            data = ITEM_DATABASE.get(self.equipped["feet"], {})
            current_speed += data.get("speed_bonus", 0)
            
        base_max_weight = 30.0
        if self.equipped.get("back"):
            data = ITEM_DATABASE.get(self.equipped["back"], {})
            base_max_weight += data.get("weight_bonus", 0)
        self.inventory.max_weight = base_max_weight
        
        # 무게 초과 확인 (80% 이상 시 속도 점진적 감소)
        current_weight = self.inventory.current_weight
        if current_weight > self.inventory.max_weight * 0.8:
            penalty_ratio = (current_weight - self.inventory.max_weight * 0.8) / (self.inventory.max_weight * 0.2)
            penalty_ratio = min(1.0, penalty_ratio)
            current_speed *= (1.0 - 0.3 * penalty_ratio) # 최대 30% 감속

        # 이동
        new_x = self.x + dx * current_speed * dt
        new_y = self.y + dy * current_speed * dt

        # 충돌 체크
        if world.is_walkable(new_x, self.y):
            self.x = new_x
        if world.is_walkable(self.x, new_y):
            self.y = new_y

        # 스프린트 시 스태미나 소모 (20/초)
        if self.is_sprinting and self.moving:
            self.stamina -= 20 * dt
            if self.stamina <= 0:
                self.stamina = 0
                self.exhausted = True
                self.is_sprinting = False

    def _update_animation(self, dt):
        """애니메이션 프레임 업데이트"""
        if self.moving:
            speed = 0.15 if self.is_sprinting else 0.1
            self.animation_timer += dt
            if self.animation_timer >= speed:
                self.animation_timer -= speed
                self.animation_frame = (self.animation_frame + 1) % 8
        else:
            self.animation_frame = 0
            self.animation_timer = 0

    def _update_stats(self, dt, world_settings, weather_type=None):
        """스탯 자연 감소/회복"""
        day_length = world_settings.get("day_length_minutes", 12) if world_settings else 12
        # 기본 12분 기준. 하루 길이가 길수록 천천히 감소 (0.5배까지)
        time_scale = 12 / max(5, day_length)
        
        hunger_rate = 0.4 * self.diff.get("hunger_rate", 1.0) * time_scale
        thirst_rate = 0.5 * self.diff.get("thirst_rate", 1.0) * time_scale
        stress_rate = 0.1 * self.diff.get("stress_rate", 1.0) * time_scale

        self.hunger -= hunger_rate * dt
        self.thirst -= thirst_rate * dt

        # 배고픔/갈증에 의한 체력 감소
        if self.hunger <= 0:
            self.hunger = 0
            self.hp -= 2 * dt
            self.stress += 3 * dt

        if self.thirst <= 0:
            self.thirst = 0
            self.hp -= 3 * dt
            self.stress += 4 * dt

        # 날씨 페널티 (야외에서 비/폭우/폭풍 노출 시)
        bad_weather = weather_type in ("비", "폭우", "폭풍") if weather_type else False
        is_outside = not self.is_interior

        # 스태미나 자연 회복 (배고픔 연동)
        if not self.is_sprinting:
            recovery_rate = 10  # 기본 10/초
            if self.hunger < PLAYER_MAX_HUNGER * 0.2:
                recovery_rate *= 0.5  # 배고프면 회복 50% 감소
            if bad_weather and is_outside:
                recovery_rate *= 0.5  # 악천후 야외 시 회복 50% 추가 감소
            old_stamina = self.stamina
            self.stamina = min(PLAYER_MAX_STAMINA, self.stamina + recovery_rate * dt)
            recovered = self.stamina - old_stamina
            if recovered > 0:
                # 스태미나 회복 10당 배고픔 0.3 소모
                self.hunger -= recovered * 0.03

        # 악천후 야외 노출 시 스트레스 지속 증가
        if bad_weather and is_outside:
            self.stress += 0.3 * dt

        # 스트레스 자연 감소 (낮, 은신처 근처)
        self.stress = max(0, self.stress - 0.1 * dt)

        # 값 제한
        self.hp = clamp(self.hp, 0, self.max_hp)
        self.hunger = clamp(self.hunger, 0, PLAYER_MAX_HUNGER)
        self.thirst = clamp(self.thirst, 0, PLAYER_MAX_THIRST)
        self.stress = clamp(self.stress, 0, PLAYER_MAX_STRESS)
        self.stamina = clamp(self.stamina, 0, PLAYER_MAX_STAMINA)

    def _check_status(self):
        """생존 상태 확인"""
        if self.hp <= 0:
            self.alive = False
            self.cause_of_death = "체력 고갈"
        elif self.stress >= PLAYER_MAX_STRESS:
            self.alive = False
            self.cause_of_death = "극심한 스트레스"

    def take_damage(self, amount, source=""):
        """피해 받기"""
        if self.invincible_timer > 0:
            return 0

        # 방어력 적용
        defense = self.defense
        if self.equipped.get("body"):
            data = ITEM_DATABASE.get(self.equipped["body"], {})
            defense += data.get("defense", 0)

        actual_damage = max(1, amount * self.diff.get("damage_multiplier", 1.0) - defense * 0.5)
        self.hp -= actual_damage
        self.invincible_timer = 0.5

        # 스트레스 증가
        self.stress += actual_damage * 0.3

        return actual_damage

    def heal(self, amount):
        """체력 회복"""
        self.hp = min(self.max_hp, self.hp + amount)

    def use_item(self, item_name):
        """아이템 사용"""
        if not self.inventory.has_item(item_name):
            return False

        data = ITEM_DATABASE.get(item_name, {})
        effects = data.get("effects", {})

        if not effects:
            return False

        # 효과 적용
        if "hp" in effects:
            self.heal(effects["hp"])
        if "hunger" in effects:
            self.hunger = min(PLAYER_MAX_HUNGER, self.hunger + effects["hunger"])
        if "thirst" in effects:
            self.thirst = min(PLAYER_MAX_THIRST, self.thirst + effects["thirst"])
        if "stress" in effects:
            self.stress = max(0, self.stress + effects["stress"])
        if "stamina" in effects:
            self.stamina = min(PLAYER_MAX_STAMINA, self.stamina + effects["stamina"])

        self.inventory.remove_item(item_name, 1)
        return True

    def equip_item(self, item_name, world=None):
        """장비 착용"""
        data = ITEM_DATABASE.get(item_name)
        if not data:
            return False

        slot = data.get("equip_slot")
        if not slot and data.get("category") == "무기":
            slot = "weapon"

        if not slot:
            return False
            
        if not self.inventory.has_item(item_name):
            return False

        old_item = self.equipped.get(slot)
        
        # 새 아이템을 먼저 인벤토리에서 제거하여 빈 공간(슬롯)을 1칸 확보
        self.inventory.remove_item(item_name, 1)

        # 기존에 장착 중이던 장비를 인벤토리에 추가
        if old_item:
            if not self.inventory.add_item(old_item):
                # 인벤토리가 가득 찼으면 바닥에 드롭 (장비 증발 방지)
                if world and hasattr(world, 'drop_item'):
                    drop_x = self.x
                    drop_y = self.y
                    world.drop_item(old_item, drop_x, drop_y)

        self.equipped[slot] = item_name
        return True

    def get_attack_damage(self):
        """현재 무기의 공격력"""
        weapon = self.equipped.get("weapon")
        if weapon:
            data = ITEM_DATABASE.get(weapon, {})
            return data.get("damage", 5)
        return 5  # 주먹

    def get_attack_range(self):
        """현재 무기의 사거리"""
        weapon = self.equipped.get("weapon")
        if weapon:
            data = ITEM_DATABASE.get(weapon, {})
            return data.get("range", 1.0)
        return 0.8  # 주먹

    def get_weapon_type(self):
        weapon = self.equipped.get("weapon")
        if weapon:
            data = ITEM_DATABASE.get(weapon, {})
            return data.get("type", "melee")
        return "melee"

    @property
    def chunk_pos(self):
        return (int(self.x) // CHUNK_SIZE, int(self.y) // CHUNK_SIZE)

    @property
    def tile_pos(self):
        return (int(self.x), int(self.y))

    @property
    def hp_ratio(self):
        return self.hp / self.max_hp if self.max_hp > 0 else 0

    @property
    def hunger_ratio(self):
        return self.hunger / PLAYER_MAX_HUNGER

    @property
    def thirst_ratio(self):
        return self.thirst / PLAYER_MAX_THIRST

    @property
    def stress_ratio(self):
        return self.stress / PLAYER_MAX_STRESS

    @property
    def stamina_ratio(self):
        return self.stamina / PLAYER_MAX_STAMINA

    def to_dict(self):
        """저장용"""
        return {
            "x": self.x, "y": self.y,
            "hp": self.hp, "hunger": self.hunger, "thirst": self.thirst,
            "stress": self.stress, "stamina": self.stamina,
            "shelter_defense": self.shelter_defense,
            "direction": self.direction,
            "inventory": self.inventory.to_dict(),
            "crafting": self.crafting.to_dict(),
            "equipped": dict(self.equipped),
            "killed_zombies": self.killed_zombies,
            "buildings_explored": self.buildings_explored,
            "items_crafted": self.items_crafted,
            "days_survived": self.days_survived,
            "discovered_biomes": list(self.discovered_biomes),
        }

    @classmethod
    def from_dict(cls, data, difficulty_settings=None):
        p = cls(data["x"], data["y"], difficulty_settings)
        p.hp = data.get("hp", PLAYER_MAX_HP)
        p.hunger = data.get("hunger", PLAYER_MAX_HUNGER)
        p.thirst = data.get("thirst", PLAYER_MAX_THIRST)
        p.stress = data.get("stress", 0)
        p.stamina = data.get("stamina", PLAYER_MAX_STAMINA)
        p.shelter_defense = data.get("shelter_defense", 10)
        p.direction = data.get("direction", 0)
        p.inventory = Inventory.from_dict(data.get("inventory", {}))
        p.crafting = CraftingSystem.from_dict(data.get("crafting", {}))
        p.equipped = data.get("equipped", {"head": None, "body": None, "feet": None, "weapon": None})
        p.killed_zombies = data.get("killed_zombies", 0)
        p.buildings_explored = data.get("buildings_explored", 0)
        p.items_crafted = data.get("items_crafted", 0)
        p.days_survived = data.get("days_survived", 0)
        p.discovered_biomes = set(data.get("discovered_biomes", []))
        return p
