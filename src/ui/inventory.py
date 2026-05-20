import pygame
import math
from settings import Colors, RESOLUTION_OPTIONS, DIFFICULTY_PRESETS, DEFAULT_WORLD_SETTINGS, GameSettings, TILE_SIZE
from renderer import draw_rounded_rect, draw_gradient_rect, draw_glow, ItemIconRenderer
from items import ITEM_DATABASE, ItemCategory
from crafting import CRAFTING_RECIPES, RECIPE_CATEGORIES
from utils import wrap_text, ease_out_cubic, lerp
from .fonts import FontManager
from i18n import t


class InventoryUI:
    """인벤토리 화면 (드래그 앤 드롭 지원)"""

    def __init__(self, screen_w, screen_h):
        self.sw = screen_w
        self.sh = screen_h
        self.visible = False
        self.selected_slot = -1
        self.hover_slot = -1
        self.hover_equip = None
        self.scroll_offset = 0
        self.animation_progress = 0
        
        # 드래그 앤 드롭 상태
        self.dragging = False
        self.drag_source_type = None  # 'inventory' or 'equip'
        self.drag_source_index = None # slot index or equip part name
        self.drag_item_name = None
        self.drag_mouse_pos = (0, 0)

    def toggle(self):
        self.visible = not self.visible
        self.animation_progress = 0
        self.selected_slot = -1
        self.dragging = False

    def update(self, dt):
        if self.visible and self.animation_progress < 1:
            self.animation_progress = min(1, self.animation_progress + dt * 5)

    def handle_event(self, event, player):
        if not self.visible:
            return None

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            inv_slot = self._get_slot_at(mx, my)
            eq_slot = self._get_equip_slot_at(mx, my)

            if event.button == 1:  # 좌클릭 - 드래그 시작 또는 사용
                if inv_slot is not None and inv_slot < len(player.inventory.items):
                    self.dragging = True
                    self.drag_source_type = 'inventory'
                    self.drag_source_index = inv_slot
                    self.drag_item_name = player.inventory.items[inv_slot][0]
                    self.drag_mouse_pos = (mx, my)
                elif eq_slot is not None and player.equipped.get(eq_slot):
                    self.dragging = True
                    self.drag_source_type = 'equip'
                    self.drag_source_index = eq_slot
                    self.drag_item_name = player.equipped[eq_slot]
                    self.drag_mouse_pos = (mx, my)

            elif event.button == 3:  # 우클릭 - 아이템 버리기 (Drop)
                if inv_slot is not None and inv_slot < len(player.inventory.items):
                    item_name = player.inventory.items[inv_slot][0]
                    return ("drop_item", item_name)

        elif event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            self.hover_slot = self._get_slot_at(mx, my)
            self.hover_equip = self._get_equip_slot_at(mx, my)
            if self.dragging:
                self.drag_mouse_pos = (mx, my)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.dragging:
                mx, my = event.pos
                inv_slot = self._get_slot_at(mx, my)
                eq_slot = self._get_equip_slot_at(mx, my)
                
                result = None
                # 드래그 종료 처리
                if self.drag_source_type == 'inventory':
                    # 인벤토리 -> 장비창으로 드롭 (장착)
                    if eq_slot is not None:
                        result = ("equip", self.drag_item_name)
                    # 드래그를 거의 안했으면 (클릭으로 간주) -> 아이템 사용
                    elif math.hypot(mx - self.drag_mouse_pos[0], my - self.drag_mouse_pos[1]) < 10 and inv_slot == self.drag_source_index:
                        result = ("use", self.drag_item_name)
                        
                elif self.drag_source_type == 'equip':
                    # 장비창 -> 인벤토리(또는 빈 공간)로 드롭 (해제)
                    if inv_slot is not None or (eq_slot is None):
                        result = ("unequip", self.drag_source_index) # slot name e.g. 'weapon'
                        
                self.dragging = False
                self.drag_source_type = None
                self.drag_source_index = None
                self.drag_item_name = None
                return result

        return None

    def _get_panel_rects(self):
        t_val = ease_out_cubic(self.animation_progress)
        cols = 6
        slot_size = 48
        gap = 6
        inv_w = cols * (slot_size + gap) + gap + 20
        panel_h = 380
        
        # 전체 패널 너비 = 장비 패널(80) + 인벤토리 패널
        eq_w = 80
        total_w = inv_w + 10 + eq_w
        
        px = (self.sw - total_w) // 2
        py = int((self.sh - panel_h) / 2 + (1 - t_val) * 30)
        
        return px, py, eq_w, inv_w, panel_h, slot_size, gap, cols

    def _get_slot_at(self, mx, my):
        px, py, eq_w, inv_w, panel_h, slot_size, gap, cols = self._get_panel_rects()
        inv_px = px + eq_w + 10
        
        for i in range(24):
            row, col = divmod(i, cols)
            sx = inv_px + 10 + col * (slot_size + gap) + gap
            sy = py + 40 + row * (slot_size + gap) + gap
            if sx <= mx <= sx + slot_size and sy <= my <= sy + slot_size:
                return i
        return None

    def _get_equip_slot_at(self, mx, my):
        px, py, eq_w, inv_w, panel_h, slot_size, gap, cols = self._get_panel_rects()
        slots = ["head", "body", "feet", "weapon"]
        for i, slot in enumerate(slots):
            sx = px + 16
            sy = py + 40 + i * (slot_size + gap + 10)
            if sx <= mx <= sx + slot_size and sy <= my <= sy + slot_size:
                return slot
        return None

    def draw(self, surface, player):
        if not self.visible:
            return

        t_val = ease_out_cubic(self.animation_progress)
        overlay = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(120 * t_val)))
        surface.blit(overlay, (0, 0))

        px, py, eq_w, inv_w, panel_h, slot_size, gap, cols = self._get_panel_rects()
        inv_px = px + eq_w + 10

        # 장비 패널
        draw_rounded_rect(surface, (20, 22, 35, int(230 * t_val)), (px, py, eq_w, panel_h), radius=12)
        draw_rounded_rect(surface, Colors.UI_BORDER + (int(150 * t_val),), (px, py, eq_w, panel_h), radius=12)
        
        # 인벤토리 패널
        draw_rounded_rect(surface, (20, 22, 35, int(230 * t_val)), (inv_px, py, inv_w, panel_h), radius=12)
        draw_rounded_rect(surface, Colors.UI_BORDER + (int(150 * t_val),), (inv_px, py, inv_w, panel_h), radius=12)

        font_title = FontManager.get(18)
        font_small = FontManager.get(11)
        font_count = FontManager.get(10)

        # 타이틀
        title = font_title.render(t("inventory"), True, Colors.UI_ACCENT)
        surface.blit(title, (inv_px + 15, py + 10))
        
        eq_title = font_small.render(t("equipment"), True, Colors.UI_ACCENT)
        surface.blit(eq_title, (px + 25, py + 15))

        # 무게
        weight_label = t("weight")
        weight_text = font_small.render(
            f"{weight_label}: {player.inventory.current_weight:.1f} / {player.inventory.max_weight:.1f} kg",
            True, Colors.UI_TEXT_DIM if player.inventory.current_weight <= player.inventory.max_weight * 0.8 else (255, 100, 100)
        )
        surface.blit(weight_text, (inv_px + inv_w - weight_text.get_width() - 15, py + 15))

        # 장비 슬롯 그리기
        eq_labels = {"head": t("equip_head"), "body": t("equip_body"), "feet": t("equip_feet"), "weapon": t("equip_weapon")}
        slots = ["head", "body", "feet", "weapon"]
        for i, eq_slot in enumerate(slots):
            sx = px + 16
            sy = py + 40 + i * (slot_size + gap + 10)
            
            is_hover = eq_slot == self.hover_equip
            bg_color = (60, 65, 80, 200) if is_hover else (35, 38, 50, 180)
            draw_rounded_rect(surface, bg_color, (sx, sy, slot_size, slot_size), radius=4)
            
            # 라벨
            lbl = font_small.render(eq_labels[eq_slot], True, Colors.UI_TEXT_DIM)
            surface.blit(lbl, (sx + (slot_size - lbl.get_width())//2, sy - 15))
            
            # 장착된 아이템
            item_name = player.equipped.get(eq_slot)
            if item_name:
                # 드래그 중인 아이템은 반투명하게 표시
                is_dragged = self.dragging and self.drag_source_type == 'equip' and self.drag_source_index == eq_slot
                if not is_dragged:
                    icon = ItemIconRenderer.get_icon(item_name)
                    surface.blit(icon, (sx + (slot_size - icon.get_width())//2, sy + (slot_size - icon.get_height())//2))

        # 인벤토리 슬롯 그리기
        for i in range(24):
            row, col = divmod(i, cols)
            sx = inv_px + 10 + col * (slot_size + gap) + gap
            sy = py + 40 + row * (slot_size + gap) + gap

            is_hover = i == self.hover_slot
            bg_color = (50, 55, 70, 200) if is_hover else (35, 38, 50, 180)

            draw_rounded_rect(surface, bg_color, (sx, sy, slot_size, slot_size), radius=4)

            if i < len(player.inventory.items):
                item_name, count = player.inventory.items[i]
                
                # 현재 드래그 중인 슬롯은 비워진 것처럼 보이게 처리
                is_dragged = self.dragging and self.drag_source_type == 'inventory' and self.drag_source_index == i
                if not is_dragged:
                    icon = ItemIconRenderer.get_icon(item_name)
                    icon_x = sx + (slot_size - icon.get_width()) // 2
                    icon_y = sy + (slot_size - icon.get_height()) // 2
                    surface.blit(icon, (icon_x, icon_y))

                    if count > 1:
                        count_surf = font_count.render(str(count), True, Colors.UI_TEXT)
                        surface.blit(count_surf, (sx + slot_size - count_surf.get_width() - 2, sy + slot_size - 14))

        # 툴팁 (마우스 오버 시 아이템 정보)
        hover_item = None
        if self.hover_slot is not None and self.hover_slot < len(player.inventory.items) and not self.dragging:
            hover_item = player.inventory.items[self.hover_slot][0]
        elif self.hover_equip is not None and player.equipped.get(self.hover_equip) and not self.dragging:
            hover_item = player.equipped[self.hover_equip]
            
        if hover_item:
            data = ITEM_DATABASE.get(hover_item, {})
            info_y = py + panel_h - 60
            name_surf = font_small.render(t(hover_item), True, Colors.UI_ACCENT_WARM)
            surface.blit(name_surf, (inv_px + 15, info_y))

            desc_surf = font_small.render(t(f"desc_{hover_item}")[:40], True, Colors.UI_TEXT_DIM)
            surface.blit(desc_surf, (inv_px + 15, info_y + 16))

            hint = font_small.render(t("inventory_hint"), True, (100, 105, 120))
            surface.blit(hint, (inv_px + 15, info_y + 32))

        # 드래그 중인 아이템 그리기 (마지막에 그려서 맨 위에 오게 함)
        if self.dragging and self.drag_item_name:
            icon = ItemIconRenderer.get_icon(self.drag_item_name)
            # 아이콘 중심이 마우스에 오도록
            dx = self.drag_mouse_pos[0] - icon.get_width() // 2
            dy = self.drag_mouse_pos[1] - icon.get_height() // 2
            surface.blit(icon, (dx, dy))
