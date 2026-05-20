"""
save_system.py - 세이브/로드 시스템
"""
import json
import os
import time
import random
from settings import (Colors, CHUNK_SIZE, DIFFICULTY_PRESETS, DEFAULT_WORLD_SETTINGS)
from camera import Camera
from world import World, WorldObject, Building
from player import Player
from entities import EntityManager, Zombie, NPC
from combat import CombatSystem
from weather import TimeSystem, WeatherSystem
from particles import ParticleSystem
from building_interior import BuildingInterior
from events import EventSystem

SAVE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saves")


def ensure_save_dir():
    os.makedirs(SAVE_DIR, exist_ok=True)


def get_save_files():
    """저장 파일 목록"""
    ensure_save_dir()
    saves = []
    for f in os.listdir(SAVE_DIR):
        if f.endswith(".json"):
            path = os.path.join(SAVE_DIR, f)
            try:
                with open(path, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                saves.append({
                    "filename": f,
                    "path": path,
                    "world_name": data.get("world_name", "알 수 없음"),
                    "day": data.get("current_day", 0),
                    "difficulty": data.get("difficulty", "보통"),
                    "save_time": data.get("save_time", ""),
                    "playtime": data.get("playtime", 0),
                })
            except Exception:
                continue
    saves.sort(key=lambda x: x.get("save_time", ""), reverse=True)
    return saves


def save_game(game_state, slot_name="autosave"):
    """게임 저장"""
    ensure_save_dir()
    filename = f"{slot_name}.json"
    path = os.path.join(SAVE_DIR, filename)
    tmp_path = path + ".tmp"

    game_state["save_time"] = time.strftime("%Y-%m-%d %H:%M:%S")

    try:
        # 1. 임시 파일에 쓰기
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(game_state, f, ensure_ascii=False, indent=2)
            # 2. 강제 동기화 (OS 캐시 문제 방어)
            f.flush()
            os.fsync(f.fileno())
            
        # 3. 원자적으로 원본 덮어쓰기
        os.replace(tmp_path, path)
        return True
    except Exception as e:
        print(f"저장 실패: {e}")
        # 실패 시 잔여 임시파일 정리 시도
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except:
                pass
        return False


def load_game(slot_name="autosave"):
    """게임 로드"""
    ensure_save_dir()
    filename = f"{slot_name}.json"
    path = os.path.join(SAVE_DIR, filename)

    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"로드 실패: {e}")
        return None


def delete_save(slot_name):
    """세이브 삭제"""
    ensure_save_dir()
    filename = f"{slot_name}.json"
    path = os.path.join(SAVE_DIR, filename)
    try:
        if os.path.exists(path):
            os.remove(path)
            return True
    except Exception:
        pass
    return False


class GameSaveManager:
    """게임 인스턴스의 모든 상태를 직렬화하고 복구하는 총괄 매니저"""

    @staticmethod
    def serialize_game(game):
        """게임의 모든 상태를 딕셔너리로 직렬화"""
        if not game.player or not game.world:
            return None

        # 1. 월드 오브젝트 및 빌딩 상태 델타 (변경된 것만 저장)
        world_deltas = []
        for (cx, cy), chunk in game.world.chunks.items():
            chunk_delta = {
                "cx": cx,
                "cy": cy,
                "objects": [],
                "buildings": [],
                "items": chunk.items_on_ground.copy()
            }
            has_changes = len(chunk.items_on_ground) > 0

            for obj in chunk.objects:
                if obj.looted or obj.hp < 30:
                    chunk_delta["objects"].append({
                        "x": obj.x, "y": obj.y, "type": obj.obj_type,
                        "looted": obj.looted, "hp": obj.hp
                    })
                    has_changes = True

            for b in chunk.buildings:
                if b.explored:
                    chunk_delta["buildings"].append({
                        "x": b.x, "y": b.y, "type": b.building_type,
                        "explored": b.explored
                    })
                    has_changes = True

            if has_changes:
                world_deltas.append(chunk_delta)

        # 이미 언로드되어 델타만 남은 청크도 세이브에 포함
        for (cx, cy), delta in game.world.unloaded_deltas.items():
            world_deltas.append({
                "cx": cx, "cy": cy,
                "objects": delta.get("objects", []),
                "buildings": delta.get("buildings", []),
                "items": delta.get("items", []),
            })

        # 2. 엔티티 상태
        entities_data = {
            "zombies": [z.to_dict() for z in game.entity_manager.zombies if z.active],
            "npcs": [n.to_dict() for n in game.entity_manager.npcs if n.active],
        }

        # 3. 탐색 완료한 건물 내부 상태
        interior_deltas = {}
        for bid, interior in game.explored_interiors.items():
            interior_deltas[bid] = interior.to_dict()

        return {
            "world_settings": game.world_settings,
            "player": game.player.to_dict(),
            "current_day": game.current_day,
            "current_hour": game.time_system.current_hour,
            "playtime": game.playtime,
            "world_name": game.world_settings.get("world_name", "월드 1"),
            "difficulty": game.world_settings.get("difficulty", "보통"),
            "world_deltas": world_deltas,
            "entities": entities_data,
            "interior_deltas": interior_deltas,
        }

    @staticmethod
    def deserialize_game(game, data):
        """딕셔너리 데이터를 기반으로 게임 인스턴스 복구"""
        if not data:
            return False

        game.world_settings = data.get("world_settings", DEFAULT_WORLD_SETTINGS)
        diff_name = game.world_settings.get("difficulty", "보통")
        game.difficulty = DIFFICULTY_PRESETS.get(diff_name, DIFFICULTY_PRESETS["보통"])
        game.total_days = game.world_settings.get("total_days", 30)

        # 월드 및 카메라 로드
        game.world = World(seed=game.world_settings.get("seed"), world_settings=game.world_settings)
        game.player = Player.from_dict(data.get("player", {}), game.difficulty)

        game.camera = Camera()
        game.camera.resize(game.screen_w, game.screen_h)
        game.entity_manager = EntityManager(game.difficulty)
        
        # 시스템 복원
        day_len = game.world_settings.get("day_length_minutes", 12)
        game.time_system = TimeSystem(day_len)
        game.time_system.current_day = data.get("current_day", 1)
        game.time_system.current_hour = data.get("current_hour", 8.0)
        
        weather_var = game.world_settings.get("weather_variability", 1.0)
        game.weather_system = WeatherSystem(weather_var)
        game.event_system = EventSystem(game.difficulty)
        game.combat_system = CombatSystem()
        game.game_particles = ParticleSystem()

        game.current_day = data.get("current_day", 1)
        game.last_day = game.current_day
        game.playtime = data.get("playtime", 0)

        # 월드 상태 델타 복구 (lazy: unloaded_deltas에 보존, 접근 시 적용)
        world_deltas = data.get("world_deltas", [])
        px = game.player.x
        py = game.player.y
        pcx = int(px) // CHUNK_SIZE
        pcy = int(py) // CHUNK_SIZE

        for delta in world_deltas:
            cx, cy = delta["cx"], delta["cy"]
            compact_delta = {}
            if delta.get("objects"):
                compact_delta["objects"] = delta["objects"]
            if delta.get("buildings"):
                compact_delta["buildings"] = delta["buildings"]
            if delta.get("items"):
                compact_delta["items"] = delta["items"]
            if not compact_delta:
                continue

            # 플레이어 근처 청크만 즉시 로드, 나머지는 lazy
            if abs(cx - pcx) <= 5 and abs(cy - pcy) <= 5:
                chunk = game.world.get_chunk(cx, cy)
                game.world._apply_delta(chunk, compact_delta)
            else:
                game.world.unloaded_deltas[(cx, cy)] = compact_delta

        # 엔티티 복구
        entities_data = data.get("entities", {})
        game.entity_manager.zombies = []
        for zdict in entities_data.get("zombies", []):
            game.entity_manager.zombies.append(Zombie.from_dict(zdict))
            
        game.entity_manager.npcs = []
        for ndict in entities_data.get("npcs", []):
            game.entity_manager.npcs.append(NPC.from_dict(ndict))

        # 건물 내부 델타 복구
        game.explored_interiors = {}
        interior_deltas = data.get("interior_deltas", {})
        for bid, idata in interior_deltas.items():
            ext_w = idata.get("width", 8) // 2
            ext_h = idata.get("height", 8) // 2
            game.explored_interiors[bid] = BuildingInterior.from_dict(idata, ext_w, ext_h)

        return True
