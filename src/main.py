"""
main.py - 30일간의 생존 (좀비 아포칼립스 오픈월드 서바이벌)
엔트리포인트, 메인 게임 루프, 씬 매니저
"""
import pygame
import sys
import os

# 하위 폴더들을 sys.path에 추가하여 기존 플랫 임포트 구조가 그대로 동작하도록 보장
src_dir = os.path.dirname(os.path.abspath(__file__))
subdirs = ['core', 'world', 'entities', 'systems', 'graphics']
for subdir in subdirs:
    path = os.path.join(src_dir, subdir)
    if path not in sys.path:
        sys.path.insert(0, path)

import math
import random
import time as pytime

from settings import (Colors, FPS, TILE_SIZE, CHUNK_SIZE, RENDER_DISTANCE,
                       DIFFICULTY_PRESETS, DEFAULT_WORLD_SETTINGS,
                       GameSettings, RESOLUTION_OPTIONS)
from camera import Camera
from world import World
from player import Player
from entities import EntityManager, Zombie, NPC, ZombieState
from combat import CombatSystem
from weather import TimeSystem, WeatherSystem
from events import EventSystem, determine_ending
from items import ITEM_DATABASE, generate_loot
from renderer import (TileRenderer, CharacterRenderer, EnvironmentRenderer,
                       BuildingRenderer, draw_rounded_rect, draw_glow, ItemIconRenderer)
from particles import ParticleSystem, ParticleEmitters
from transitions import TransitionManager
from world_renderer import WorldSceneRenderer
from ui import (FontManager, HUD, InventoryUI, CraftingUI, DialogueUI,
                EventLogUI, MainMenuUI, WorldCreationUI, SettingsUI,
                PauseUI, EndingUI)
from sounds import SoundGenerator
from save_system import save_game, load_game, get_save_files, GameSaveManager
from interaction import InteractionHandler
from building_interior import BuildingInterior
from i18n import t, set_language, get_language


# ============================================================
# 게임 상태
# ============================================================
class GameState:
    MAIN_MENU = "main_menu"
    WORLD_CREATION = "world_creation"
    SETTINGS = "settings"
    LOADING = "loading"
    PLAYING = "playing"
    BUILDING_INTERIOR = "building_interior"
    PAUSED = "paused"
    INVENTORY = "inventory"
    CRAFTING = "crafting"
    DIALOGUE = "dialogue"
    ENDING = "ending"
    GAME_OVER = "game_over"


# ============================================================
# 메인 게임 클래스
# ============================================================
class Game:
    """메인 게임"""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("30일간의 생존 - 좀비 아포칼립스")

        self.game_settings = GameSettings()
        self.screen_w = self.game_settings.width
        self.screen_h = self.game_settings.height

        self._create_window()

        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.MAIN_MENU

        # 폰트 초기화
        FontManager.init()
        SoundGenerator.init()

        # 전환 효과
        self.transition = TransitionManager()

        # 렌더러 및 상호작용 매니저
        self.world_renderer = WorldSceneRenderer(self)
        self.interaction_handler = InteractionHandler(self)

        # UI 시스템
        self._init_ui()

        # 메뉴 파티클
        self.menu_particles = ParticleSystem()

        # 게임 월드 (게임 시작 시 생성)
        self.world = None
        self.player = None
        self.camera = None
        self.entity_manager = None
        self.combat_system = None
        self.time_system = None
        self.weather_system = None
        self.event_system = None
        self.game_particles = None

        self.world_settings = None
        self.difficulty = None
        self.sandbox_mode = False
        self.current_day = 1
        self.total_days = 30
        self.day_changed = False
        self.last_day = 1
        self.playtime = 0

        # 상호작용 상태
        self.interact_target = None
        self.chunk_unload_timer = 0.0
        self.loading_progress = 0

        # 건물 내부 상태
        self.current_interior = None     # BuildingInterior 객체
        self.interior_camera = None      # 내부용 카메라
        self.interior_building_ref = None # 외부 건물 참조
        self.interior_zombies = []       # 내부 은신형 좀비
        self.explored_interiors = {}     # 건물_id -> BuildingInterior (delta 저장)

        # 습격(Raid) 시스템 상태
        self.raid_active = False
        self.raid_warned = False       # 18:00 경고 표시 여부
        self.raid_spawned = False      # 22:00 좀비 스폰 여부
        self.raid_zombies = []         # 습격 전용 좀비 리스트
        self.raid_strength = 0         # 이번 습격의 강도

    def _create_window(self):
        """창 생성"""
        flags = pygame.RESIZABLE
        if self.game_settings.fullscreen:
            flags = pygame.FULLSCREEN | pygame.SCALED
        self.screen = pygame.display.set_mode(
            (self.screen_w, self.screen_h), flags
        )

    def _init_ui(self):
        """UI 초기화"""
        w, h = self.screen_w, self.screen_h
        self.main_menu_ui = MainMenuUI(w, h)
        self.world_creation_ui = WorldCreationUI(w, h)
        self.settings_ui = SettingsUI(w, h)
        self.hud = HUD(w, h)
        self.inventory_ui = InventoryUI(w, h)
        self.crafting_ui = CraftingUI(w, h)
        self.dialogue_ui = DialogueUI(w, h)
        self.event_log_ui = EventLogUI(w, h)
        self.pause_ui = PauseUI(w, h)
        self.ending_ui = EndingUI(w, h)

    def _apply_resolution(self):
        """해상도 변경 적용"""
        self.screen_w = self.game_settings.width
        self.screen_h = self.game_settings.height
        self._create_window()
        self._init_ui()
        if self.camera:
            self.camera.resize(self.screen_w, self.screen_h)

    # ============================================================
    # 게임 시작 / 로드
    # ============================================================
    def start_new_game(self, world_settings):
        """새 게임 시작"""
        self.world_settings = world_settings
        diff_name = world_settings.get("difficulty", "보통")
        self.difficulty = DIFFICULTY_PRESETS.get(diff_name, DIFFICULTY_PRESETS["보통"])
        self.total_days = world_settings.get("total_days", 30)

        seed = world_settings.get("seed") or random.randint(0, 2**31)
        world_settings["seed"] = seed

        # 월드 생성
        self.world = World(seed=seed, world_settings=world_settings)

        # 플레이어 (은신처 문 앞에 스폰)
        spawn_x = CHUNK_SIZE // 2 + 0.5
        spawn_y = CHUNK_SIZE // 2 + 3.5  # 은신처 문 바로 아래
        self.player = Player(spawn_x, spawn_y, self.difficulty)

        # 시작 아이템
        if world_settings.get("starting_items", True):
            self.player.inventory.add_item("생수", 2)
            self.player.inventory.add_item("식량통조림", 1)
            self.player.inventory.add_item("붕대", 2)

        # 샌드박스 모드
        self.sandbox_mode = world_settings.get("sandbox", False)
        if self.sandbox_mode:
            self.player.inventory.slots = 100  # 슬롯 대폭 확장
            self.player.inventory.is_sandbox = True
            for item_name, item_data in ITEM_DATABASE.items():
                if item_data.get("stackable"):
                    count = item_data.get("max_stack", 10)
                else:
                    count = 1
                self.player.inventory.add_item(item_name, count)

        # 시스템 초기화
        self.camera = Camera()
        self.camera.resize(self.screen_w, self.screen_h)
        self.entity_manager = EntityManager(self.difficulty)
        self.combat_system = CombatSystem()
        day_len = world_settings.get("day_length_minutes", 12)
        self.time_system = TimeSystem(day_len)
        weather_var = world_settings.get("weather_variability", 1.0)
        self.weather_system = WeatherSystem(weather_var)
        self.event_system = EventSystem(self.difficulty)
        self.game_particles = ParticleSystem()

        self.current_day = 1
        self.last_day = 1
        self.playtime = 0
        self.day_changed = False

        # 초기 청크 로드
        self.world.get_chunk(0, 0)

        self.state = GameState.PLAYING
        if self.sandbox_mode:
            self.event_system.add_log("★ [샌드박스 모드] 모든 아이템이 지급되었습니다!")
        self.event_system.add_log("★ 30일간의 생존이 시작됩니다. 구조대가 올 때까지 살아남으세요!")
        SoundGenerator.play("day_start")

    def load_saved_game(self):
        """저장된 게임 로드"""
        saves = get_save_files()
        if not saves:
            return False

        data = load_game(saves[0]["filename"].replace(".json", ""))
        if not data:
            return False

        if GameSaveManager.deserialize_game(self, data):
            self.state = GameState.PLAYING
            self.event_system.add_log(f"★ Day {self.current_day} - 게임을 불러왔습니다.")
            return True
        return False

    def save_current_game(self):
        """현재 게임 저장 (월드 상태 델타 포함)"""
        game_data = GameSaveManager.serialize_game(self)
        if not game_data:
            return

        world_name = self.world_settings.get("world_name", "autosave").replace(" ", "_")
        if save_game(game_data, world_name):
            self.event_system.add_log("✓ 게임이 저장되었습니다.")
            SoundGenerator.play("craft_complete")

    # ============================================================
    # 메인 루프
    # ============================================================
    def run(self):
        """메인 게임 루프"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)  # 프레임 레이트 안전장치

            self._handle_events()
            self._update(dt)
            self._draw()

            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def _handle_events(self):
        """이벤트 처리"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.VIDEORESIZE:
                self.screen_w = event.w
                self.screen_h = event.h
                self.game_settings.resolution = [event.w, event.h]
                self._init_ui()
                if self.camera:
                    self.camera.resize(self.screen_w, self.screen_h)
                if self.interior_camera:
                    self.interior_camera.resize(self.screen_w, self.screen_h)

            # 전환 중엔 입력 무시
            if self.transition.is_active:
                continue

            if self.state == GameState.MAIN_MENU:
                result = self.main_menu_ui.handle_event(event)
                if result == "new_game":
                    SoundGenerator.play("menu_select")
                    self.transition.start("fade", 0.6,
                        on_mid=lambda: setattr(self, 'state', GameState.WORLD_CREATION))
                elif result == "load_game":
                    SoundGenerator.play("menu_select")
                    self.transition.start("fade", 0.6,
                        on_mid=lambda: self.load_saved_game() or setattr(self, 'state',
                            GameState.PLAYING if self.player else GameState.MAIN_MENU))
                elif result == "settings":
                    SoundGenerator.play("menu_select")
                    self.transition.start("fade", 0.4,
                        on_mid=lambda: setattr(self, 'state', GameState.SETTINGS))
                elif result == "quit":
                    self.running = False

            elif self.state == GameState.WORLD_CREATION:
                result = self.world_creation_ui.handle_event(event)
                if result == "start":
                    SoundGenerator.play("menu_select")
                    ws = self.world_creation_ui.get_settings()
                    self.transition.start("circle", 1.0,
                        on_mid=lambda: self.start_new_game(ws))
                elif result == "back":
                    self.transition.start("fade", 0.4,
                        on_mid=lambda: setattr(self, 'state', GameState.MAIN_MENU))

            elif self.state == GameState.SETTINGS:
                result = self.settings_ui.handle_event(event)
                if result == "apply":
                    self._apply_resolution()
                elif result == "back":
                    self.transition.start("fade", 0.4,
                        on_mid=lambda: setattr(self, 'state', GameState.MAIN_MENU))

            elif self.state in (GameState.PLAYING, GameState.BUILDING_INTERIOR):
                self._process_global_inputs(event)

            elif self.state == GameState.PAUSED:
                result = self.pause_ui.handle_event(event)
                if result == "resume":
                    self.state = GameState.PLAYING
                elif result == "save":
                    self.save_current_game()
                elif result == "settings":
                    self.state = GameState.SETTINGS
                elif result == "main_menu":
                    self.save_current_game()
                    self.transition.start("fade", 0.6,
                        on_mid=lambda: setattr(self, 'state', GameState.MAIN_MENU))

            elif self.state == GameState.ENDING:
                result = self.ending_ui.handle_event(event)
                if result == "main_menu":
                    self.transition.start("fade", 1.0,
                        on_mid=lambda: setattr(self, 'state', GameState.MAIN_MENU))

    def _process_global_inputs(self, event):
        """게임플레이 중 이벤트"""
        # 인벤토리/크래프팅이 열려있으면 우선 처리
        if self.inventory_ui.visible:
            # 단축키(I, ESC, C) 입력은 아래쪽 글로벌 단축키 처리로 통과시킴
            if not (event.type == pygame.KEYDOWN and event.key in (pygame.K_i, pygame.K_ESCAPE, pygame.K_c)):
                result = self.inventory_ui.handle_event(event, self.player)
                if result:
                    action, value = result
                    if action == "use":
                        if value == "바리케이드 재료":
                            # 바리케이드 재료는 은신처 내부에서만 사용 가능
                            if self.player.is_interior and self.current_interior and \
                               self.interior_building_ref and hasattr(self.interior_building_ref, 'building_type') and \
                               self.interior_building_ref.building_type == "shelter":
                                self.player.inventory.remove_item(value, 1)
                                self.player.shelter_defense += 10
                                self.event_system.add_log(f"바리케이드를 설치했습니다! (방어도 +10 → {self.player.shelter_defense})")
                                SoundGenerator.play("pickup")
                            else:
                                self.event_system.add_log("바리케이드 재료는 은신처 내부에서만 사용할 수 있습니다.")
                                SoundGenerator.play("error")
                        elif self.player.use_item(value):
                            self.event_system.add_log(f"'{value}'을(를) 사용했습니다.")
                            SoundGenerator.play("pickup")
                    elif action == "equip":
                        equip_world = self.current_interior if self.player.is_interior else self.world
                        if self.player.equip_item(value, equip_world):
                            self.event_system.add_log(f"'{value}'을(를) 장착했습니다.")
                            SoundGenerator.play("pickup")
                    elif action == "drop_item":
                        # 아이템 바닥에 버리기
                        if self.player.inventory.has_item(value):
                            self.player.inventory.remove_item(value, 1)
                            if self.player.is_interior and self.current_interior:
                                self.current_interior.drop_item(value, self.player.x, self.player.y)
                            else:
                                self.world.drop_item(value, self.player.x, self.player.y)
                            self.event_system.add_log(f"'{value}'을(를) 버렸습니다.")
                            SoundGenerator.play("pickup")
                    elif action == "unequip":
                        # 장착 해제
                        item = self.player.equipped.get(value)
                        if item:
                            if self.player.inventory.add_item(item):
                                self.player.equipped[value] = None
                                self.event_system.add_log(f"'{item}'을(를) 해제했습니다.")
                                SoundGenerator.play("pickup")
                            else:
                                self.event_system.add_log("인벤토리 빈 공간이 부족합니다!")
                return

        if self.crafting_ui.visible:
            # 단축키(I, ESC, C) 입력은 아래쪽 글로벌 단축키 처리로 통과시킴
            if not (event.type == pygame.KEYDOWN and event.key in (pygame.K_i, pygame.K_ESCAPE, pygame.K_c)):
                result = self.crafting_ui.handle_event(event, self.player)
                if result:
                    action, recipe_name = result
                    if action == "craft":
                        if self.player.crafting.start_craft(recipe_name, self.player.inventory):
                            self.event_system.add_log(f"'{recipe_name}' 제작을 시작합니다...")
                            SoundGenerator.play("craft_complete")
                return

        if self.dialogue_ui.visible:
            self.dialogue_ui.handle_event(event)
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.inventory_ui.visible:
                    self.inventory_ui.toggle()
                elif self.crafting_ui.visible:
                    self.crafting_ui.toggle()
                else:
                    self.state = GameState.PAUSED
            elif event.key == pygame.K_i:
                self.inventory_ui.toggle()
                if self.crafting_ui.visible:
                    self.crafting_ui.toggle()
            elif event.key == pygame.K_c:
                self.crafting_ui.toggle()
                if self.inventory_ui.visible:
                    self.inventory_ui.toggle()
            elif event.key == pygame.K_e:
                if self.state == GameState.BUILDING_INTERIOR:
                    self.interaction_handler.handle_interior_interaction()
                else:
                    self.interaction_handler.handle_interaction()
            elif event.key == pygame.K_F5:
                self.save_current_game()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and not self.inventory_ui.visible and not self.crafting_ui.visible:
                if self.state == GameState.BUILDING_INTERIOR:
                    self._handle_interior_attack()
                else:
                    self._handle_exterior_attack()

    def _handle_exterior_attack(self):
        # 공격
        results = self.combat_system.player_attack(
            self.player, self.entity_manager, self.world, self.camera
        )
        if results:
            for action, target, dmg in results:
                if action == "hit":
                    SoundGenerator.play("hit_melee")
                    self.camera.shake(3, 0.15)
                    # 피 파티클
                    if target:
                        self.game_particles.emit(
                            lambda: ParticleEmitters.blood(
                                target.x * TILE_SIZE, target.y * TILE_SIZE),
                            5)
                elif action == "kill":
                    SoundGenerator.play("zombie_die")
                    self.event_system.add_log("좀비를 처치했습니다!")
                    if target:
                        loot = target.get_loot()
                        for item in loot:
                            self.world.drop_item(item, target.x, target.y)
                            self.event_system.add_log(f"  [{item}] 드롭!")
                elif action == "no_ammo":
                    self.event_system.add_log("탄약이 부족합니다!")
                elif action == "gunshot_fired":
                    SoundGenerator.play("gunshot")
                    self._trigger_gunshot_noise(self.player.x, self.player.y, False)


    def _trigger_gunshot_noise(self, px, py, is_interior):
        """총성 소음 어그로: 반경 내 좀비를 Chase 상태로 전환"""
        NOISE_RADIUS = 60  # 타일 단위 (~3~4 청크)
        if is_interior:
            for z in self.interior_zombies:
                if not z.is_dead and z.active:
                    z.state = "chase"
                    z.aggro_alert = 2.0
        else:
            nearby = self.entity_manager.get_nearby_zombies(px, py, NOISE_RADIUS)
            for z in nearby:
                if z.state in ("idle", "wander"):
                    z.state = "chase"
                    z.aggro_alert = 2.0

    # ============================================================
    # 건물 내부 진입/퇴장
    # ============================================================
    def _enter_building(self, building):
        """건물 내부로 진입"""
        building_id = f"{building.x}_{building.y}"

        # 이미 탐색한 건물이면 기존 내부 복원
        if building_id in self.explored_interiors:
            self.current_interior = self.explored_interiors[building_id]
        else:
            self.current_interior = BuildingInterior(
                building.building_type,
                building.width, building.height,
                seed=hash(building_id) + (self.world.seed if self.world else 0)
            )
            self.explored_interiors[building_id] = self.current_interior

        self.interior_building_ref = building
        self.player.enter_interior(float(self.current_interior.door_pos[0]), float(self.current_interior.door_pos[1] - 1))

        # 내부 카메라
        self.interior_camera = Camera()
        self.interior_camera.resize(self.screen_w, self.screen_h)

        # 내부 좀비 (Bug②: type과 hp를 복원)
        self.interior_zombies = []
        for zdata in self.current_interior.zombies:
            z_type = zdata.get("type", "normal")
            z = Zombie(zdata["x"], zdata["y"], z_type, self.difficulty)
            z.speed *= 0.5  # 은신형 좀비는 느림
            z.detection_range = 3
            if "hp" in zdata:
                z.hp = zdata["hp"]
            self.interior_zombies.append(z)

        if not building.explored:
            building.explored = True
            self.player.buildings_explored += 1

        SoundGenerator.play("door_open")
        self.event_system.add_log(t("entering_building"))

        self.transition.start("fade", 0.5,
            on_mid=lambda: setattr(self, 'state', GameState.BUILDING_INTERIOR))

    def _exit_building(self):
        """건물에서 나가기"""
        # 살아있는 좀비만 건물 내부 상태에 동기화 (Bug②: hp와 type도 저장)
        if self.current_interior is not None:
            self.current_interior.zombies = [
                {"x": z.x, "y": z.y, "hp": z.hp, "type": z.zombie_type}
                for z in self.interior_zombies
                if not z.is_dead and z.active
            ]
        self.player.exit_interior()
        self.current_interior = None
        self.interior_building_ref = None
        self.interior_zombies = []

        SoundGenerator.play("door_open")
        self.event_system.add_log(t("exiting_building"))

        self.transition.start("fade", 0.5,
            on_mid=lambda: setattr(self, 'state', GameState.PLAYING))

    def _handle_interior_attack(self):
        if not self.player.attack_cooldown.is_ready("attack"):
            return

        weapon = self.player.equipped.get("weapon")
        weapon_data = ITEM_DATABASE.get(weapon, {}) if weapon else {}
        weapon_type = weapon_data.get("type", "melee")
        speed = weapon_data.get("speed", 1.0)
        self.player.attack_cooldown.set_cooldown("attack", speed)

        damage = self.player.get_attack_damage()
        attack_range = self.player.get_attack_range()

        mouse_sx, mouse_sy = pygame.mouse.get_pos()
        mouse_wx, mouse_wy = self.interior_camera.screen_to_world(mouse_sx, mouse_sy)

        px, py = self.player.x, self.player.y
        attack_angle = math.atan2(mouse_wy - py, mouse_wx - px)
        
        hit_zombies = []
        from combat import angle_diff

        if weapon_type == "melee":
            for z in self.interior_zombies:
                if z.is_dead or not z.active: continue
                dist = math.sqrt((z.x - px)**2 + (z.y - py)**2)
                if dist <= attack_range:
                    angle_to_target = math.atan2(z.y - py, z.x - px)
                    if abs(angle_diff(attack_angle, angle_to_target)) <= math.pi / 6:
                        hit_zombies.append(z)
        else:
            closest_z = None
            min_dist = 999
            for z in self.interior_zombies:
                if z.is_dead or not z.active: continue
                dist = math.sqrt((z.x - px)**2 + (z.y - py)**2)
                if dist <= attack_range:
                    angle_to_target = math.atan2(z.y - py, z.x - px)
                    if abs(angle_diff(attack_angle, angle_to_target)) <= math.pi / 12:
                        if dist < min_dist:
                            min_dist = dist
                            closest_z = z
            if closest_z:
                hit_zombies.append(closest_z)

        if weapon_type == "melee":
            SoundGenerator.play("melee_swing")
            self.player.stamina = max(0, self.player.stamina - 5)
        else:
            SoundGenerator.play("gunshot")
            self._trigger_gunshot_noise(px, py, True)

        for z in hit_zombies:
            z.take_damage(damage)
            actual_damage = damage
            self.combat_system.damage_numbers.append((z.x, z.y - 0.5, actual_damage, 1.0, (255, 255, 100)))
            if weapon_type == "melee":
                SoundGenerator.play("hit_melee")
                self.interior_camera.shake(3, 0.15)
            self.game_particles.emit(lambda: ParticleEmitters.blood(z.x * TILE_SIZE, z.y * TILE_SIZE))
            
            kb_dist = 1.0 if weapon_type == "melee" else 0.5
            angle = math.atan2(z.y - py, z.x - px)
            z.x += math.cos(angle) * kb_dist
            z.y += math.sin(angle) * kb_dist
            
            if z.is_dead:
                self.player.killed_zombies += 1
                self.event_system.add_log(t("zombie_killed"))
                # 건물 내부 좀비 전리품 드롭 (내부 바닥에)
                loot = z.get_loot() if hasattr(z, 'get_loot') else []
                for item_name in loot:
                    if self.current_interior:
                        self.current_interior.drop_item(item_name, z.x, z.y)
                    self.event_system.add_log(f"  [{item_name}] 드롭!")


    def _update(self, dt):
        """상태별 업데이트"""
        self.transition.update(dt)
        if self.transition.is_active:
            return

        if self.state == GameState.MAIN_MENU:
            self.main_menu_ui.update(dt)
            self.menu_particles.update(dt)
            if random.random() < 0.05:
                from particles import ParticleEmitters
                self.menu_particles.emit(lambda: ParticleEmitters.ember(self.screen_w // 2, self.screen_h), 1)

        elif self.state == GameState.WORLD_CREATION:
            pass

        elif self.state == GameState.SETTINGS:
            pass

        elif self.state in (GameState.PLAYING, GameState.BUILDING_INTERIOR):
            self._process_global_update(dt)

        elif self.state == GameState.PAUSED:
            pass

        elif self.state == GameState.ENDING:
            self.ending_ui.update(dt)


    def _process_global_update(self, dt):
        """게임플레이 및 건물 내부 공통 업데이트"""
        if not self.player or not self.player.alive:
            return

        is_interior = (self.state == GameState.BUILDING_INTERIOR)
        current_world = self.current_interior if is_interior else self.world
        cam = self.interior_camera if is_interior else self.camera

        self.playtime += dt

        # 시간 & 날씨 (내부에서도 시간은 흐름)
        self.time_system.update(dt)
        if not is_interior:
            self.weather_system.update(dt)

        # 날짜 변경 체크
        self.current_day = self.time_system.current_day
        if self.current_day != self.last_day:
            self.last_day = self.current_day
            self.player.days_survived = self.current_day
            self._on_new_day()

        # 습격(Raid) 시스템 처리
        self._update_raid_system(dt)

        # 플레이어
        weather = self.weather_system.current_weather if not is_interior and self.weather_system else None
        self.player.update(dt, current_world, weather)

        # 카메라
        if cam:
            cam.set_target(self.player.x, self.player.y)
            cam.update(dt)

        # 엔티티 (외부 vs 내부)
        if is_interior:
            for z in self.interior_zombies:
                if not z.is_dead and z.active:
                    z.update(dt, self.player.x, self.player.y, current_world, self.player.is_crouching)
                    if z.state == "attack" and z.can_attack():
                        damage = z.do_attack()
                        actual = self.player.take_damage(damage, "은신형 좀비")
                        if actual > 0:
                            self.combat_system.damage_numbers.append((self.player.x, self.player.y - 0.5, actual, 1.0, (255, 60, 60)))
                            self.event_system.add_log(f"은신형 좀비에게 {int(actual)} 피해!")
                            if self.camera: self.camera.shake(3, 0.2)
                            self.interior_camera.shake(3, 0.2)
        else:
            self.entity_manager.update(dt, self.player, self.world)
            combat_results = self.combat_system.process_zombie_attacks(self.player, self.entity_manager)
            for action, zombie, dmg in combat_results:
                if action == "player_hit":
                    from sounds import SoundGenerator
                    from particles import ParticleEmitters
                    SoundGenerator.play("player_hurt")
                    self.camera.shake(5, 0.2)
                    self.game_particles.emit(
                        lambda: ParticleEmitters.blood(
                            self.player.x * 32, self.player.y * 32), 3)

        # 전투, 이벤트, 파티클
        self.combat_system.update(dt)
        self.event_system.update(dt, self.player, self.current_day)
        self.game_particles.update(dt)

        # 발자국 먼지 (은신 중에는 발생하지 않음)
        if self.player.moving and not self.player.is_crouching and self.player.footstep_timer > 0.3:
            self.player.footstep_timer = 0
            from particles import ParticleEmitters
            self.game_particles.emit(
                lambda: ParticleEmitters.footstep_dust(
                    self.player.x * 32, self.player.y * 32), 2)

        # UI
        self.hud.update(dt, self.player)
        self.inventory_ui.update(dt)
        self.crafting_ui.update(dt)

        # 청크 관리 (외부일 때만)
        if not is_interior:
            self.chunk_unload_timer += dt
            if self.chunk_unload_timer >= 2.0:
                pcx, pcy = self.player.chunk_pos
                self.world.unload_far_chunks(pcx, pcy, 5) # RENDER_DISTANCE is roughly 5 chunks
                self.chunk_unload_timer = 0.0

        # 플레이어 사망 체크
        if not self.player.alive:
            self.transition.start("fade", 1.5,
                on_mid=lambda: self._trigger_ending())

        # 엔딩 날짜 체크
        if self.current_day > self.total_days:
            self.transition.start("fade", 1.5,
                on_mid=lambda: self._trigger_ending())

    def _on_new_day(self):
        """새로운 날 시작"""
        self.event_system.add_log(f"═══ Day {self.current_day} ═══")
        SoundGenerator.play("day_start")

        # 새 날 이벤트
        events = self.event_system.check_new_day_events(self.player, self.current_day)

        # 바이옴 발견 추적
        biome = self.world.get_biome(int(self.player.x), int(self.player.y))
        if biome not in self.player.discovered_biomes:
            self.player.discovered_biomes.add(biome)
            self.event_system.add_log(f"새로운 지역 발견: {biome}")

        # 자동 저장 (5일마다)
        if self.current_day % 5 == 0:
            self.save_current_game()

        # 새 날에 습격 상태 초기화
        self.raid_active = False
        self.raid_warned = False
        self.raid_spawned = False
        self.raid_zombies = []
        self.raid_strength = 0

    def _update_raid_system(self, dt):
        """습격 시스템 시간별 처리"""
        if not self.time_system or not self.difficulty:
            return

        hour = self.time_system.current_hour
        day = self.current_day

        # 18:00 - 습격 여부 판정 및 경고
        if 18.0 <= hour < 19.0 and not self.raid_warned:
            self.raid_warned = True
            is_horde_night = (day % 7 == 0)
            raid_chance = self.difficulty.get("raid_chance", 0.1)

            if is_horde_night or (random.random() < raid_chance):
                self.raid_active = True
                zombie_count = 5 + day // 3  # 날이 갈수록 강해짐
                if is_horde_night:
                    zombie_count = int(zombie_count * 2)  # 호드 밤은 2배
                self.raid_strength = zombie_count
                if is_horde_night:
                    self.event_system.add_log(f"⚠ [호드 경고] 오늘 밤 대규모 좀비 습격이 예상됩니다! ({zombie_count}마리)")
                else:
                    self.event_system.add_log(f"⚠ [습격 경고] 오늘 밤 좀비 무리가 접근하고 있습니다... ({zombie_count}마리)")
                self.hud.add_notification("⚠ 습격 예보! 방어를 준비하세요!", 5.0)

        # 22:00 - 습격 좀비 스폰
        if hour >= 22.0 and self.raid_active and not self.raid_spawned:
            self.raid_spawned = True
            self._spawn_raid_zombies()

        # 습격 중 좀비 전멸 체크
        if self.raid_active and self.raid_spawned:
            alive_raid = [z for z in self.raid_zombies if not z.is_dead and z.active]
            if len(alive_raid) == 0:
                self.raid_active = False
                self.event_system.add_log("★ 습격 방어 완료: 좀비 무리를 모두 물리쳤습니다! ★")
                self.hud.add_notification("★ 습격 방어 성공! ★", 4.0)

        # 06:00 - 아직 활성 상태이면 자동 해결
        if 6.0 <= hour < 7.0 and self.raid_active and self.raid_spawned:
            self._resolve_raid()

    def _spawn_raid_zombies(self):
        """은신처 주변에 습격 좀비를 스폰"""
        import random as rng
        shelter_x, shelter_y = 8, 8  # 은신처 위치 (0,0 청크의 8,8)
        count = self.raid_strength

        for i in range(count):
            # 은신처 주변 5~12타일에 스폰
            angle = rng.uniform(0, 2 * math.pi)
            dist = rng.uniform(5, 12)
            sx = shelter_x + math.cos(angle) * dist
            sy = shelter_y + math.sin(angle) * dist

            # 타입 결정 (날이 지날수록 강한 좀비)
            z_type = "normal"
            roll = rng.random()
            if self.current_day >= 14 and roll < 0.15:
                z_type = "tank"
            elif self.current_day >= 7 and roll < 0.3:
                z_type = "runner"

            z = Zombie(sx, sy, z_type, self.difficulty)
            z.state = ZombieState.CHASE
            z.is_raid_zombie = True
            self.raid_zombies.append(z)
            self.entity_manager.zombies.append(z)

        self.event_system.add_log(f"⚔ 습격 시작! {count}마리의 좀비가 은신처를 공격합니다!")

    def _resolve_raid(self):
        """습격 자동 해결 (방어도 대조)"""
        alive_count = len([z for z in self.raid_zombies if not z.is_dead and z.active])
        defense = self.player.shelter_defense

        if defense >= alive_count * 2:
            # 완전 방어: 방어도 차감
            cost = alive_count
            self.player.shelter_defense = max(0, defense - cost)
            self.event_system.add_log(f"★ 바리케이드가 습격을 막아냈습니다! (방어도 -{cost})")
        else:
            # 돌파: HP 손실 + 스트레스 증가 + 방어도 전소
            breach_damage = (alive_count - defense // 2) * 5
            self.player.hp -= breach_damage
            self.player.stress += 25
            self.player.shelter_defense = 0
            self.event_system.add_log(f"✕ 바리케이드가 돌파되었습니다! (HP -{int(breach_damage)}, 방어도 → 0)")

        # 남은 습격 좀비 정리
        for z in self.raid_zombies:
            if not z.is_dead and z.active:
                z.active = False
        self.raid_zombies = []
        self.raid_active = False

    def _trigger_ending(self):
        """엔딩 트리거"""
        if not self.player.alive:
            # 게임 오버 (사망)
            ending_data = {
                "title": f"게임 오버: {self.player.cause_of_death}",
                "description": f"당신은 {self.current_day}일차에 '{self.player.cause_of_death}'(으)로 생을 마감했습니다.\n"
                              "폐허 속에서의 투쟁은 여기서 끝이 났습니다...",
            }
        else:
            # 엔딩 달성
            _, ending_data = determine_ending(self.player)

        self.ending_ui.show(ending_data, self.player)
        self.state = GameState.ENDING
        SoundGenerator.play("game_over")

    # ============================================================
    # 렌더링
    # ============================================================
    def _draw(self):
        """상태별 렌더링"""
        if self.state == GameState.MAIN_MENU:
            self.main_menu_ui.draw(self.screen)
            self.menu_particles.draw(self.screen)

        elif self.state == GameState.WORLD_CREATION:
            self.world_creation_ui.draw(self.screen)

        elif self.state == GameState.SETTINGS:
            self.settings_ui.draw(self.screen)

        elif self.state == GameState.PLAYING:
            self._draw_gameplay()

        elif self.state == GameState.BUILDING_INTERIOR:
            self._draw_interior_gameplay()

        elif self.state == GameState.PAUSED:
            if self.current_interior:
                self._draw_interior_gameplay()
            else:
                self._draw_gameplay()
            self.pause_ui.draw(self.screen)

        elif self.state == GameState.ENDING:
            self.ending_ui.draw(self.screen)

        # 전환 효과
        self.transition.draw(self.screen)

        # FPS 표시
        if self.game_settings.show_fps:
            font = FontManager.get(12)
            fps_text = font.render(f"FPS: {int(self.clock.get_fps())}", True, (100, 255, 100))
            self.screen.blit(fps_text, (self.screen_w - 80, 5))

    def _draw_gameplay(self):
        """게임플레이 렌더링"""
        if not self.world or not self.player or not self.camera:
            self.screen.fill(Colors.BLACK)
            return

        # 하늘 색상
        sky_color = self.time_system.get_sky_color()
        self.screen.fill(sky_color)

        # 게임 월드를 렌더링할 서피스
        game_surface = self.screen

        # 타일 렌더링
        self.world_renderer.draw_tiles(game_surface)

        # 바닥 아이템
        self.world_renderer.draw_ground_items(game_surface)

        # 환경 오브젝트
        self.world_renderer.draw_environment(game_surface)

        # 건물
        self.world_renderer.draw_buildings(game_surface)

        # 엔티티 (좀비, NPC)
        self.world_renderer.draw_entities(game_surface)

        # 플레이어
        self.world_renderer.draw_player(game_surface)
        self.world_renderer.draw_aim_indicator(game_surface, self.player.x, self.player.y, self.camera)

        # 전투 이펙트
        self.world_renderer.draw_combat_effects(game_surface)

        # 파티클
        self.game_particles.draw(game_surface, self.camera)

        # 낮밤 오버레이
        self.weather_system.draw_ambient(game_surface, self.time_system)

        # 날씨 효과
        self.weather_system.draw_effects(game_surface, 0)

        # UI (가장 위에)
        self.hud.draw(game_surface, self.player, self.time_system,
                     self.weather_system, self.current_day, self.total_days)

        # 이벤트 로그
        self.event_log_ui.draw(game_surface, self.event_system.event_log)

        # 인벤토리 / 크래프팅
        self.inventory_ui.draw(game_surface, self.player)
        self.crafting_ui.draw(game_surface, self.player)

        # 대화
        self.dialogue_ui.draw(game_surface)

        # 퀘스트 HUD
        self._draw_quest_hud(game_surface)

        # 상호작용 힌트
        self.world_renderer.draw_interaction_hint(game_surface)

    def _draw_interior_gameplay(self):
        """건물 내부 게임플레이 및 UI 렌더링"""
        if not self.player:
            self.screen.fill(Colors.BLACK)
            return

        self.world_renderer.draw_interior(self.screen)

        # UI (가장 위에)
        self.hud.draw(self.screen, self.player, self.time_system,
                     self.weather_system, self.current_day, self.total_days)

        # 이벤트 로그
        self.event_log_ui.draw(self.screen, self.event_system.event_log)

        # 인벤토리 / 크래프팅
        self.inventory_ui.draw(self.screen, self.player)
        self.crafting_ui.draw(self.screen, self.player)

        # 대화
        self.dialogue_ui.draw(self.screen)

        # 퀘스트 HUD
        self._draw_quest_hud(self.screen)

    def _draw_quest_hud(self, surface):
        """퀘스트 진행 상황 HUD 렌더링"""
        active_quests = []
        for npc in self.entity_manager.npcs:
            if npc.active and hasattr(npc, 'met') and npc.met and npc.quest_req[0] is not None:
                active_quests.append(npc)
        
        if not active_quests:
            return
            
        font = FontManager.get(10)
        start_x = self.screen_w - 240
        start_y = 60
        
        # 배경 그리기
        max_display = 3
        display_quests = active_quests[:max_display]
        panel_h = 30 + len(display_quests) * 16 + (20 if len(active_quests) > max_display else 0)
        
        bg = pygame.Surface((230, panel_h), pygame.SRCALPHA)
        bg.fill((15, 18, 25, 200))
        surface.blit(bg, (start_x - 10, start_y - 10))
        
        # 제목
        title_surf = FontManager.get(12).render("진행 중인 퀘스트", True, (255, 200, 100))
        surface.blit(title_surf, (start_x, start_y - 5))
        
        for i, npc in enumerate(display_quests):
            req_item, req_count = npc.quest_req
            has = self.player.inventory.count_item(req_item)
            
            if has >= req_count:
                color = (150, 255, 150)
                text = f"- {req_item} ({has}/{req_count}) [완료 가능]"
            else:
                color = (200, 200, 200)
                text = f"- {req_item} ({has}/{req_count})"
                
            text_surf = font.render(text, True, color)
            surface.blit(text_surf, (start_x, start_y + 18 + i * 16))
            
        if len(active_quests) > max_display:
            more_surf = font.render(f"...외 {len(active_quests) - max_display}개", True, (150, 150, 150))
            surface.blit(more_surf, (start_x, start_y + 18 + max_display * 16))


# ============================================================
# 엔트리포인트
# ============================================================
if __name__ == "__main__":
    game = Game()
    game.run()
