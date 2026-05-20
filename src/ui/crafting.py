import pygame
import math
from settings import Colors, RESOLUTION_OPTIONS, DIFFICULTY_PRESETS, DEFAULT_WORLD_SETTINGS, GameSettings, TILE_SIZE
from renderer import draw_rounded_rect, draw_gradient_rect, draw_glow, ItemIconRenderer
from items import ITEM_DATABASE, ItemCategory
from crafting import CRAFTING_RECIPES, RECIPE_CATEGORIES
from utils import wrap_text, ease_out_cubic, lerp
from .fonts import FontManager
from i18n import t


class CraftingUI:
    """크래프팅 화면"""

    def __init__(self, screen_w, screen_h):
        self.sw = screen_w
        self.sh = screen_h
        self.visible = False
        self.selected_recipe = -1
        self.hover_recipe = -1
        self.animation_progress = 0
        self.scroll_offset = 0

    def toggle(self):
        self.visible = not self.visible
        self.animation_progress = 0

    def update(self, dt):
        if self.visible and self.animation_progress < 1:
            self.animation_progress = min(1, self.animation_progress + dt * 5)

    def handle_event(self, event, player):
        if not self.visible:
            return None

        recipes = player.crafting.get_all_recipes_with_status(player.inventory)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            panel_w, panel_h = 400, 420
            px = (self.sw - panel_w) // 2
            py = (self.sh - panel_h) // 2

            for i, recipe in enumerate(recipes):
                ry = py + 45 + i * 40 - self.scroll_offset
                if not (py + 40 <= ry <= py + panel_h - 10):
                    continue
                if px + 10 <= mx <= px + panel_w - 10 and ry <= my <= ry + 36:
                    if recipe["can_craft"] and not player.crafting.is_crafting:
                        return ("craft", recipe["name"])
                    break

        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            panel_w, panel_h = 400, 420
            px = (self.sw - panel_w) // 2
            py = (self.sh - panel_h) // 2
            self.hover_recipe = -1
            recipes = list(CRAFTING_RECIPES.keys())
            for i in range(len(recipes)):
                ry = py + 45 + i * 40 - self.scroll_offset
                if not (py + 40 <= ry <= py + panel_h - 10):
                    continue
                if px + 10 <= mx <= px + panel_w - 10 and ry <= my <= ry + 36:
                    self.hover_recipe = i
                    break

        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset -= event.y * 20
            self.scroll_offset = max(0, self.scroll_offset)

        return None

    def draw(self, surface, player):
        if not self.visible:
            return

        t_val = ease_out_cubic(self.animation_progress)
        overlay = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(120 * t_val)))
        surface.blit(overlay, (0, 0))

        panel_w, panel_h = 400, 420
        px = (self.sw - panel_w) // 2
        py = int((self.sh - panel_h) / 2 + (1 - t_val) * 30)

        draw_rounded_rect(surface, (20, 22, 35, int(230 * t_val)), (px, py, panel_w, panel_h), radius=12)
        draw_rounded_rect(surface, Colors.UI_BORDER + (int(150 * t_val),), (px, py, panel_w, panel_h), radius=12)

        font_title = FontManager.get(18)
        font = FontManager.get(12)
        font_small = FontManager.get(10)

        title = font_title.render(t("crafting"), True, Colors.UI_ACCENT)
        surface.blit(title, (px + 15, py + 10))

        recipes = player.crafting.get_all_recipes_with_status(player.inventory)

        # 크래프팅 진행 바
        if player.crafting.is_crafting:
            prog = player.crafting.craft_progress
            bar_y = py + 35
            pygame.draw.rect(surface, (30, 32, 42), (px + 10, bar_y, panel_w - 20, 6), border_radius=3)
            pygame.draw.rect(surface, Colors.UI_ACCENT, (px + 10, bar_y, int((panel_w - 20) * prog), 6), border_radius=3)

        for i, recipe in enumerate(recipes):
            ry = py + 45 + i * 40 - self.scroll_offset
            if ry < py + 40 or ry > py + panel_h - 10:
                continue

            is_hover = i == self.hover_recipe
            can_craft = recipe["can_craft"]
            bg = (50, 55, 70, 180) if is_hover else (30, 33, 45, 150)
            if not can_craft:
                bg = (25, 25, 30, 120)

            draw_rounded_rect(surface, bg, (px + 10, ry, panel_w - 20, 36), radius=4)

            name_color = Colors.UI_TEXT if can_craft else Colors.UI_TEXT_DIM
            name_surf = font.render(t(recipe["name"]), True, name_color)
            surface.blit(name_surf, (px + 20, ry + 4))

            # 재료 표시
            mats = []
            for item_name, (have, need) in recipe["ingredients_status"].items():
                color = Colors.UI_SUCCESS if have >= need else Colors.UI_DANGER
                mats.append((f"{t(item_name)}({have}/{need})", color))

            mx = px + 20
            for mat_text, mat_color in mats:
                ms = font_small.render(mat_text, True, mat_color)
                surface.blit(ms, (mx, ry + 20))
                mx += ms.get_width() + 8
