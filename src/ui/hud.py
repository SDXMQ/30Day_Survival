import pygame
import math
from settings import Colors, RESOLUTION_OPTIONS, DIFFICULTY_PRESETS, DEFAULT_WORLD_SETTINGS, GameSettings, TILE_SIZE
from renderer import draw_rounded_rect, draw_gradient_rect, draw_glow, ItemIconRenderer
from items import ITEM_DATABASE, ItemCategory
from crafting import CRAFTING_RECIPES, RECIPE_CATEGORIES
from utils import wrap_text, ease_out_cubic, lerp
from .fonts import FontManager


class HUD:
    """인게임 HUD"""

    def __init__(self, screen_w, screen_h):
        self.sw = screen_w
        self.sh = screen_h
        self.notification_queue = []
        self.shown_hp = 100
        self.shown_hunger = 100
        self.shown_thirst = 100
        self.shown_stress = 0
        self.shown_stamina = 100

    def resize(self, w, h):
        self.sw = w
        self.sh = h

    def update(self, dt, player):
        # 부드러운 바 애니메이션
        self.shown_hp = lerp(self.shown_hp, player.hp, 0.1)
        self.shown_hunger = lerp(self.shown_hunger, player.hunger, 0.1)
        self.shown_thirst = lerp(self.shown_thirst, player.thirst, 0.1)
        self.shown_stress = lerp(self.shown_stress, player.stress, 0.1)
        self.shown_stamina = lerp(self.shown_stamina, player.stamina, 0.1)

        # 알림 업데이트
        self.notification_queue = [(msg, t - dt, a) for msg, t, a in self.notification_queue if t > 0]

    def add_notification(self, message, duration=3.0):
        self.notification_queue.append((message, duration, 0))

    def draw(self, surface, player, time_system, weather_system, current_day, total_days):
        self._draw_stat_bars(surface, player)
        self._draw_time_info(surface, time_system, current_day, total_days)
        self._draw_weather_info(surface, weather_system)
        self._draw_minimap(surface, player)
        self._draw_notifications(surface)
        self._draw_equipped_weapon(surface, player)
        self._draw_quick_info(surface, player)
        self._draw_crouch_indicator(surface, player)

    def _draw_stat_bars(self, surface, player):
        """스탯 바 (좌측 상단)"""
        x, y = 15, 15
        bar_w, bar_h = 180, 14
        spacing = 22
        font = FontManager.get(12)

        bars = [
            ("체력", self.shown_hp, 100, (220, 50, 50), (180, 30, 30)),
            ("배고픔", self.shown_hunger, 100, (210, 160, 50), (170, 130, 30)),
            ("갈증", self.shown_thirst, 100, (50, 140, 220), (30, 110, 180)),
            ("스트레스", self.shown_stress, 100, (180, 50, 200), (150, 30, 170)),
            ("스태미나", self.shown_stamina, 100, (50, 200, 100), (30, 160, 70)),
        ]

        # 배경 패널
        panel_h = len(bars) * spacing + 15
        draw_rounded_rect(surface, (15, 15, 25, 180), (x - 5, y - 5, bar_w + 55, panel_h), radius=8)

        for i, (label, value, max_val, color, dark_color) in enumerate(bars):
            by = y + i * spacing

            # 라벨
            label_surf = font.render(label, True, Colors.UI_TEXT_DIM)
            surface.blit(label_surf, (x, by))

            # 바 배경
            bx = x + 48
            pygame.draw.rect(surface, (30, 30, 40), (bx, by + 1, bar_w, bar_h), border_radius=3)

            # 바 값
            ratio = max(0, min(1, value / max_val))
            fill_w = int(bar_w * ratio)
            if fill_w > 0:
                draw_gradient_rect(surface, (bx, by + 1, fill_w, bar_h),
                                  color, dark_color, vertical=True, radius=3)

            # 수치 표시
            val_text = font.render(f"{int(value)}", True, Colors.UI_TEXT)
            surface.blit(val_text, (bx + bar_w + 4, by))

    def _draw_time_info(self, surface, time_system, current_day, total_days):
        """시간 정보 (우측 상단)"""
        font_big = FontManager.get(20)
        font_small = FontManager.get(13)

        # 배경 패널
        panel_w, panel_h = 160, 55
        px = self.sw - panel_w - 15
        py = 15
        draw_rounded_rect(surface, (15, 15, 25, 180), (px, py, panel_w, panel_h), radius=8)

        # 날짜
        day_text = font_big.render(f"Day {current_day}/{total_days}", True, Colors.UI_ACCENT)
        surface.blit(day_text, (px + 10, py + 5))

        # 시간
        time_text = font_small.render(f"{time_system.time_string}  {time_system.period_name}", True, Colors.UI_TEXT)
        surface.blit(time_text, (px + 10, py + 32))

    def _draw_weather_info(self, surface, weather_system):
        """날씨 (우측 상단 아래)"""
        font = FontManager.get(13)
        px = self.sw - 175
        py = 80

        weather_text = font.render(f"날씨: {weather_system.current_weather}", True, Colors.UI_TEXT_DIM)
        surface.blit(weather_text, (px + 10, py))

    def _draw_minimap(self, surface, player):
        """미니맵 (우측 하단)"""
        size = 120
        mx = self.sw - size - 15
        my = self.sh - size - 15

        # 미니맵 배경
        minimap_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(minimap_surf, (20, 22, 30, 200), (0, 0, size, size), border_radius=6)
        pygame.draw.rect(minimap_surf, (60, 65, 80, 150), (0, 0, size, size), 1, border_radius=6)

        # 플레이어 위치 (중앙)
        center = size // 2
        pygame.draw.circle(minimap_surf, (80, 200, 255), (center, center), 3)
        pygame.draw.circle(minimap_surf, (80, 200, 255), (center, center), 6, 1)

        # 좌표 표시
        font = FontManager.get(10)
        coord = font.render(f"({int(player.x)}, {int(player.y)})", True, Colors.UI_TEXT_DIM)
        minimap_surf.blit(coord, (4, size - 14))

        surface.blit(minimap_surf, (mx, my))

    def _draw_notifications(self, surface):
        """알림 메시지 (화면 상단 중앙)"""
        font = FontManager.get(14)
        y = 60

        for msg, timer, _ in self.notification_queue[:5]:
            alpha = max(0, min(255, int(timer * 255)))
            if alpha <= 0:
                continue
            text_surf = font.render(msg, True, Colors.UI_TEXT)
            text_w = text_surf.get_width()
            x = (self.sw - text_w) // 2

            bg_alpha = max(0, min(180, alpha))
            bg = pygame.Surface((text_w + 20, 28), pygame.SRCALPHA)
            pygame.draw.rect(bg, (20, 22, 30, bg_alpha), (0, 0, text_w + 20, 28), border_radius=6)
            surface.blit(bg, (x - 10, y - 4))
            text_surf.set_alpha(alpha)
            surface.blit(text_surf, (x, y))
            y += 32

    def _draw_equipped_weapon(self, surface, player):
        """장착 무기 (좌측 하단)"""
        wx, wy = 15, self.sh - 60
        draw_rounded_rect(surface, (15, 15, 25, 180), (wx, wy, 50, 50), radius=6)

        weapon = player.equipped.get("weapon")
        if weapon:
            icon = ItemIconRenderer.get_icon(weapon)
            surface.blit(icon, (wx + 9, wy + 9))
        else:
            font = FontManager.get(10)
            text = font.render("주먹", True, Colors.UI_TEXT_DIM)
            surface.blit(text, (wx + 12, wy + 18))

    def _draw_quick_info(self, surface, player):
        """빠른 정보 (좌측 하단)"""
        font = FontManager.get(11)
        x, y = 75, self.sh - 55

        # 방어도
        def_text = font.render(f"방어도: {player.shelter_defense}", True, Colors.UI_TEXT_DIM)
        surface.blit(def_text, (x, y))

        # 킬 수
        kill_text = font.render(f"처치: {player.killed_zombies}", True, Colors.UI_TEXT_DIM)
        surface.blit(kill_text, (x, y + 16))

        # 조작 안내
        hint = font.render("E:상호작용  I:인벤토리  C:크래프팅  Tab:지도  LCTRL:앉기  ESC:메뉴", True, (100, 105, 120))
        surface.blit(hint, (x, y + 32))

    def _draw_crouch_indicator(self, surface, player):
        """은신 상태 표시 (하단 중앙)"""
        if not player.is_crouching:
            return
        font = FontManager.get(14)
        text = font.render("◆ 은신 중 ◆", True, (100, 200, 255))
        tw = text.get_width()
        x = (self.sw - tw) // 2
        y = self.sh - 45
        bg = pygame.Surface((tw + 20, 28), pygame.SRCALPHA)
        pygame.draw.rect(bg, (20, 40, 60, 180), (0, 0, tw + 20, 28), border_radius=6)
        surface.blit(bg, (x - 10, y - 4))
        surface.blit(text, (x, y))

class EventLogUI:
    """이벤트 로그 표시"""

    def __init__(self, screen_w, screen_h):
        self.sw = screen_w
        self.sh = screen_h

    def draw(self, surface, event_log):
        if not event_log:
            return

        font = FontManager.get(12)
        y = self.sh // 2 - len(event_log) * 18

        for msg, timer in event_log:
            alpha = max(0, min(255, int(timer * 80)))
            if alpha <= 0:
                continue
            text_surf = font.render(msg, True, Colors.UI_TEXT)
            text_surf.set_alpha(alpha)

            bg_alpha = max(0, min(140, alpha))
            bg = pygame.Surface((text_surf.get_width() + 16, 20), pygame.SRCALPHA)
            bg.fill((10, 12, 20, bg_alpha))
            surface.blit(bg, (8, y - 2))
            surface.blit(text_surf, (16, y))
            y += 20

