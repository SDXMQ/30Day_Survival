import random
import pygame
# pyrefly: ignore [missing-import]
from settings import Colors, TILE_SIZE
from items import ITEM_DATABASE
from sounds import SoundGenerator
from particles import ParticleEmitters
from i18n import t

class InteractionHandler:
    """게임 내 모든 상호작용(E키, NPC 거래, 퀘스트 등)을 담당하는 비즈니스 로직 핸들러"""
    def __init__(self, game):
        self.game = game

    def handle_interaction(self):
        """오버월드에서의 E키 상호작용"""
        if not self.game.player:
            return

        px, py = self.game.player.x, self.game.player.y

        # 바닥 아이템 줍기
        ground_items = self.game.world.get_ground_items_near(px, py, 1.5)
        for (item_name, ix, iy), chunk in ground_items:
            if self.game.player.inventory.add_item(item_name):
                chunk.items_on_ground.remove((item_name, ix, iy))
                self.game.event_system.add_log(f"'{item_name}'을(를) 획득했습니다!")
                SoundGenerator.play("pickup")
                self.game.game_particles.emit(
                    lambda: ParticleEmitters.pickup_sparkle(px * TILE_SIZE, py * TILE_SIZE), 5)
                return

        # NPC 대화
        npcs = self.game.entity_manager.get_nearby_npcs(px, py, 2.0)
        if npcs:
            npc = npcs[0]
            if npc.npc_type == "merchant":
                options = []
                for offer, want, count in npc.trade_items[:4]:
                    has = self.game.player.inventory.count_item(want)
                    if has >= count:
                        label = f"[가능] 획득: {offer}  |  지불: {want} x{count} (보유: {has})"
                    else:
                        label = f"[부족] 획득: {offer}  |  지불: {want} x{count} (보유: {has})"
                    options.append((label, f"trade_{offer}_{want}_{count}"))
                options.append(("거래 종료", "close"))
                self.game.dialogue_ui.show(
                    npc.name, npc.dialogue_intro, options,
                    on_select=lambda result: self.handle_trade(result)
                )
            elif npc.npc_type in ("soldier", "survivor"):
                if not getattr(npc, "met", False):
                    npc.met = True
                    self.game.event_system.add_log(f"★ 임무 등록: {npc.name}에게 {npc.quest_req[0]} {npc.quest_req[1]}개 전달")
                req_item, req_count = npc.quest_req
                reward_item, reward_count = npc.quest_reward
                has = self.game.player.inventory.count_item(req_item)
                
                if has >= req_count:
                    label = f"[완료 가능] 전달: {req_item} x{req_count}  |  보상: {reward_item} x{reward_count} (현재: {has})"
                else:
                    label = f"[진행 중] 필요: {req_item} x{req_count}  |  보상: {reward_item} x{reward_count} (현재: {has})"
                
                self.game.dialogue_ui.show(
                    npc.name,
                    f"이봐 생존자. {req_item} {req_count}개만 좀 가져다 주겠나? 댓가로 {reward_item} {reward_count}개를 주지. (필요: {req_item} {req_count}개 | 보상: {reward_item} {reward_count}개)",
                    [
                        (label, "complete_quest"),
                        ("나중에", "close")
                    ],
                    on_select=lambda r: self.handle_quest(npc, r)
                )
            else:
                self.game.dialogue_ui.show(npc.name, npc.dialogue_intro)
            return

        # 건물 진입 (문 앞에서 E키)
        buildings = self.game.world.get_nearby_buildings(int(px), int(py), 2)
        for building in buildings:
            if building.is_near_door(px, py):
                self.game._enter_building(building)
                return

        # 나무 채집
        objects = self.game.world.get_nearby_objects(int(px), int(py), 1.5)
        for obj in objects:
            if obj.obj_type.startswith("tree_") and not obj.looted:
                obj.looted = True
                self.game.player.inventory.add_item("나무", random.randint(1, 3))
                self.game.event_system.add_log("나무를 채집했습니다!")
                SoundGenerator.play("pickup")
                return
            elif obj.obj_type == "bush" and not obj.looted:
                obj.looted = True
                if random.random() < 0.5:
                    self.game.player.inventory.add_item("약초", 1)
                    self.game.event_system.add_log("약초를 발견했습니다!")
                else:
                    self.game.event_system.add_log("관목을 뒤졌지만 아무것도 없었습니다.")
                SoundGenerator.play("pickup")
                return

    def handle_trade(self, result):
        """상인 거래 처리"""
        if result == "close":
            return

        parts = result.split("_")
        if len(parts) >= 4 and parts[0] == "trade":
            offer = parts[1]
            want = parts[2]
            count = int(parts[3])
            if self.game.player.inventory.has_item(want, count):
                self.game.player.inventory.remove_item(want, count)
                self.game.player.inventory.add_item(offer)
                self.game.event_system.add_log(f"거래 완료: {want} x{count} → {offer}")
                SoundGenerator.play("pickup")
            else:
                self.game.event_system.add_log(f"{want}이(가) 부족합니다.")

    def handle_quest(self, npc, result):
        """NPC 퀘스트 완료 처리"""
        if result == "close":
            return

        if result == "complete_quest":
            req_item, req_count = npc.quest_req
            reward_item, reward_count = npc.quest_reward
            if self.game.player.inventory.has_item(req_item, req_count):
                self.game.player.inventory.remove_item(req_item, req_count)
                
                # 보상이 1개 이상 여러 개일 수 있으므로 반복 지급
                for _ in range(reward_count):
                    self.game.player.inventory.add_item(reward_item, 1)
                    
                self.game.event_system.add_log(f"임무 완료: {reward_item} x{reward_count} 획득")
                SoundGenerator.play("craft_complete")
                npc.active = False  # NPC 퇴장
            else:
                self.game.event_system.add_log(f"[{req_item}]이(가) 부족합니다.")

    def handle_interior_interaction(self):
        """건물 내부 E키 상호작용"""
        if not self.game.current_interior:
            return

        ix, iy = self.game.player.x, self.game.player.y

        # 바닥 아이템 줍기
        ground_items = self.game.current_interior.get_ground_items_near(ix, iy, 1.5)
        if ground_items:
            item_tuple = ground_items[0]
            item_name = item_tuple[0]
            if self.game.player.inventory.add_item(item_name):
                self.game.current_interior.items_on_ground.remove(item_tuple)
                self.game.event_system.add_log(f"'{item_name}'을(를) 획득했습니다!")
                SoundGenerator.play("pickup")
                self.game.game_particles.emit(
                    lambda: ParticleEmitters.pickup_sparkle(ix * TILE_SIZE, iy * TILE_SIZE), 5)
                return

        # 출구 확인
        if self.game.current_interior.is_at_exit(ix, iy):
            self.game._exit_building()
            return

        # 가구 탐색 및 상호작용
        furniture = self.game.current_interior.get_furniture_at(ix, iy, 1.5)
        if furniture:
            if furniture.type == "침대":
                # 수면 시스템
                current_hour = self.game.time_system.current_hour
                if 6 <= current_hour < 18:
                    self.game.event_system.add_log("낮에는 수면이 불가능합니다. (18:00 ~ 6:00 가능)")
                    SoundGenerator.play("error")
                else:
                    self.game.event_system.add_log("잠자리에 듭니다... (다음 날 아침 6시 됨)")
                    SoundGenerator.play("door_open")
                    
                    # 6시로 스킵
                    hours_to_skip = 24 - current_hour + 6 if current_hour >= 18 else 6 - current_hour
                    self.game.time_system.current_hour = 6.0
                    if current_hour >= 18:
                        self.game.time_system.current_day += 1

                    # 습격 밤이면 자동 방어 처리
                    if self.game.raid_active:
                        self.game._resolve_raid()

                    self.game.player.hp = min(self.game.player.max_hp, self.game.player.hp + 50)
                    self.game.player.stamina = self.game.player.max_stamina
                    self.game.player.hunger = max(0, self.game.player.hunger - 15)
                    self.game.player.thirst = max(0, self.game.player.thirst - 20)
                    self.game.player.stress = max(0, self.game.player.stress - 30)
                    
                    self.game.transition.start("fade", 1.5)
                return
            
            # 일반 가구 루팅
            if not furniture.searched:
                loot_quality = self.game.world_settings.get("resource_density", 1.0) if self.game.world_settings else 1.0
                found = furniture.search(loot_quality)
                if found:
                    droppedItems = False
                    for item_name in found:
                        if not self.game.player.inventory.add_item(item_name):
                            # 무게나 슬롯 초과 시 내부 바닥에 드롭
                            self.game.current_interior.drop_item(item_name, self.game.player.x, self.game.player.y)
                            droppedItems = True
                    items_str = ", ".join(found)
                    log_text = f"{t('found_items')}{items_str}"
                    if droppedItems: log_text += " (가방 꽉참: 바닥에 떨굼)"
                    self.game.event_system.add_log(log_text)
                    SoundGenerator.play("pickup")
                else:
                    self.game.event_system.add_log(t("found_nothing"))
                SoundGenerator.play("door_open")
                return
            else:
                self.game.event_system.add_log(t("searched_already"))
