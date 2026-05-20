"""
combat.py - 전투 시스템
마우스 방향 기반 부채꼴 판정, 원거리 조준
"""
import math
import random
import pygame
from utils import distance, direction_to, angle_between
from items import ITEM_DATABASE
from settings import TILE_SIZE


def angle_diff(a, b):
    """두 각도(라디안) 사이의 최소 차이 (정규화)"""
    d = (a - b) % (2 * math.pi)
    if d > math.pi:
        d -= 2 * math.pi
    return abs(d)


class CombatSystem:
    """전투 로직 관리"""

    def __init__(self):
        self.hit_effects = []   # [(x, y, timer)]
        self.damage_numbers = []  # [(x, y, damage, timer, color)]

    def update(self, dt):
        self.hit_effects = [(x, y, t - dt) for x, y, t in self.hit_effects if t > 0]
        self.damage_numbers = [(x, y - dt * 30, d, t - dt, c)
                               for x, y, d, t, c in self.damage_numbers if t > 0]

    def player_attack(self, player, entity_manager, world, camera=None):
        """플레이어 공격 (camera 필요: 마우스→월드 좌표 변환)"""
        if not player.attack_cooldown.is_ready("attack"):
            return None

        weapon = player.equipped.get("weapon")
        weapon_data = ITEM_DATABASE.get(weapon, {}) if weapon else {}
        weapon_type = weapon_data.get("type", "melee")

        damage = player.get_attack_damage()
        attack_range = player.get_attack_range()

        # 마우스 방향 → 월드 좌표 → 공격 각도
        mouse_sx, mouse_sy = pygame.mouse.get_pos()
        center_x = player.x + 0.5
        center_y = player.y + 0.5
        
        if camera:
            # 스크린 좌표 → 월드 좌표
            mouse_wx, mouse_wy = camera.screen_to_world(mouse_sx, mouse_sy)
        else:
            mouse_wx = center_x + 1
            mouse_wy = center_y

        attack_angle = math.atan2(mouse_wy - center_y, mouse_wx - center_x)

        results = []

        if weapon_type == "melee":
            # 근접 공격 - 부채꼴 60° (±30°) 판정
            MELEE_ARC = math.pi / 3  # 60도
            targets = entity_manager.get_nearby_zombies(center_x, center_y, attack_range + 0.5)

            for zombie in targets:
                zx = zombie.x + 0.5
                zy = zombie.y + 0.5
                if distance(zx, zy, center_x, center_y) > attack_range:
                    continue
                target_angle = math.atan2(zy - center_y, zx - center_x)
                if angle_diff(target_angle, attack_angle) > MELEE_ARC / 2:
                    continue  # 부채꼴 밖 → 미스

                actual_damage = damage + random.randint(-2, 3)
                kb_dir = direction_to(player.x, player.y, zombie.x, zombie.y)
                zombie.take_damage(actual_damage, kb_dir)

                self.hit_effects.append((zombie.x, zombie.y, 0.3))
                self.damage_numbers.append((zombie.x, zombie.y - 0.5, actual_damage, 1.0, (255, 255, 100)))
                results.append(("hit", zombie, actual_damage))

                if zombie.is_dead:
                    player.killed_zombies += 1
                    results.append(("kill", zombie, 0))

        elif weapon_type == "ranged":
            ammo_type = weapon_data.get("ammo")
            if ammo_type and not player.inventory.has_item(ammo_type):
                results.append(("no_ammo", None, 0))
            else:
                if ammo_type:
                    player.inventory.remove_item(ammo_type, 1)

                # 총성 발사 신호 (어그로 트리거용)
                results.append(("gunshot_fired", None, 0))

                # 마우스 방향에서 가장 가까운 적 (±15° 내)
                RANGED_ARC = math.pi / 6  # 30도
                targets = entity_manager.get_nearby_zombies(center_x, center_y, attack_range + 0.5)
                valid = []
                for z in targets:
                    zx = z.x + 0.5
                    zy = z.y + 0.5
                    if distance(zx, zy, center_x, center_y) > attack_range:
                        continue
                    t_angle = math.atan2(zy - center_y, zx - center_x)
                    if angle_diff(t_angle, attack_angle) <= RANGED_ARC:
                        valid.append(z)

                if valid:
                    target = min(valid, key=lambda z: distance(z.x + 0.5, z.y + 0.5, center_x, center_y))
                    actual_damage = damage + random.randint(-3, 5)
                    kb_dir = direction_to(center_x, center_y, target.x, target.y)
                    target.take_damage(actual_damage, kb_dir)

                    self.hit_effects.append((target.x, target.y, 0.3))
                    self.damage_numbers.append((target.x, target.y - 0.5, actual_damage, 1.0, (255, 200, 50)))
                    results.append(("hit", target, actual_damage))

                    if target.is_dead:
                        player.killed_zombies += 1
                        results.append(("kill", target, 0))

        attack_speed = weapon_data.get("attack_speed", 0.5)
        player.attack_cooldown.set_cooldown("attack", attack_speed)
        return results

    def process_zombie_attacks(self, player, entity_manager):
        """좀비 공격 처리"""
        results = []
        px = player.x + 0.5
        py = player.y + 0.5
        for zombie in entity_manager.zombies:
            if zombie.is_dead or not zombie.active:
                continue
            if zombie.can_attack():
                dist = distance(zombie.x + 0.5, zombie.y + 0.5, px, py)
                if dist <= zombie.attack_range:
                    damage = zombie.do_attack()
                    actual = player.take_damage(damage, "좀비 공격")
                    if actual > 0:
                        self.damage_numbers.append(
                            (player.x, player.y - 0.5, int(actual), 1.0, (255, 60, 60))
                        )
                        results.append(("player_hit", zombie, actual))
        return results

    def get_hit_effects(self):
        return self.hit_effects

    def get_damage_numbers(self):
        return self.damage_numbers
