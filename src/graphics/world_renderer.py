import pygame
import math
import time as pytime
from settings import Colors, TILE_SIZE, CHUNK_SIZE
from renderer import TileRenderer, CharacterRenderer, EnvironmentRenderer, BuildingRenderer, ItemIconRenderer
from items import ITEM_DATABASE
from ui import FontManager
from i18n import t

class WorldSceneRenderer:
    """오버월드 및 인게임 씬 전체 렌더링을 돕는 렌더러 클래스"""
    def __init__(self, game):
        self.game = game

    def draw_tiles(self, surface):
        x1, y1, x2, y2 = self.game.camera.get_visible_area()

        cx1 = x1 // CHUNK_SIZE
        cx2 = x2 // CHUNK_SIZE
        cy1 = y1 // CHUNK_SIZE
        cy2 = y2 // CHUNK_SIZE

        for cy in range(cy1, cy2 + 1):
            for cx in range(cx1, cx2 + 1):
                chunk = self.game.world.get_chunk(cx, cy)

                if chunk.surface is None or chunk.dirty:
                    chunk_px_size = CHUNK_SIZE * TILE_SIZE
                    chunk.surface = pygame.Surface((chunk_px_size, chunk_px_size)).convert()

                    for ly in range(CHUNK_SIZE):
                        for lx in range(CHUNK_SIZE):
                            wx = cx * CHUNK_SIZE + lx
                            wy = cy * CHUNK_SIZE + ly
                            tile_type = chunk.get_tile(lx, ly)
                            variant = (wx * 7 + wy * 13) % 4
                            tile_surf = TileRenderer.get_tile(tile_type, variant)
                            chunk.surface.blit(tile_surf, (lx * TILE_SIZE, ly * TILE_SIZE))

                    chunk.dirty = False

                sx, sy_pos = self.game.camera.world_to_screen(cx * CHUNK_SIZE, cy * CHUNK_SIZE)
                surface.blit(chunk.surface, (sx, sy_pos))

    def draw_ground_items(self, surface):
        x1, y1, x2, y2 = self.game.camera.get_visible_area()

        for cy in range(y1 // CHUNK_SIZE - 1, y2 // CHUNK_SIZE + 2):
            for cx in range(x1 // CHUNK_SIZE - 1, x2 // CHUNK_SIZE + 2):
                chunk = self.game.world.chunks.get((cx, cy))
                if not chunk:
                    continue
                for item_name, ix, iy in chunk.items_on_ground:
                    sx, sy = self.game.camera.world_to_screen(ix, iy)
                    if -32 <= sx <= self.game.screen_w + 32 and -32 <= sy <= self.game.screen_h + 32:
                        icon = ItemIconRenderer.get_icon(item_name)
                        bounce = math.sin(pytime.time() * 3 + ix + iy) * 3
                        surface.blit(icon, (sx + 4, sy + 4 + int(bounce)))

    def draw_environment(self, surface):
        x1, y1, x2, y2 = self.game.camera.get_visible_area()

        for cy in range(y1 // CHUNK_SIZE - 1, y2 // CHUNK_SIZE + 2):
            for cx in range(x1 // CHUNK_SIZE - 1, x2 // CHUNK_SIZE + 2):
                chunk = self.game.world.chunks.get((cx, cy))
                if not chunk:
                    continue
                for obj in chunk.objects:
                    if not (x1 - 2 <= obj.x <= x2 + 2 and y1 - 2 <= obj.y <= y2 + 2):
                        continue

                    sx, sy = self.game.camera.world_to_screen(obj.x, obj.y)

                    if obj.obj_type.startswith("tree_"):
                        if getattr(obj, "looted", False):
                            sprite = EnvironmentRenderer.get_stump(obj.variant)
                            surface.blit(sprite, (sx - sprite.get_width() // 2,
                                                sy - sprite.get_height() + TILE_SIZE // 2))
                        else:
                            tree_type = obj.obj_type.replace("tree_", "")
                            sprite = EnvironmentRenderer.get_tree(tree_type, obj.variant)
                            surface.blit(sprite, (sx - sprite.get_width() // 2,
                                                sy - sprite.get_height() + TILE_SIZE // 2))
                    elif obj.obj_type == "rock":
                        sprite = EnvironmentRenderer.get_rock(obj.variant)
                        surface.blit(sprite, (sx, sy))
                    elif obj.obj_type == "bush":
                        sprite = EnvironmentRenderer.get_bush(obj.variant)
                        surface.blit(sprite, (sx, sy))

    def draw_buildings(self, surface):
        x1, y1, x2, y2 = self.game.camera.get_visible_area()

        for cy in range(y1 // CHUNK_SIZE - 1, y2 // CHUNK_SIZE + 2):
            for cx in range(x1 // CHUNK_SIZE - 1, x2 // CHUNK_SIZE + 2):
                chunk = self.game.world.chunks.get((cx, cy))
                if not chunk:
                    continue
                for building in chunk.buildings:
                    bx = building.x
                    by = building.y
                    if not (x1 - 5 <= bx <= x2 + 5 and y1 - 5 <= by <= y2 + 5):
                        continue

                    sprite = BuildingRenderer.get_building(
                        building.building_type, building.width, building.height, building.variant
                    )
                    sx, sy = self.game.camera.world_to_screen(bx, by)
                    surface.blit(sprite, (sx, sy))

                    if building.explored:
                        font = FontManager.get(10)
                        mark = font.render("✓", True, Colors.UI_SUCCESS)
                        surface.blit(mark, (sx + 2, sy + 2))

    def draw_entities(self, surface):
        for zombie in self.game.entity_manager.zombies:
            if not zombie.active:
                continue
            if not self.game.camera.is_visible(zombie.x, zombie.y):
                continue

            sx, sy = self.game.camera.world_to_screen(zombie.x, zombie.y)
            sprite = CharacterRenderer.get_zombie_sprite(
                zombie.zombie_type, zombie.direction, zombie.animation_frame
            )

            if zombie.state == "hurt" and int(zombie.hurt_timer * 10) % 2:
                sprite = sprite.copy()
                sprite.fill((255, 100, 100, 128), special_flags=pygame.BLEND_RGBA_MULT)

            surface.blit(sprite, (sx, sy))

            if zombie.hp < zombie.max_hp:
                bar_w = TILE_SIZE
                bar_h = 3
                ratio = zombie.hp / zombie.max_hp
                pygame.draw.rect(surface, (40, 40, 45), (sx, sy - 5, bar_w, bar_h))
                pygame.draw.rect(surface, (220, 50, 50), (sx, sy - 5, int(bar_w * ratio), bar_h))

            # 총성 어그로 느낌표
            if zombie.aggro_alert > 0:
                alert_font = FontManager.get(14)
                alert_surf = alert_font.render("!", True, (255, 50, 50))
                bounce = math.sin(pytime.time() * 8) * 2
                surface.blit(alert_surf, (sx + TILE_SIZE // 2 - alert_surf.get_width() // 2,
                                          sy - 15 + int(bounce)))

        for npc in self.game.entity_manager.npcs:
            if not npc.active:
                continue
            if not self.game.camera.is_visible(npc.x, npc.y):
                continue

            sx, sy = self.game.camera.world_to_screen(npc.x, npc.y)
            sprite = CharacterRenderer.get_npc_sprite(
                npc.npc_type, npc.direction, npc.animation_frame
            )
            surface.blit(sprite, (sx, sy))

            font = FontManager.get(10)
            name_surf = font.render(npc.name, True, Colors.UI_ACCENT_WARM)
            surface.blit(name_surf, (sx + TILE_SIZE // 2 - name_surf.get_width() // 2, sy - 12))

    def draw_player(self, surface):
        sx, sy = self.game.camera.world_to_screen(self.game.player.x, self.game.player.y)
        has_weapon = self.game.player.equipped.get("weapon") is not None
        sprite = CharacterRenderer.get_player_sprite(
            self.game.player.direction, self.game.player.animation_frame, has_weapon, self.game.player.is_crouching
        )

        if self.game.player.invincible_timer > 0 and int(self.game.player.invincible_timer * 10) % 2:
            sprite = sprite.copy()
            sprite.set_alpha(128)

        surface.blit(sprite, (sx, sy))

    def draw_aim_indicator(self, surface, px, py, camera):
        if self.game.inventory_ui.visible or self.game.crafting_ui.visible or self.game.dialogue_ui.visible:
            return

        weapon = self.game.player.equipped.get("weapon")
        weapon_data = ITEM_DATABASE.get(weapon, {}) if weapon else {}
        weapon_type = weapon_data.get("type", "melee")
        attack_range = self.game.player.get_attack_range()

        mouse_sx, mouse_sy = pygame.mouse.get_pos()
        mouse_wx, mouse_wy = camera.screen_to_world(mouse_sx, mouse_sy)
        
        center_x = px + 0.5
        center_y = py + 0.5
        
        attack_angle = math.atan2(mouse_wy - center_y, mouse_wx - center_x)
        psx, psy = camera.world_to_screen(center_x, center_y)
        
        radius = int(attack_range * TILE_SIZE * camera.zoom)
        indicator_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        center = (radius, radius)
        
        points = [center]
        steps = 10
        if weapon_type == "melee":
            start_angle = attack_angle - math.pi / 6
            end_angle = attack_angle + math.pi / 6
            for i in range(steps + 1):
                ang = start_angle + (end_angle - start_angle) * i / steps
                dx = math.cos(ang) * radius
                dy = math.sin(ang) * radius
                points.append((radius + dx, radius + dy))
            pygame.draw.polygon(indicator_surf, (255, 100, 100, 30), points)
            pygame.draw.polygon(indicator_surf, (255, 50, 50, 80), points, 1)
        else:
            start_angle = attack_angle - math.pi / 12
            end_angle = attack_angle + math.pi / 12
            for i in range(steps + 1):
                ang = start_angle + (end_angle - start_angle) * i / steps
                dx = math.cos(ang) * radius
                dy = math.sin(ang) * radius
                points.append((radius + dx, radius + dy))
            pygame.draw.polygon(indicator_surf, (100, 255, 100, 30), points)
            pygame.draw.polygon(indicator_surf, (50, 255, 50, 80), points, 1)
            
            end_x = psx + math.cos(attack_angle) * radius
            end_y = psy + math.sin(attack_angle) * radius
            pygame.draw.line(surface, (255, 0, 0, 150), (psx, psy), (end_x, end_y), 1)

        surface.blit(indicator_surf, (psx - radius, psy - radius))

    def draw_combat_effects(self, surface, camera=None):
        cam = camera or self.game.camera
        font = FontManager.get(14)

        for x, y, dmg, timer, color in self.game.combat_system.get_damage_numbers():
            sx, sy = cam.world_to_screen(x, y)
            alpha = max(0, min(255, int(255 * min(1, timer))))
            dmg_surf = font.render(str(int(dmg)), True, color)
            dmg_surf.set_alpha(alpha)
            surface.blit(dmg_surf, (sx, sy))

    def draw_interaction_hint(self, surface):
        if not self.game.player:
            return
        if self.game.inventory_ui.visible or self.game.crafting_ui.visible or self.game.dialogue_ui.visible:
            return

        px, py = self.game.player.x, self.game.player.y
        hint_text = None

        ground_items = self.game.world.get_ground_items_near(px, py, 1.5)
        if ground_items:
            item_name = ground_items[0][0][0]
            hint_text = f"[E] {item_name} 줍기"

        if not hint_text:
            npcs = self.game.entity_manager.get_nearby_npcs(px, py, 2.0)
            if npcs:
                hint_text = f"[E] {npcs[0].name}과 대화"

        if not hint_text:
            buildings = self.game.world.get_nearby_buildings(int(px), int(py), 2)
            for b in buildings:
                if b.is_near_door(px, py):
                    hint_text = t("press_e_enter")
                    break

        if not hint_text:
            objects = self.game.world.get_nearby_objects(int(px), int(py), 1.5)
            for obj in objects:
                if obj.obj_type.startswith("tree_") and not obj.looted:
                    hint_text = "[E] 나무 채집"
                    break
                elif obj.obj_type == "bush" and not obj.looted:
                    hint_text = "[E] 관목 조사"
                    break

        if hint_text:
            font = FontManager.get(13)
            text_surf = font.render(hint_text, True, Colors.UI_ACCENT)
            tw = text_surf.get_width()
            tx = (self.game.screen_w - tw) // 2
            ty = self.game.screen_h // 2 + 60

            bg = pygame.Surface((tw + 16, 24), pygame.SRCALPHA)
            pygame.draw.rect(bg, (15, 18, 28, 180), (0, 0, tw + 16, 24), border_radius=6)
            surface.blit(bg, (tx - 8, ty - 3))
            surface.blit(text_surf, (tx, ty))

    def draw_interior(self, surface):
        """건물 내부 렌더링"""
        if not self.game.current_interior or not self.game.interior_camera:
            return

        surface.fill((20, 18, 25))

        interior = self.game.current_interior
        cam = self.game.interior_camera

        # 타일 그리기
        for ty in range(interior.height):
            for tx in range(interior.width):
                tile = interior.get_tile(tx, ty)
                sx, sy = cam.world_to_screen(tx, ty)

                if sx < -TILE_SIZE or sx > self.game.screen_w + TILE_SIZE:
                    continue
                if sy < -TILE_SIZE or sy > self.game.screen_h + TILE_SIZE:
                    continue

                if tile == "wall":
                    pygame.draw.rect(surface, (55, 50, 60),
                                    (sx, sy, TILE_SIZE, TILE_SIZE))
                    pygame.draw.rect(surface, (70, 65, 75),
                                    (sx, sy, TILE_SIZE, TILE_SIZE), 1)
                elif tile == "floor":
                    color = Colors.FLOOR_WOOD if (tx + ty) % 2 == 0 else (145, 108, 65)
                    pygame.draw.rect(surface, color,
                                    (sx, sy, TILE_SIZE, TILE_SIZE))
                elif tile == "door":
                    pygame.draw.rect(surface, Colors.DOOR,
                                    (sx, sy, TILE_SIZE, TILE_SIZE))
                    # 출구 표시
                    font = FontManager.get(10)
                    exit_text = font.render("출구", True, (255, 255, 200))
                    surface.blit(exit_text, (sx + 4, sy + 10))
                elif tile == "furniture":
                    pygame.draw.rect(surface, Colors.FLOOR_WOOD,
                                    (sx, sy, TILE_SIZE, TILE_SIZE))
                elif tile == "window":
                    # 창문 타일: 벽 배경 + 반투명 파란 유리 + 십자 격자
                    pygame.draw.rect(surface, (55, 50, 60),
                                    (sx, sy, TILE_SIZE, TILE_SIZE))
                    win_surf = pygame.Surface((TILE_SIZE - 4, TILE_SIZE - 4), pygame.SRCALPHA)
                    win_surf.fill((120, 180, 220, 100))
                    surface.blit(win_surf, (sx + 2, sy + 2))
                    # 십자 격자
                    pygame.draw.line(surface, (80, 75, 85), (sx + TILE_SIZE // 2, sy + 2), (sx + TILE_SIZE // 2, sy + TILE_SIZE - 2), 1)
                    pygame.draw.line(surface, (80, 75, 85), (sx + 2, sy + TILE_SIZE // 2), (sx + TILE_SIZE - 2, sy + TILE_SIZE // 2), 1)
                    pygame.draw.rect(surface, (90, 85, 95), (sx, sy, TILE_SIZE, TILE_SIZE), 1)

        # 가구 그리기
        for furn in interior.furniture:
            sx, sy = cam.world_to_screen(furn.x, furn.y)

            if furn.searched:
                color = (80, 75, 70)
                border = (60, 55, 50)
            else:
                color = (120, 90, 55)
                border = (160, 120, 70)

            pygame.draw.rect(surface, color, (sx + 2, sy + 2, TILE_SIZE - 4, TILE_SIZE - 4), border_radius=3)
            pygame.draw.rect(surface, border, (sx + 2, sy + 2, TILE_SIZE - 4, TILE_SIZE - 4), 1, border_radius=3)

            # 가구 이름
            font = FontManager.get(8)
            name_surf = font.render(furn.type, True, (200, 200, 200) if not furn.searched else (100, 100, 100))
            surface.blit(name_surf, (sx + 2, sy + TILE_SIZE - 12))

        # 내부 바닥 아이템 그리기
        for item_name, ix, iy in interior.items_on_ground:
            isx, isy = cam.world_to_screen(ix, iy)
            icon = ItemIconRenderer.get_icon(item_name)
            bounce = math.sin(pytime.time() * 3 + ix + iy) * 3
            surface.blit(icon, (isx + 4, isy + 4 + int(bounce)))

        # 내부 좀비 그리기
        for z in self.game.interior_zombies:
            if z.active and not z.is_dead:
                zsx, zsy = cam.world_to_screen(z.x, z.y)
                sprite = CharacterRenderer.get_zombie_sprite(z.zombie_type, z.direction, z.animation_frame)
                
                # 피격 시 깜빡임
                if z.state == "hurt" and int(z.hurt_timer * 10) % 2:
                    sprite = sprite.copy()
                    sprite.fill((255, 100, 100, 128), special_flags=pygame.BLEND_RGBA_MULT)
                    
                surface.blit(sprite, (zsx, zsy))
                
                # 체력바
                if z.hp < z.max_hp:
                    bar_w = TILE_SIZE
                    bar_h = 3
                    ratio = z.hp / z.max_hp
                    pygame.draw.rect(surface, (40, 40, 45), (zsx, zsy - 5, bar_w, bar_h))
                    pygame.draw.rect(surface, (220, 50, 50), (zsx, zsy - 5, int(bar_w * ratio), bar_h))

                # 총성 어그로 느낌표
                if z.aggro_alert > 0:
                    alert_font = FontManager.get(14)
                    alert_surf = alert_font.render("!", True, (255, 50, 50))
                    bounce = math.sin(pytime.time() * 8) * 2
                    surface.blit(alert_surf, (zsx + TILE_SIZE // 2 - alert_surf.get_width() // 2,
                                              zsy - 15 + int(bounce)))

        # 전투 이펙트 및 파티클
        self.draw_combat_effects(surface, cam)
        self.game.game_particles.draw(surface, cam)

        # 플레이어 그리기
        psx, psy = cam.world_to_screen(self.game.player.x, self.game.player.y)
        player_sprite = CharacterRenderer.get_player_sprite(
            self.game.player.direction, self.game.player.animation_frame, self.game.player.is_sprinting, self.game.player.is_crouching
        )
        surface.blit(player_sprite, (psx, psy))
        self.draw_aim_indicator(surface, self.game.player.x, self.game.player.y, cam)

        # 창문 시야 오버레이 및 실외 렌더링
        window_vision = getattr(self.game, 'window_vision', None)
        if window_vision:
            win = window_vision["win"]
            wsx, wsy = cam.world_to_screen(win["x"], win["y"])

            win_angle = math.atan2(window_vision["dir_y"], window_vision["dir_x"])
            cone_range = window_vision["range"] * TILE_SIZE
            half_fov = math.pi / 6  # 30도

            cx = wsx + TILE_SIZE // 2
            cy = wsy + TILE_SIZE // 2

            # --- 실외 풍경 실제 렌더링 ---
            ext_cam = self.game.camera
            old_x, old_y = ext_cam.x, ext_cam.y

            wx = window_vision["world_x"]
            wy = window_vision["world_y"]
            ext_cam.x = wx * TILE_SIZE - cx / ext_cam.zoom
            ext_cam.y = wy * TILE_SIZE - cy / ext_cam.zoom

            ext_surf = pygame.Surface((self.game.screen_w, self.game.screen_h), pygame.SRCALPHA)

            self.draw_tiles(ext_surf)
            self.draw_ground_items(ext_surf)
            self.draw_environment(ext_surf)
            self.draw_buildings(ext_surf)
            self.draw_entities(ext_surf)

            ext_cam.x, ext_cam.y = old_x, old_y

            # 부채꼴 마스크 생성
            mask_surf = pygame.Surface((self.game.screen_w, self.game.screen_h), pygame.SRCALPHA)
            num_points = 12
            points = [(cx, cy)]
            for i in range(num_points + 1):
                a = win_angle - half_fov + (2 * half_fov * i / num_points)
                px = cx + math.cos(a) * cone_range
                py = cy + math.sin(a) * cone_range
                points.append((int(px), int(py)))

            if len(points) >= 3:
                # 마스크: 부채꼴 영역은 흰색(완전 불투명)
                pygame.draw.polygon(mask_surf, (255, 255, 255, 255), points)
                # 실외 서피스에 마스크 적용
                ext_surf.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                # 최종 화면에 블릿
                surface.blit(ext_surf, (0, 0))
                
                # 푸른빛 오버레이 테두리 (알파 블렌딩을 위해 임시 서피스 사용)
                overlay_surf = pygame.Surface((self.game.screen_w, self.game.screen_h), pygame.SRCALPHA)
                pygame.draw.polygon(overlay_surf, (120, 200, 255, 35), points)
                pygame.draw.polygon(overlay_surf, (120, 200, 255, 60), points, 2)
                surface.blit(overlay_surf, (0, 0))

            # 좀비 수 표시 (실외 렌더링 위에)
            visible_zombies = window_vision.get("zombies", [])
            if visible_zombies:
                count_font = FontManager.get(10)
                count_text = count_font.render(f"외부 좀비: {len(visible_zombies)}", True, (255, 200, 100))
                surface.blit(count_text, (wsx - 10, wsy - 18))

        # 상호작용 힌트 (건물 내부용)
        ix, iy = self.game.player.x, self.game.player.y
        font = FontManager.get(12)
        hint_text = None

        if interior.is_at_exit(ix, iy):
            hint_text = t("press_e_exit")
        else:
            furn = interior.get_unsearched_furniture_near(ix, iy, 1.5)
            if furn:
                hint_text = f"{t('press_e_search')} [{furn.type}]"
            else:
                searched = interior.get_furniture_at(ix, iy, 1.5)
                if searched and searched.searched:
                    hint_text = t("searched_already")

        if hint_text:
            hint_surf = font.render(hint_text, True, Colors.UI_ACCENT)
            hx = (self.game.screen_w - hint_surf.get_width()) // 2
            hy = self.game.screen_h - 80
            bg = pygame.Surface((hint_surf.get_width() + 16, 24), pygame.SRCALPHA)
            bg.fill((10, 12, 20, 160))
            surface.blit(bg, (hx - 8, hy - 4))
            surface.blit(hint_surf, (hx, hy))

