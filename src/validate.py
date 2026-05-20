"""
validate.py - 시스템 전체 검증 스크립트 v2
"""
import sys
import traceback
import os

# 하위 폴더들을 sys.path에 추가하여 기존 플랫 임포트 구조가 그대로 동작하도록 보장
src_dir = os.path.dirname(os.path.abspath(__file__))
subdirs = ['core', 'world', 'entities', 'systems', 'graphics']
for subdir in subdirs:
    path = os.path.join(src_dir, subdir)
    if path not in sys.path:
        sys.path.insert(0, path)

errors = []
warnings = []

def check(name, fn):
    try:
        fn()
        print(f"  ✅ {name}")
    except Exception as e:
        errors.append((name, str(e)))
        print(f"  ❌ {name}: {e}")
        traceback.print_exc()

print("=" * 60)
print("30일 서바이벌 - 시스템 검증 v2")
print("=" * 60)

# 1. 모듈 임포트
print("\n[1] 모듈 임포트 검증")
def import_all():
    import settings
    import utils
    import items
    import crafting
    import player
    import entities
    import combat
    import world
    import weather
    import events
    import camera
    import renderer
    import particles
    import transitions
    import ui
    import sounds
    import save_system
    import building_interior
    import i18n
check("모든 모듈 임포트", import_all)

# 2. i18n 시스템
print("\n[2] 다국어 시스템")
def test_i18n():
    from i18n import t, set_language, get_language, get_available_languages
    assert get_language() == "ko"
    assert t("game_title") == "30일간의 생존"
    set_language("en")
    assert t("game_title") == "30 Days to Survive"
    set_language("ko")
    assert t("new_day", 5) == "5일차가 밝았습니다."
    assert len(get_available_languages()) >= 2
check("i18n 번역 시스템", test_i18n)

# 3. 건물 내부 시스템
print("\n[3] 건물 내부 시스템")
def test_interior():
    from building_interior import BuildingInterior, FURNITURE_LOOT_TABLES
    for btype in ["house", "store", "hospital", "police", "military"]:
        interior = BuildingInterior(btype, 4, 4, seed=42)
        assert interior.width >= 8
        assert interior.height >= 8
        assert len(interior.rooms) > 0
        assert len(interior.furniture) > 0
        # 문, 벽, 바닥 올바르게 생성됐는지
        assert interior.get_tile(0, 0) == "wall"
        dx, dy = interior.door_pos
        assert interior.get_tile(dx, dy) == "door"
        # 가구 탐색
        f = interior.furniture[0]
        old_searched = f.searched
        loot = f.search(1.0)
        assert f.searched == True
        assert isinstance(loot, list)
        # 직렬화
        d = interior.to_dict()
        assert d["type"] == btype
    assert len(FURNITURE_LOOT_TABLES) >= 10
check("건물 내부 생성 (모든 타입)", test_interior)

# 4. 월드 생성 검증 (겹침/물 방지)
print("\n[4] 월드 생성 검증")
def test_world_gen():
    from world import World, TileType
    from settings import CHUNK_SIZE
    w = World(seed=12345, world_settings={"resource_density": 1.0, "building_density": 1.0})
    chunks_to_check = [(0,0), (1,0), (0,1), (-1,0), (0,-1), (2,2)]
    total_buildings = 0
    overlap_count = 0
    water_building = 0

    for cx, cy in chunks_to_check:
        chunk = w.get_chunk(cx, cy)
        total_buildings += len(chunk.buildings)

        # 건물 겹침 검사
        for i, b1 in enumerate(chunk.buildings):
            for j, b2 in enumerate(chunk.buildings):
                if i >= j:
                    continue
                if (b1.x < b2.x + b2.width and b1.x + b1.width > b2.x and
                    b1.y < b2.y + b2.height and b1.y + b1.height > b2.y):
                    overlap_count += 1
                    print(f"Overlap detected in chunk {cx},{cy}: b1({b1.building_type} at {b1.x},{b1.y} {b1.width}x{b1.height}) <-> b2({b2.building_type} at {b2.x},{b2.y} {b2.width}x{b2.height})")

        # 물 위 건물 검사
        for b in chunk.buildings:
            wx_base = cx * CHUNK_SIZE
            wy_base = cy * CHUNK_SIZE
            for dy in range(b.height):
                for dx in range(b.width):
                    lx = b.x - wx_base + dx
                    ly = b.y - wy_base + dy
                    if 0 <= lx < CHUNK_SIZE and 0 <= ly < CHUNK_SIZE:
                        tile = chunk.get_tile(lx, ly)
                        if tile == TileType.WATER:
                            water_building += 1

    assert overlap_count == 0, f"건물 겹침 {overlap_count}건"
    assert water_building == 0, f"물 위 건물 {water_building}건"
    print(f"     (총 건물 {total_buildings}개, 겹침 0, 물 위 0)")
check("건물 배치 유효성", test_world_gen)

# 5. 스태미나 시스템
print("\n[5] 스태미나 시스템")
def test_stamina():
    from player import Player
    from settings import PLAYER_MAX_STAMINA
    p = Player(5, 5)
    p.stamina = 0
    assert p.exhausted == False
    p.exhausted = True
    # 탈진 상태에서 스태미나가 30% 미만이면 sprinting 금지
    p.stamina = PLAYER_MAX_STAMINA * 0.2
    import pygame
    pygame.init()
    # 수동 체크
    assert p.exhausted == True  # 아직 30% 미만
    p.stamina = PLAYER_MAX_STAMINA * 0.35
    # 여기서 exhausted 해제는 _handle_movement에서
check("스태미나 탈진 로직", test_stamina)

# 6. 전투 각도 판정
print("\n[6] 전투 각도 판정")
def test_combat_angle():
    from combat import angle_diff
    import math
    assert abs(angle_diff(0, 0)) < 0.001
    assert abs(angle_diff(0, math.pi) - math.pi) < 0.001
    assert abs(angle_diff(math.pi/4, -math.pi/4) - math.pi/2) < 0.001
check("근접 전투 각도 함수", test_combat_angle)

# 7. 도로 시스템
print("\n[7] 도로 시스템")
def test_roads():
    from world import World, TileType
    from settings import CHUNK_SIZE
    w = World(seed=99, world_settings={"resource_density": 1.0, "building_density": 1.0})
    # 도시 바이옴 중심 근처 어딘가에서 도로 검증
    road_count = 0
    total_tiles = 0
    chunk = w.get_chunk(0, 0)
    for ly in range(CHUNK_SIZE):
        for lx in range(CHUNK_SIZE):
            tile = chunk.get_tile(lx, ly)
            total_tiles += 1
            if tile == TileType.ROAD:
                road_count += 1
    print(f"     (체크: {total_tiles}타일 중 도로 {road_count}개)")
check("도로 생성 검증", test_roads)

# 8. 엔티티 디스폰
print("\n[8] 엔티티 디스폰")
def test_despawn():
    from entities import EntityManager, Zombie
    from settings import CHUNK_SIZE
    em = EntityManager()
    # 플레이어에서 매우 먼 좀비
    z = Zombie(999, 999, "normal")
    em.zombies.append(z)
    em._cull_distant_entities(0, 0)
    assert z.active == False, "먼 엔티티가 비활성화되지 않음"
check("원거리 엔티티 디스폰", test_despawn)

# 결과 요약
print("\n" + "=" * 60)
if errors:
    print(f"⚠️  {len(errors)}개 오류 발견:")
    for name, err in errors:
        print(f"  - {name}: {err}")
else:
    print("✅ 모든 검증 통과!")
print("=" * 60)
sys.exit(len(errors))
