import pygame
import math
from settings import Colors, RESOLUTION_OPTIONS, DIFFICULTY_PRESETS, DEFAULT_WORLD_SETTINGS, GameSettings, TILE_SIZE
from renderer import draw_rounded_rect, draw_gradient_rect, draw_glow, ItemIconRenderer
from items import ITEM_DATABASE, ItemCategory
from crafting import CRAFTING_RECIPES, RECIPE_CATEGORIES
from utils import wrap_text, ease_out_cubic, lerp
from .fonts import FontManager


class DialogueUI:
    """NPC 대화 시스템"""

    def __init__(self, screen_w, screen_h):
        self.sw = screen_w
        self.sh = screen_h
        self.visible = False
        self.npc_name = ""
        self.text = ""
        self.options = []
        self.selected_option = 0
        self.on_select = None

    def show(self, npc_name, text, options=None, on_select=None):
        self.visible = True
        self.npc_name = npc_name
        self.text = text
        self.options = options or [("확인", "ok")]
        self.selected_option = 0
        self.on_select = on_select

    def hide(self):
        self.visible = False

    def handle_event(self, event):
        if not self.visible:
            return None

        panel_w = min(500, self.sw - 40)
        panel_h = 160 + len(self.options) * 28
        px = (self.sw - panel_w) // 2
        py = self.sh - panel_h - 30

        font = FontManager.get(14)
        lines = wrap_text(self.text, font, panel_w - 30)
        opt_y = py + 40 + min(len(lines), 4) * 20 + 20

        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            for i in range(len(self.options)):
                oy = opt_y + i * 28
                if px + 20 <= mx <= px + panel_w - 20 and oy - 8 <= my <= oy + 25:
                    self.selected_option = i

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # 대화창 패널 클릭, 혹은 밖을 클릭 시
            if len(self.options) == 1 and self.options[0][1] == "ok":
                # 일반 대화인 경우 클릭 시 무조건 닫힘/진행
                result = self.options[self.selected_option][1]
                if self.on_select:
                    self.on_select(result)
                self.hide()
                return result
            else:
                # 선택지가 있는 경우 클릭한 옵션 선택
                for i in range(len(self.options)):
                    oy = opt_y + i * 28
                    if px + 20 <= mx <= px + panel_w - 20 and oy - 8 <= my <= oy + 25:
                        self.selected_option = i
                        result = self.options[self.selected_option][1]
                        if self.on_select:
                            self.on_select(result)
                        self.hide()
                        return result
                
                # 옵션 단추 외의 다른 영역(패널 내부 텍스트 및 외부 포함) 클릭 시 대화 닫기
                result = "close"
                if self.on_select:
                    self.on_select(result)
                self.hide()
                return result

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                result = "close"
                if self.on_select:
                    self.on_select(result)
                self.hide()
                return result
            elif event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE):
                result = self.options[self.selected_option][1]
                if self.on_select:
                    self.on_select(result)
                self.hide()
                return result

        return None

    def draw(self, surface):
        if not self.visible:
            return

        font = FontManager.get(14)
        font_name = FontManager.get(16)
        font_opt = FontManager.get(13)

        panel_w = min(500, self.sw - 40)
        panel_h = 160 + len(self.options) * 28
        px = (self.sw - panel_w) // 2
        py = self.sh - panel_h - 30

        draw_rounded_rect(surface, (15, 18, 28, 230), (px, py, panel_w, panel_h), radius=10)
        draw_rounded_rect(surface, Colors.UI_BORDER + (180,), (px, py, panel_w, panel_h), radius=10)

        # NPC 이름
        name_surf = font_name.render(self.npc_name, True, Colors.UI_ACCENT_WARM)
        surface.blit(name_surf, (px + 15, py + 12))

        # 대화 내용
        lines = wrap_text(self.text, font, panel_w - 30)
        for i, line in enumerate(lines[:4]):
            text_surf = font.render(line, True, Colors.UI_TEXT)
            surface.blit(text_surf, (px + 15, py + 40 + i * 20))

        # 선택지
        opt_y = py + 40 + min(len(lines), 4) * 20 + 20
        for i, (opt_text, opt_value) in enumerate(self.options):
            is_selected = i == self.selected_option
            color = Colors.UI_ACCENT if is_selected else Colors.UI_TEXT_DIM
            prefix = "▸ " if is_selected else "  "
            opt_surf = font_opt.render(f"{prefix}{opt_text}", True, color)
            surface.blit(opt_surf, (px + 20, opt_y + i * 28))

