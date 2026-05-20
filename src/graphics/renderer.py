"""
renderer.py - 코드 기반 그래픽 렌더러
모든 스프라이트를 기하학적 도형으로 생성 (외부 에셋 없음)
"""
import pygame
import math
import random
import functools
from settings import Colors, TILE_SIZE


def create_surface(w, h, alpha=True):
    """투명 서피스 생성"""
    if alpha:
        s = pygame.Surface((w, h), pygame.SRCALPHA)
    else:
        s = pygame.Surface((w, h))
    return s


# ============================================================
# 타일 렌더러
# ============================================================
class TileRenderer:
    """타일 스프라이트 캐시 및 렌더링"""

    @classmethod
    def clear_cache(cls):
        cls.get_tile.cache_clear()

    @classmethod
    @functools.lru_cache(maxsize=256)
    def get_tile(cls, tile_type, variant=0):
        return cls._render_tile(tile_type, variant)

    @classmethod
    def _render_tile(cls, tile_type, variant):
        s = create_surface(TILE_SIZE, TILE_SIZE, False)
        rng = random.Random(variant * 1000 + hash(tile_type))

        if tile_type == "grass":
            base = [Colors.GRASS_1, Colors.GRASS_2, Colors.GRASS_3][variant % 3]
            s.fill(base)
            for _ in range(5):
                gx = rng.randint(0, TILE_SIZE - 2)
                gy = rng.randint(0, TILE_SIZE - 2)
                gc = (base[0] + rng.randint(-10, 10), base[1] + rng.randint(-10, 15), base[2] + rng.randint(-8, 8))
                gc = tuple(max(0, min(255, c)) for c in gc)
                pygame.draw.rect(s, gc, (gx, gy, 2, 2))
            # 풀잎 디테일
            for _ in range(3):
                bx = rng.randint(2, TILE_SIZE - 2)
                by = rng.randint(2, TILE_SIZE - 2)
                bl = rng.randint(3, 6)
                bc = (base[0] - 15, base[1] + 20, base[2] - 10)
                bc = tuple(max(0, min(255, c)) for c in bc)
                pygame.draw.line(s, bc, (bx, by), (bx + rng.randint(-2, 2), by - bl), 1)

        elif tile_type == "dirt":
            base = [Colors.DIRT_1, Colors.DIRT_2][variant % 2]
            s.fill(base)
            for _ in range(8):
                dx = rng.randint(0, TILE_SIZE - 3)
                dy = rng.randint(0, TILE_SIZE - 3)
                dc = (base[0] + rng.randint(-15, 15), base[1] + rng.randint(-12, 12), base[2] + rng.randint(-10, 10))
                dc = tuple(max(0, min(255, c)) for c in dc)
                pygame.draw.rect(s, dc, (dx, dy, rng.randint(2, 4), rng.randint(2, 4)))

        elif tile_type == "road":
            s.fill(Colors.ROAD)
            for _ in range(4):
                rx = rng.randint(0, TILE_SIZE - 2)
                ry = rng.randint(0, TILE_SIZE - 2)
                rc = (Colors.ROAD[0] + rng.randint(-8, 8),) * 3
                rc = tuple(max(0, min(255, c)) for c in rc)
                pygame.draw.rect(s, rc, (rx, ry, rng.randint(1, 3), rng.randint(1, 3)))

        elif tile_type == "concrete":
            s.fill(Colors.CONCRETE)
            for _ in range(3):
                cx = rng.randint(0, TILE_SIZE - 2)
                cy = rng.randint(0, TILE_SIZE - 2)
                cc = tuple(max(0, min(255, Colors.CONCRETE[i] + rng.randint(-10, 10))) for i in range(3))
                pygame.draw.rect(s, cc, (cx, cy, rng.randint(2, 5), rng.randint(2, 5)))
            # 균열
            if variant % 4 == 0:
                points = [(rng.randint(0, TILE_SIZE), rng.randint(0, TILE_SIZE)) for _ in range(3)]
                pygame.draw.lines(s, (Colors.CONCRETE[0] - 30, Colors.CONCRETE[1] - 30, Colors.CONCRETE[2] - 30), False, points, 1)

        elif tile_type == "water":
            base = [Colors.WATER_1, Colors.WATER_2][variant % 2]
            s.fill(base)
            for _ in range(3):
                wy = rng.randint(0, TILE_SIZE)
                wc = (base[0] + 20, base[1] + 25, base[2] + 15)
                wc = tuple(max(0, min(255, c)) for c in wc)
                pygame.draw.line(s, wc, (0, wy), (TILE_SIZE, wy + rng.randint(-3, 3)), 1)

        elif tile_type == "sand":
            s.fill(Colors.SAND)
            for _ in range(6):
                sx2 = rng.randint(0, TILE_SIZE - 1)
                sy2 = rng.randint(0, TILE_SIZE - 1)
                sc = tuple(max(0, min(255, Colors.SAND[i] + rng.randint(-8, 8))) for i in range(3))
                pygame.draw.circle(s, sc, (sx2, sy2), 1)

        elif tile_type == "floor_wood":
            s.fill(Colors.FLOOR_WOOD)
            for i in range(0, TILE_SIZE, 8):
                wc = tuple(max(0, min(255, Colors.FLOOR_WOOD[j] + rng.randint(-12, 12))) for j in range(3))
                pygame.draw.rect(s, wc, (0, i, TILE_SIZE, 7))
                pygame.draw.line(s, (Colors.FLOOR_WOOD[0] - 20, Colors.FLOOR_WOOD[1] - 20, Colors.FLOOR_WOOD[2] - 20),
                               (0, i), (TILE_SIZE, i), 1)

        elif tile_type == "floor_tile":
            s.fill(Colors.FLOOR_TILE)
            offset = (variant % 2) * (TILE_SIZE // 2)
            for ix in range(0, TILE_SIZE + TILE_SIZE // 2, TILE_SIZE // 2):
                pygame.draw.line(s, (Colors.FLOOR_TILE[0] - 15,) * 3, (ix, 0), (ix, TILE_SIZE), 1)
            for iy in range(0, TILE_SIZE + TILE_SIZE // 2, TILE_SIZE // 2):
                pygame.draw.line(s, (Colors.FLOOR_TILE[0] - 15,) * 3, (0, iy), (TILE_SIZE, iy), 1)

        else:  # 기본
            s.fill(Colors.DARK_GRAY)

        return s


# ============================================================
# 캐릭터 렌더러
# ============================================================
class CharacterRenderer:
    """코드 기반 캐릭터 스프라이트 생성"""

    @classmethod
    def clear_cache(cls):
        cls.get_player_sprite.cache_clear()
        cls.get_zombie_sprite.cache_clear()
        cls.get_npc_sprite.cache_clear()

    @classmethod
    @functools.lru_cache(maxsize=128)
    def get_player_sprite(cls, direction=0, frame=0, has_weapon=False, is_crouching=False):
        return cls._render_player(direction, frame, has_weapon, is_crouching)

    @classmethod
    def _render_player(cls, direction, frame, has_weapon, is_crouching=False):
        size = TILE_SIZE
        s = create_surface(size, size)

        cx, cy = size // 2, size // 2
        # 방향: 0=하, 1=좌하, 2=좌, 3=좌상, 4=상, 5=우상, 6=우, 7=우하
        dir_offsets = [(0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (1, -1)]

        # 은신 시 Y오프셋으로 낮춘 자세 표현
        crouch_offset = 4 if is_crouching else 0

        # 걷기 애니메이션 오프셋 (은신 시 절반으로)
        anim_scale = 0.5 if is_crouching else 1.0
        walk_offset = math.sin(frame * 0.3) * 2 * anim_scale if frame > 0 else 0
        leg_swing = math.sin(frame * 0.6) * 3 * anim_scale if frame > 0 else 0

        # 몸통 (배낭 포함)
        body_color = Colors.PLAYER_SHIRT
        pygame.draw.rect(s, body_color, (cx - 5, cy - 3 + walk_offset * 0.3 + crouch_offset, 10, 10 - crouch_offset // 2), border_radius=2)

        # 배낭 (뒤를 보면 보임)
        if direction in [3, 4, 5]:
            pygame.draw.rect(s, (50, 60, 45), (cx - 4, cy - 1 + crouch_offset, 8, 7 - crouch_offset // 2), border_radius=1)

        # 다리 (은신 시 짧게)
        leg_y = cy + 7 + walk_offset * 0.3 + crouch_offset
        leg_len = 3 if is_crouching else 5
        pygame.draw.line(s, Colors.PLAYER_PANTS, (cx - 3, int(leg_y)), (cx - 3 - int(leg_swing), int(leg_y + leg_len)), 2)
        pygame.draw.line(s, Colors.PLAYER_PANTS, (cx + 3, int(leg_y)), (cx + 3 + int(leg_swing), int(leg_y + leg_len)), 2)

        # 신발
        pygame.draw.circle(s, (40, 35, 30), (int(cx - 3 - leg_swing), int(leg_y + leg_len)), 2)
        pygame.draw.circle(s, (40, 35, 30), (int(cx + 3 + leg_swing), int(leg_y + leg_len)), 2)

        # 팔
        arm_swing = leg_swing * 0.7
        arm_y = cy + walk_offset * 0.3 + crouch_offset
        pygame.draw.line(s, Colors.PLAYER_SKIN, (cx - 6, int(arm_y)), (cx - 8, int(arm_y + 4 - arm_swing)), 2)
        pygame.draw.line(s, Colors.PLAYER_SKIN, (cx + 6, int(arm_y)), (cx + 8, int(arm_y + 4 + arm_swing)), 2)

        # 무기 (오른손)
        if has_weapon:
            wx = cx + 8
            wy = int(arm_y + 4 + arm_swing)
            pygame.draw.line(s, (160, 160, 170), (wx, wy), (wx + 4, wy - 6), 2)

        # 머리
        head_y = cy - 7 + walk_offset * 0.2 + crouch_offset
        pygame.draw.circle(s, Colors.PLAYER_SKIN, (cx, int(head_y)), 5)

        # 머리카락
        pygame.draw.arc(s, Colors.PLAYER_HAIR, (cx - 5, int(head_y) - 6, 10, 8), 0, math.pi, 2)

        # 눈 (정면/측면)
        if direction in [0, 1, 7]:  # 아래 쪽 바라봄
            pygame.draw.circle(s, (30, 30, 35), (cx - 2, int(head_y)), 1)
            pygame.draw.circle(s, (30, 30, 35), (cx + 2, int(head_y)), 1)
        elif direction in [2]:  # 왼쪽
            pygame.draw.circle(s, (30, 30, 35), (cx - 3, int(head_y)), 1)
        elif direction in [6]:  # 오른쪽
            pygame.draw.circle(s, (30, 30, 35), (cx + 3, int(head_y)), 1)

        return s

    @classmethod
    @functools.lru_cache(maxsize=512)
    def get_zombie_sprite(cls, zombie_type="normal", direction=0, frame=0):
        return cls._render_zombie(zombie_type, direction, frame % 16)

    @classmethod
    def _render_zombie(cls, zombie_type, direction, frame):
        size = TILE_SIZE
        if zombie_type == "tank":
            size = int(TILE_SIZE * 1.5)
        s = create_surface(size, size)

        cx, cy = size // 2, size // 2
        walk_offset = math.sin(frame * 0.25) * 2
        stumble = math.sin(frame * 0.15) * 1.5  # 좀비 비틀거림

        skin = Colors.ZOMBIE_SKIN if zombie_type != "runner" else Colors.ZOMBIE_SKIN_DARK
        clothes = Colors.ZOMBIE_CLOTHES

        if zombie_type == "tank":
            # 탱크 좀비 (큰 체구)
            pygame.draw.rect(s, clothes, (cx - 8, cy - 5 + stumble, 16, 14), border_radius=3)
            pygame.draw.circle(s, skin, (cx + int(stumble), int(cy - 10)), 7)
            # 피
            pygame.draw.circle(s, Colors.ZOMBIE_BLOOD, (cx + 3, int(cy - 8)), 2)
            # 팔 (굵은)
            pygame.draw.line(s, skin, (cx - 9, int(cy + stumble)), (cx - 14, int(cy + 5)), 3)
            pygame.draw.line(s, skin, (cx + 9, int(cy + stumble)), (cx + 14, int(cy + 5)), 3)
            # 다리
            pygame.draw.line(s, clothes, (cx - 4, cy + 9), (cx - 5, cy + 15 + int(walk_offset)), 3)
            pygame.draw.line(s, clothes, (cx + 4, cy + 9), (cx + 5, cy + 15 - int(walk_offset)), 3)
        elif zombie_type == "runner":
            # 러너 좀비 (날씬, 빠름)
            pygame.draw.rect(s, clothes, (cx - 4, cy - 3 + stumble, 8, 9), border_radius=1)
            pygame.draw.circle(s, skin, (cx, int(cy - 7 + stumble * 0.5)), 4)
            # 앞으로 기울어진 포즈
            lean = 2
            pygame.draw.line(s, skin, (cx - 5, int(cy + stumble)), (cx - 9 - lean, int(cy + 3)), 2)
            pygame.draw.line(s, skin, (cx + 5, int(cy + stumble)), (cx + 9 + lean, int(cy + 1)), 2)
            pygame.draw.line(s, clothes, (cx - 2, cy + 6), (cx - 4, cy + 12 + int(walk_offset * 1.5)), 2)
            pygame.draw.line(s, clothes, (cx + 2, cy + 6), (cx + 4, cy + 12 - int(walk_offset * 1.5)), 2)
            # 빨간 눈
            pygame.draw.circle(s, (255, 30, 30), (cx - 2, int(cy - 7)), 1)
            pygame.draw.circle(s, (255, 30, 30), (cx + 2, int(cy - 7)), 1)
        elif zombie_type == "spider":
            # 스파이더 좀비 (네 발로 기어다님)
            pygame.draw.ellipse(s, skin, (cx - 6, cy - 3, 12, 8))
            pygame.draw.circle(s, skin, (cx, cy - 5), 4)
            pygame.draw.circle(s, (255, 50, 50), (cx - 2, cy - 5), 1)
            pygame.draw.circle(s, (255, 50, 50), (cx + 2, cy - 5), 1)
            # 다리 4쌍
            for i, ang in enumerate([30, 60, 120, 150]):
                anim = math.sin(frame * 0.4 + i * 1.2) * 3
                rad = math.radians(ang)
                lx = cx + int(math.cos(rad) * 10)
                ly = cy + int(math.sin(rad) * 6 + anim)
                pygame.draw.line(s, skin, (cx + int(math.cos(rad) * 5), cy), (lx, ly), 1)
                rad2 = math.radians(360 - ang)
                lx2 = cx + int(math.cos(rad2) * 10)
                ly2 = cy + int(math.sin(rad2) * 6 - anim)
                pygame.draw.line(s, skin, (cx + int(math.cos(rad2) * 5), cy), (lx2, ly2), 1)
        else:
            # 일반 좀비
            pygame.draw.rect(s, clothes, (cx - 5, cy - 2 + stumble, 10, 10), border_radius=1)
            pygame.draw.circle(s, skin, (cx + int(stumble * 0.5), int(cy - 6 + stumble * 0.3)), 5)
            # 찢어진 옷 디테일
            pygame.draw.line(s, (clothes[0] + 20, clothes[1] + 15, clothes[2] + 10), (cx - 3, cy + 2), (cx - 5, cy + 6), 1)
            # 팔 (한쪽은 앞으로 뻗음)
            pygame.draw.line(s, skin, (cx - 6, int(cy + stumble)), (cx - 9, int(cy + 5 - walk_offset)), 2)
            pygame.draw.line(s, skin, (cx + 6, int(cy + stumble)), (cx + 10, int(cy - 1 + walk_offset)), 2)
            # 다리
            pygame.draw.line(s, clothes, (cx - 3, cy + 8), (cx - 4, cy + 13 + int(walk_offset)), 2)
            pygame.draw.line(s, clothes, (cx + 3, cy + 8), (cx + 3, cy + 13 - int(walk_offset)), 2)
            # 약간의 피
            pygame.draw.circle(s, Colors.ZOMBIE_BLOOD, (cx + 2, int(cy - 4)), 1)
            # 눈
            pygame.draw.circle(s, (200, 200, 50), (cx - 2, int(cy - 6)), 1)
            pygame.draw.circle(s, (200, 200, 50), (cx + 2, int(cy - 6)), 1)

        return s

    @classmethod
    @functools.lru_cache(maxsize=128)
    def get_npc_sprite(cls, npc_type="merchant", direction=0, frame=0):
        return cls._render_npc(npc_type, direction, frame % 16)

    @classmethod
    def _render_npc(cls, npc_type, direction, frame):
        s = create_surface(TILE_SIZE, TILE_SIZE)
        cx, cy = TILE_SIZE // 2, TILE_SIZE // 2
        walk_offset = math.sin(frame * 0.3) * 1.5

        if npc_type == "merchant":
            cloak = Colors.NPC_MERCHANT_CLOAK
            pygame.draw.polygon(s, cloak, [
                (cx, cy - 10), (cx - 8, cy + 10), (cx + 8, cy + 10)
            ])
            pygame.draw.circle(s, (180, 155, 120), (cx, int(cy - 8)), 4)
            # 후드
            pygame.draw.arc(s, (cloak[0] - 15, cloak[1] - 15, cloak[2] - 10),
                          (cx - 5, cy - 13, 10, 8), 0, math.pi, 2)
            # 눈 (후드 아래서 빛남)
            pygame.draw.circle(s, (200, 180, 100), (cx - 2, int(cy - 7)), 1)
            pygame.draw.circle(s, (200, 180, 100), (cx + 2, int(cy - 7)), 1)
            # 배낭
            pygame.draw.rect(s, (80, 60, 40), (cx + 5, cy - 2, 5, 8), border_radius=1)

        elif npc_type == "survivor":
            # 일반 생존자
            shirt = Colors.NPC_SURVIVOR_SHIRT
            pygame.draw.rect(s, shirt, (cx - 5, cy - 2 + walk_offset * 0.3, 10, 10), border_radius=2)
            pygame.draw.circle(s, Colors.PLAYER_SKIN, (cx, int(cy - 6)), 4)
            pygame.draw.line(s, shirt, (cx - 6, int(cy + walk_offset * 0.3)), (cx - 8, int(cy + 4)), 2)
            pygame.draw.line(s, shirt, (cx + 6, int(cy + walk_offset * 0.3)), (cx + 8, int(cy + 4)), 2)
            pygame.draw.line(s, (50, 50, 60), (cx - 3, cy + 8), (cx - 3, cy + 13), 2)
            pygame.draw.line(s, (50, 50, 60), (cx + 3, cy + 8), (cx + 3, cy + 13), 2)

        elif npc_type == "soldier":
            uniform = Colors.NPC_SOLDIER_UNIFORM
            pygame.draw.rect(s, uniform, (cx - 5, cy - 3, 10, 11), border_radius=1)
            pygame.draw.circle(s, (180, 150, 120), (cx, int(cy - 7)), 4)
            # 헬멧
            pygame.draw.arc(s, (60, 70, 50), (cx - 5, cy - 12, 10, 8), 0, math.pi, 2)
            pygame.draw.rect(s, (60, 70, 50), (cx - 5, int(cy - 9), 10, 3))
            # 총
            pygame.draw.line(s, (80, 80, 85), (cx + 6, cy), (cx + 12, cy - 4), 2)
            # 다리
            pygame.draw.line(s, uniform, (cx - 3, cy + 8), (cx - 4, cy + 13), 2)
            pygame.draw.line(s, uniform, (cx + 3, cy + 8), (cx + 4, cy + 13), 2)

        return s


# ============================================================
# 환경 오브젝트 렌더러
# ============================================================
class EnvironmentRenderer:
    """나무, 바위, 관목 등 환경 오브젝트 렌더링"""

    @classmethod
    def clear_cache(cls):
        cls.get_tree.cache_clear()
        cls.get_stump.cache_clear()
        cls.get_rock.cache_clear()
        cls.get_bush.cache_clear()

    @classmethod
    @functools.lru_cache(maxsize=256)
    def get_tree(cls, tree_type="oak", variant=0):
        return cls._render_tree(tree_type, variant)

    @classmethod
    @functools.lru_cache(maxsize=64)
    def get_stump(cls, variant=0):
        return cls._render_stump(variant)

    @classmethod
    def _render_stump(cls, variant):
        w, h = TILE_SIZE * 2, TILE_SIZE * 2
        s = create_surface(w, h)
        cx, cy = w // 2, h // 2
        # 줄기 밑동
        pygame.draw.rect(s, Colors.TREE_TRUNK, (cx - 3, cy + 8, 6, 8))
        # 잘려나간 단면
        pygame.draw.ellipse(s, (150, 110, 70), (cx - 3, cy + 6, 6, 4))
        # 나이테 표현
        pygame.draw.ellipse(s, (120, 85, 45), (cx - 2, cy + 7, 4, 2))
        return s

    @classmethod
    def _render_tree(cls, tree_type, variant):
        w, h = TILE_SIZE * 2, TILE_SIZE * 2
        s = create_surface(w, h)
        cx, cy = w // 2, h // 2
        rng = random.Random(variant * 777 + hash(tree_type))

        if tree_type == "oak":
            # 줄기
            pygame.draw.rect(s, Colors.TREE_TRUNK, (cx - 3, cy + 2, 6, 14))
            # 잎 (원형 클러스터)
            for _ in range(5):
                lx = cx + rng.randint(-10, 10)
                ly = cy - rng.randint(2, 14)
                lr = rng.randint(6, 10)
                lc = [Colors.TREE_LEAVES_1, Colors.TREE_LEAVES_2, Colors.TREE_LEAVES_3][rng.randint(0, 2)]
                pygame.draw.circle(s, lc, (lx, ly), lr)

        elif tree_type == "pine":
            # 줄기
            pygame.draw.rect(s, Colors.TREE_TRUNK, (cx - 2, cy + 4, 4, 12))
            # 삼각형 잎 (3단)
            for i, (sy, sw, sh) in enumerate([(cy - 2, 16, 10), (cy - 8, 12, 8), (cy - 13, 8, 7)]):
                color = tuple(max(0, Colors.TREE_PINE[j] + rng.randint(-5, 10)) for j in range(3))
                pygame.draw.polygon(s, color, [
                    (cx, sy - sh), (cx - sw // 2, sy + 2), (cx + sw // 2, sy + 2)
                ])

        elif tree_type == "dead":
            # 죽은 나무 (가지만 남음)
            trunk_color = (70, 55, 40)
            pygame.draw.rect(s, trunk_color, (cx - 2, cy - 4, 4, 18))
            pygame.draw.line(s, trunk_color, (cx, cy - 2), (cx - 8, cy - 10), 2)
            pygame.draw.line(s, trunk_color, (cx, cy), (cx + 7, cy - 8), 2)
            pygame.draw.line(s, trunk_color, (cx - 8, cy - 10), (cx - 12, cy - 14), 1)
            pygame.draw.line(s, trunk_color, (cx + 7, cy - 8), (cx + 10, cy - 13), 1)

        return s

    @classmethod
    @functools.lru_cache(maxsize=64)
    def get_rock(cls, variant=0):
        return cls._render_rock(variant)

    @classmethod
    def _render_rock(cls, variant):
        s = create_surface(TILE_SIZE, TILE_SIZE)
        rng = random.Random(variant * 333)
        cx, cy = TILE_SIZE // 2, TILE_SIZE // 2

        # 불규칙한 돌 모양
        points = []
        num_points = rng.randint(5, 8)
        radius = rng.randint(5, 10)
        for i in range(num_points):
            angle = (2 * math.pi * i) / num_points + rng.uniform(-0.3, 0.3)
            r = radius + rng.randint(-2, 3)
            px = cx + int(math.cos(angle) * r)
            py = cy + int(math.sin(angle) * r)
            points.append((px, py))

        color = [Colors.ROCK_1, Colors.ROCK_2][variant % 2]
        pygame.draw.polygon(s, color, points)
        # 하이라이트
        highlight = tuple(min(255, c + 25) for c in color)
        if len(points) >= 3:
            pygame.draw.line(s, highlight, points[0], points[1], 1)

        return s

    @classmethod
    @functools.lru_cache(maxsize=64)
    def get_bush(cls, variant=0):
        return cls._render_bush(variant)

    @classmethod
    def _render_bush(cls, variant):
        s = create_surface(TILE_SIZE, TILE_SIZE)
        rng = random.Random(variant * 555)
        cx, cy = TILE_SIZE // 2, TILE_SIZE // 2 + 4

        for _ in range(3):
            bx = cx + rng.randint(-5, 5)
            by = cy + rng.randint(-4, 2)
            br = rng.randint(4, 7)
            bc = (Colors.BUSH[0] + rng.randint(-10, 10),
                  Colors.BUSH[1] + rng.randint(-10, 15),
                  Colors.BUSH[2] + rng.randint(-8, 8))
            bc = tuple(max(0, min(255, c)) for c in bc)
            pygame.draw.circle(s, bc, (bx, by), br)

        # 베리 (일부 관목에)
        if variant % 3 == 0:
            for _ in range(3):
                bx2 = cx + rng.randint(-4, 4)
                by2 = cy + rng.randint(-3, 2)
                pygame.draw.circle(s, (200, 50, 50), (bx2, by2), 2)

        return s


# ============================================================
# 건물 렌더러
# ============================================================
class BuildingRenderer:
    """건물 외관 렌더링"""

    @classmethod
    def clear_cache(cls):
        cls.get_building.cache_clear()

    @classmethod
    @functools.lru_cache(maxsize=128)
    def get_building(cls, building_type, width_tiles, height_tiles, variant=0):
        return cls._render_building(building_type, width_tiles, height_tiles, variant)

    @classmethod
    def _render_building(cls, building_type, w_tiles, h_tiles, variant):
        pw = w_tiles * TILE_SIZE
        ph = h_tiles * TILE_SIZE
        s = create_surface(pw, ph)
        rng = random.Random(variant * 999 + hash(building_type))

        # 벽 색상
        wall_colors = {
            "house": Colors.WALL_BRICK,
            "store": Colors.WALL_CONCRETE,
            "hospital": (220, 220, 225),
            "police": Colors.WALL_CONCRETE,
            "military": (90, 95, 80),
            "shelter": Colors.WALL_WOOD,
        }
        wall_color = wall_colors.get(building_type, Colors.WALL_CONCRETE)

        # 지붕 색상
        roof_colors = {
            "house": Colors.ROOF_1,
            "hospital": (200, 200, 205),
            "military": (70, 75, 65),
        }
        roof_color = roof_colors.get(building_type, Colors.ROOF_2)

        # 건물 몸체
        pygame.draw.rect(s, wall_color, (2, 4, pw - 4, ph - 6))
        # 지붕
        pygame.draw.rect(s, roof_color, (0, 0, pw, 6))

        # 창문
        window_spacing = TILE_SIZE
        for wx in range(window_spacing, pw - window_spacing // 2, window_spacing):
            for wy in range(TILE_SIZE // 2, ph - TILE_SIZE, TILE_SIZE):
                if rng.random() < 0.6:
                    ww, wh = 6, 8
                    ws = create_surface(ww, wh)
                    broken = rng.random() < 0.3
                    if broken:
                        ws.fill((80, 90, 100))
                        pygame.draw.line(ws, (60, 60, 70), (0, 0), (ww, wh), 1)
                        pygame.draw.line(ws, (60, 60, 70), (ww, 0), (0, wh), 1)
                    else:
                        ws.fill((100, 140, 180, 150))
                    s.blit(ws, (wx - ww // 2, wy))

        # 문
        door_x = pw // 2 - 5
        door_y = ph - TILE_SIZE + 2
        pygame.draw.rect(s, Colors.DOOR, (door_x, door_y, 10, TILE_SIZE - 4), border_radius=1)
        pygame.draw.circle(s, (180, 150, 80), (door_x + 8, door_y + TILE_SIZE // 2 - 2), 1)

        # 건물 타입별 특수 마크
        if building_type == "hospital":
            # 빨간 십자가
            cross_x, cross_y = pw // 2, TILE_SIZE // 2 + 4
            pygame.draw.rect(s, (200, 40, 40), (cross_x - 4, cross_y - 1, 8, 3))
            pygame.draw.rect(s, (200, 40, 40), (cross_x - 1, cross_y - 4, 3, 8))
        elif building_type == "police":
            # 'P' 표시
            pygame.draw.rect(s, (40, 80, 160), (pw // 2 - 6, 8, 12, 10), border_radius=2)
        elif building_type == "military":
            # 별 마크
            star_x, star_y = pw // 2, 12
            pygame.draw.polygon(s, (180, 180, 60), [
                (star_x, star_y - 5), (star_x + 2, star_y - 1),
                (star_x + 5, star_y), (star_x + 2, star_y + 2),
                (star_x + 3, star_y + 5), (star_x, star_y + 3),
                (star_x - 3, star_y + 5), (star_x - 2, star_y + 2),
                (star_x - 5, star_y), (star_x - 2, star_y - 1),
            ])

        return s


# ============================================================
# 아이템 아이콘 렌더러
# ============================================================
class ItemIconRenderer:
    """인벤토리용 아이템 아이콘 생성"""

    ICON_SIZE = 32

    @classmethod
    @functools.lru_cache(maxsize=128)
    def get_icon(cls, item_id):
        return cls._render_icon(item_id)

    @classmethod
    def _render_icon(cls, item_id):
        sz = cls.ICON_SIZE
        s = create_surface(sz, sz)
        cx, cy = sz // 2, sz // 2

        renderers = {
            "식량통조림": cls._draw_can,
            "생수": cls._draw_water,
            "구급상자": cls._draw_medkit,
            "방독면": cls._draw_gasmask,
            "손전등": cls._draw_flashlight,
            "비상용 배터리": cls._draw_battery,
            "무기": cls._draw_weapon_melee,
            "운동화": cls._draw_shoes,
            "지도": cls._draw_map,
            "방탄조끼": cls._draw_vest,
            "진통제": cls._draw_pills,
            "라디오 부품": cls._draw_radio_part,
            "나무": cls._draw_wood,
            "못": cls._draw_nails,
            "천": cls._draw_cloth,
            "약초": cls._draw_herb,
            "파이프": cls._draw_pipe,
            "나이프": cls._draw_knife,
            "도끼": cls._draw_axe,
            "권총": cls._draw_pistol,
            "탄약": cls._draw_ammo,
            "야구방망이": cls._draw_bat,
            "바리케이드 재료": cls._draw_barricade_mat,
            "고급 치료킷": cls._draw_adv_medkit,
            "개조 손전등": cls._draw_mod_flashlight,
            "장거리 무전기": cls._draw_radio,
        }

        renderer = renderers.get(item_id)
        if renderer:
            renderer(s, cx, cy, sz)
        else:
            # 기본 아이콘
            pygame.draw.rect(s, (100, 100, 110), (4, 4, sz - 8, sz - 8), border_radius=4)
            pygame.draw.rect(s, (140, 140, 150), (4, 4, sz - 8, sz - 8), 1, border_radius=4)

        return s

    @staticmethod
    def _draw_can(s, cx, cy, sz):
        pygame.draw.rect(s, (180, 180, 185), (cx - 7, cy - 6, 14, 12), border_radius=2)
        pygame.draw.rect(s, (160, 50, 40), (cx - 6, cy - 3, 12, 6))
        pygame.draw.rect(s, (200, 200, 205), (cx - 3, cy - 8, 6, 3), border_radius=1)

    @staticmethod
    def _draw_water(s, cx, cy, sz):
        pygame.draw.rect(s, (180, 220, 240), (cx - 5, cy - 7, 10, 14), border_radius=2)
        pygame.draw.rect(s, (140, 190, 220), (cx - 3, cy - 9, 6, 4), border_radius=1)
        pygame.draw.rect(s, (60, 140, 220), (cx - 4, cy, 8, 5))

    @staticmethod
    def _draw_medkit(s, cx, cy, sz):
        pygame.draw.rect(s, (220, 220, 225), (cx - 8, cy - 6, 16, 12), border_radius=2)
        pygame.draw.rect(s, (200, 40, 40), (cx - 4, cy - 2, 8, 3))
        pygame.draw.rect(s, (200, 40, 40), (cx - 1, cy - 5, 3, 8))

    @staticmethod
    def _draw_gasmask(s, cx, cy, sz):
        pygame.draw.circle(s, (60, 65, 55), (cx, cy), 9)
        pygame.draw.circle(s, (40, 45, 35), (cx, cy), 9, 2)
        pygame.draw.circle(s, (100, 140, 160, 150), (cx - 3, cy - 2), 3)
        pygame.draw.circle(s, (100, 140, 160, 150), (cx + 3, cy - 2), 3)
        pygame.draw.ellipse(s, (50, 55, 45), (cx - 4, cy + 3, 8, 5))

    @staticmethod
    def _draw_flashlight(s, cx, cy, sz):
        pygame.draw.rect(s, (80, 80, 85), (cx - 3, cy - 8, 6, 14), border_radius=1)
        pygame.draw.rect(s, (120, 120, 125), (cx - 4, cy - 8, 8, 4), border_radius=1)
        pygame.draw.circle(s, (255, 255, 200), (cx, cy - 9), 3)

    @staticmethod
    def _draw_battery(s, cx, cy, sz):
        pygame.draw.rect(s, (60, 60, 65), (cx - 5, cy - 6, 10, 12), border_radius=1)
        pygame.draw.rect(s, (200, 200, 60), (cx - 3, cy - 4, 6, 3))
        pygame.draw.rect(s, (80, 80, 85), (cx - 2, cy - 8, 4, 3))

    @staticmethod
    def _draw_weapon_melee(s, cx, cy, sz):
        pygame.draw.line(s, (160, 160, 170), (cx - 2, cy + 8), (cx + 2, cy - 10), 3)
        pygame.draw.rect(s, (100, 70, 40), (cx - 3, cy + 5, 6, 5), border_radius=1)

    @staticmethod
    def _draw_shoes(s, cx, cy, sz):
        pygame.draw.ellipse(s, (60, 60, 180), (cx - 8, cy - 2, 10, 8))
        pygame.draw.ellipse(s, (60, 60, 180), (cx - 2, cy - 4, 10, 8))
        pygame.draw.rect(s, (50, 50, 50), (cx - 8, cy + 4, 16, 3), border_radius=1)

    @staticmethod
    def _draw_map(s, cx, cy, sz):
        pygame.draw.rect(s, (220, 210, 180), (cx - 8, cy - 6, 16, 12), border_radius=1)
        pygame.draw.line(s, (150, 100, 80), (cx - 5, cy - 3), (cx + 4, cy - 1), 1)
        pygame.draw.line(s, (150, 100, 80), (cx - 3, cy + 1), (cx + 6, cy + 3), 1)
        pygame.draw.circle(s, (200, 50, 50), (cx + 3, cy - 2), 2)

    @staticmethod
    def _draw_vest(s, cx, cy, sz):
        pygame.draw.rect(s, (60, 80, 60), (cx - 7, cy - 6, 14, 14), border_radius=2)
        pygame.draw.rect(s, (50, 70, 50), (cx - 5, cy - 4, 4, 10))
        pygame.draw.rect(s, (50, 70, 50), (cx + 1, cy - 4, 4, 10))
        pygame.draw.rect(s, (70, 90, 70), (cx - 6, cy - 2, 12, 2))

    @staticmethod
    def _draw_pills(s, cx, cy, sz):
        pygame.draw.rect(s, (230, 230, 235), (cx - 6, cy - 4, 12, 8), border_radius=3)
        for i in range(3):
            pygame.draw.circle(s, (200 + i * 15, 80, 80), (cx - 3 + i * 3, cy), 2)

    @staticmethod
    def _draw_radio_part(s, cx, cy, sz):
        pygame.draw.rect(s, (50, 120, 50), (cx - 6, cy - 5, 12, 10), border_radius=1)
        pygame.draw.line(s, (180, 180, 60), (cx, cy - 5), (cx, cy - 10), 2)
        pygame.draw.line(s, (180, 180, 60), (cx, cy - 10), (cx + 3, cy - 12), 1)
        pygame.draw.circle(s, (255, 60, 60), (cx - 3, cy - 2), 2)
        pygame.draw.circle(s, (60, 200, 60), (cx + 3, cy - 2), 2)

    @staticmethod
    def _draw_wood(s, cx, cy, sz):
        pygame.draw.rect(s, (130, 90, 50), (cx - 7, cy - 3, 5, 12))
        pygame.draw.rect(s, (140, 100, 55), (cx - 1, cy - 5, 5, 14))
        pygame.draw.rect(s, (120, 85, 45), (cx + 5, cy - 2, 4, 10))

    @staticmethod
    def _draw_nails(s, cx, cy, sz):
        for i in range(4):
            nx = cx - 5 + i * 4
            pygame.draw.line(s, (180, 180, 185), (nx, cy + 5), (nx, cy - 5), 1)
            pygame.draw.circle(s, (200, 200, 205), (nx, cy - 5), 1)

    @staticmethod
    def _draw_cloth(s, cx, cy, sz):
        pygame.draw.rect(s, (180, 170, 150), (cx - 7, cy - 5, 14, 10), border_radius=1)
        for y in range(cy - 4, cy + 5, 2):
            pygame.draw.line(s, (160, 150, 130), (cx - 6, y), (cx + 6, y), 1)

    @staticmethod
    def _draw_herb(s, cx, cy, sz):
        pygame.draw.line(s, (50, 120, 40), (cx, cy + 6), (cx, cy - 2), 2)
        pygame.draw.circle(s, (40, 150, 50), (cx - 3, cy - 4), 3)
        pygame.draw.circle(s, (50, 140, 45), (cx + 3, cy - 5), 3)
        pygame.draw.circle(s, (45, 160, 55), (cx, cy - 6), 3)

    @staticmethod
    def _draw_pipe(s, cx, cy, sz):
        pygame.draw.line(s, (140, 140, 145), (cx - 1, cy + 8), (cx + 1, cy - 10), 3)

    @staticmethod
    def _draw_knife(s, cx, cy, sz):
        pygame.draw.polygon(s, (190, 195, 200), [(cx, cy - 10), (cx - 2, cy + 2), (cx + 2, cy + 2)])
        pygame.draw.rect(s, (100, 70, 40), (cx - 2, cy + 2, 4, 5), border_radius=1)

    @staticmethod
    def _draw_axe(s, cx, cy, sz):
        pygame.draw.line(s, (120, 85, 50), (cx - 1, cy + 8), (cx + 1, cy - 6), 2)
        pygame.draw.polygon(s, (170, 175, 180), [(cx + 1, cy - 6), (cx + 7, cy - 3), (cx + 1, cy)])

    @staticmethod
    def _draw_pistol(s, cx, cy, sz):
        pygame.draw.rect(s, (60, 60, 65), (cx - 6, cy - 3, 12, 4), border_radius=1)
        pygame.draw.rect(s, (50, 50, 55), (cx - 1, cy + 1, 4, 6), border_radius=1)

    @staticmethod
    def _draw_ammo(s, cx, cy, sz):
        pygame.draw.rect(s, (140, 120, 50), (cx - 6, cy - 4, 12, 8), border_radius=2)
        for i in range(3):
            pygame.draw.rect(s, (180, 160, 60), (cx - 4 + i * 3, cy - 2, 2, 5), border_radius=1)

    @staticmethod
    def _draw_bat(s, cx, cy, sz):
        pygame.draw.line(s, (160, 130, 80), (cx - 2, cy + 8), (cx + 2, cy - 10), 4)
        pygame.draw.circle(s, (170, 140, 85), (cx + 2, cy - 10), 3)

    @staticmethod
    def _draw_barricade_mat(s, cx, cy, sz):
        pygame.draw.line(s, (120, 85, 50), (cx - 6, cy - 4), (cx - 6, cy + 6), 3)
        pygame.draw.line(s, (120, 85, 50), (cx + 6, cy - 4), (cx + 6, cy + 6), 3)
        pygame.draw.line(s, (120, 85, 50), (cx - 8, cy), (cx + 8, cy), 2)
        pygame.draw.line(s, (120, 85, 50), (cx - 7, cy - 4), (cx + 7, cy + 4), 2)

    @staticmethod
    def _draw_adv_medkit(s, cx, cy, sz):
        pygame.draw.rect(s, (240, 240, 245), (cx - 8, cy - 6, 16, 12), border_radius=2)
        pygame.draw.rect(s, (40, 160, 40), (cx - 4, cy - 2, 8, 3))
        pygame.draw.rect(s, (40, 160, 40), (cx - 1, cy - 5, 3, 8))
        pygame.draw.circle(s, (40, 160, 40), (cx + 5, cy - 4), 2)

    @staticmethod
    def _draw_mod_flashlight(s, cx, cy, sz):
        pygame.draw.rect(s, (90, 90, 95), (cx - 4, cy - 8, 8, 16), border_radius=2)
        pygame.draw.rect(s, (140, 140, 145), (cx - 5, cy - 8, 10, 5), border_radius=2)
        pygame.draw.circle(s, (255, 255, 150), (cx, cy - 10), 4)

    @staticmethod
    def _draw_radio(s, cx, cy, sz):
        pygame.draw.rect(s, (50, 120, 50), (cx - 7, cy - 5, 14, 12), border_radius=2)
        pygame.draw.line(s, (200, 200, 60), (cx + 4, cy - 5), (cx + 4, cy - 12), 2)
        pygame.draw.circle(s, (255, 60, 60), (cx - 3, cy - 2), 2)
        pygame.draw.rect(s, (30, 90, 30), (cx - 5, cy + 2, 10, 3), border_radius=1)


# ============================================================
# UI 그래픽 헬퍼
# ============================================================
def draw_rounded_rect(surface, color, rect, radius=8, border=0, border_color=None):
    """둥근 모서리 사각형 그리기 (알파 지원)"""
    x, y, w, h = rect
    if len(color) == 4:
        s = create_surface(w, h)
        pygame.draw.rect(s, color, (0, 0, w, h), border_radius=radius)
        if border > 0 and border_color:
            pygame.draw.rect(s, border_color, (0, 0, w, h), border, border_radius=radius)
        surface.blit(s, (x, y))
    else:
        pygame.draw.rect(surface, color, rect, border_radius=radius)
        if border > 0 and border_color:
            pygame.draw.rect(surface, border_color, rect, border, border_radius=radius)


def draw_gradient_rect(surface, rect, color_top, color_bottom, vertical=True, radius=0):
    """그라데이션 사각형"""
    x, y, w, h = rect
    s = create_surface(w, h)
    steps = h if vertical else w
    for i in range(steps):
        t = i / max(1, steps - 1)
        color = tuple(int(color_top[j] + (color_bottom[j] - color_top[j]) * t) for j in range(min(len(color_top), len(color_bottom))))
        if vertical:
            pygame.draw.line(s, color, (0, i), (w, i))
        else:
            pygame.draw.line(s, color, (i, 0), (i, h))
    if radius > 0:
        mask = create_surface(w, h)
        pygame.draw.rect(mask, (255, 255, 255), (0, 0, w, h), border_radius=radius)
        s.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surface.blit(s, (x, y))


def draw_glow(surface, pos, radius, color, intensity=0.5):
    """글로우 이펙트"""
    glow_surf = create_surface(radius * 2, radius * 2)
    for r in range(radius, 0, -1):
        alpha = int(intensity * 255 * (r / radius) ** 2)
        alpha = min(255, alpha)
        c = (*color[:3], alpha)
        pygame.draw.circle(glow_surf, c, (radius, radius), r)
    surface.blit(glow_surf, (pos[0] - radius, pos[1] - radius), special_flags=pygame.BLEND_ALPHA_SDL2)
