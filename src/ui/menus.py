import pygame
import math
from settings import Colors, RESOLUTION_OPTIONS, DIFFICULTY_PRESETS, DEFAULT_WORLD_SETTINGS, GameSettings, TILE_SIZE
from renderer import draw_rounded_rect, draw_gradient_rect, draw_glow, ItemIconRenderer
from items import ITEM_DATABASE, ItemCategory
from crafting import CRAFTING_RECIPES, RECIPE_CATEGORIES
from utils import wrap_text, ease_out_cubic, lerp
from .fonts import FontManager


class MainMenuUI:
    """메인 메뉴"""

    def __init__(self, screen_w, screen_h):
        self.sw = screen_w
        self.sh = screen_h
        self.buttons = [
            ("새 게임", "new_game"),
            ("이어하기", "load_game"),
            ("설정", "settings"),
            ("종료", "quit"),
        ]
        self.hover_index = -1
        self.title_glow_timer = 0
        self.title_y_offset = 0

    def update(self, dt):
        self.title_glow_timer += dt
        self.title_y_offset = math.sin(self.title_glow_timer * 0.8) * 3

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            self.hover_index = -1
            for i in range(len(self.buttons)):
                bw, bh = 260, 45
                bx = (self.sw - bw) // 2
                by = self.sh // 2 + 30 + i * 60
                if bx <= mx <= bx + bw and by <= my <= by + bh:
                    self.hover_index = i

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if 0 <= self.hover_index < len(self.buttons):
                return self.buttons[self.hover_index][1]

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return "new_game"

        return None

    def draw(self, surface):
        # 배경
        surface.fill(Colors.MENU_BG)

        # 그라데이션 오버레이
        for y in range(self.sh):
            t = y / self.sh
            alpha = int(20 * t)
            pygame.draw.line(surface, (30 + int(10 * t), 15, 20 + int(15 * t)), (0, y), (self.sw, y))

        font_title = FontManager.get(48)
        font_sub = FontManager.get(16)
        font_btn = FontManager.get(18)
        font_small = FontManager.get(11)

        # 타이틀
        title = "30일간의 생존"
        title_surf = font_title.render(title, True, Colors.UI_ACCENT_WARM)
        tx = (self.sw - title_surf.get_width()) // 2
        ty = int(self.sh * 0.2 + self.title_y_offset)

        # 글로우 효과
        glow_intensity = 0.3 + 0.2 * math.sin(self.title_glow_timer * 2)
        draw_glow(surface, (tx + title_surf.get_width() // 2, ty + 20),
                  80, Colors.TITLE_GLOW, glow_intensity)

        surface.blit(title_surf, (tx, ty))

        # 부제
        sub = font_sub.render("좀비 아포칼립스 오픈월드 서바이벌", True, Colors.UI_TEXT_DIM)
        surface.blit(sub, ((self.sw - sub.get_width()) // 2, ty + 60))

        # 버튼
        for i, (text, action) in enumerate(self.buttons):
            bw, bh = 260, 45
            bx = (self.sw - bw) // 2
            by = self.sh // 2 + 30 + i * 60
            is_hover = i == self.hover_index

            if is_hover:
                draw_rounded_rect(surface, (Colors.UI_ACCENT[0], Colors.UI_ACCENT[1], Colors.UI_ACCENT[2], 40),
                                 (bx, by, bw, bh), radius=8)
                pygame.draw.rect(surface, Colors.UI_ACCENT, (bx, by, bw, bh), 2, border_radius=8)
                color = Colors.UI_ACCENT
            else:
                draw_rounded_rect(surface, (30, 35, 50, 150), (bx, by, bw, bh), radius=8)
                pygame.draw.rect(surface, Colors.UI_BORDER, (bx, by, bw, bh), 1, border_radius=8)
                color = Colors.UI_TEXT

            btn_surf = font_btn.render(text, True, color)
            surface.blit(btn_surf, (bx + (bw - btn_surf.get_width()) // 2,
                                    by + (bh - btn_surf.get_height()) // 2))

        # 하단 정보
        ver = font_small.render("v1.0  |  Python + Pygame", True, (60, 65, 75))
        surface.blit(ver, ((self.sw - ver.get_width()) // 2, self.sh - 30))


class WorldCreationUI:
    """월드 생성 설정 화면"""

    def __init__(self, screen_w, screen_h):
        self.sw = screen_w
        self.sh = screen_h
        self.settings = dict(DEFAULT_WORLD_SETTINGS)
        self.difficulty_names = list(DIFFICULTY_PRESETS.keys())
        self.diff_index = 2  # 보통
        self.settings["difficulty"] = self.difficulty_names[self.diff_index]

        self.sliders = {
            "day_length_minutes": {"label": "하루 길이(분)", "min": 5, "max": 30, "step": 1},
            "resource_density": {"label": "자원 밀도", "min": 0.2, "max": 3.0, "step": 0.1},
            "weather_variability": {"label": "날씨 변동성", "min": 0.0, "max": 2.0, "step": 0.1},
            "zombie_activity": {"label": "좀비 활동량", "min": 0.0, "max": 2.0, "step": 0.1},
            "building_density": {"label": "건물 밀도", "min": 0.5, "max": 2.0, "step": 0.1},
            "total_days": {"label": "생존 일수", "min": 10, "max": 100, "step": 5},
        }
        self.hover_button = ""
        self.dragging_slider = None
        self.world_name_input = "월드 1"
        self.name_editing = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            panel_w, panel_h = 500, 520
            px = (self.sw - panel_w) // 2
            py = (self.sh - panel_h) // 2

            # 난이도 화살표
            diff_y = py + 80
            if px + 200 <= mx <= px + 220 and diff_y <= my <= diff_y + 25:
                self.diff_index = (self.diff_index - 1) % len(self.difficulty_names)
                self.settings["difficulty"] = self.difficulty_names[self.diff_index]
            elif px + 400 <= mx <= px + 420 and diff_y <= my <= diff_y + 25:
                self.diff_index = (self.diff_index + 1) % len(self.difficulty_names)
                self.settings["difficulty"] = self.difficulty_names[self.diff_index]

            # 슬라이더 클릭
            for i, (key, slider) in enumerate(self.sliders.items()):
                sy = py + 130 + i * 45
                sx = px + 200
                sw = 250
                if sx <= mx <= sx + sw and sy <= my <= sy + 20:
                    self.dragging_slider = key

            # 시작 버튼
            btn_y = py + panel_h - 55
            if px + panel_w // 2 - 80 <= mx <= px + panel_w // 2 + 80 and btn_y <= my <= btn_y + 42:
                return "start"

            # 샌드박스 토글
            sandbox_y = py + panel_h - 100
            if px + 20 <= mx <= px + 200 and sandbox_y <= my <= sandbox_y + 22:
                self.settings["sandbox"] = not self.settings.get("sandbox", False)

            # 뒤로 버튼
            if px + 10 <= mx <= px + 70 and py + 10 <= my <= py + 35:
                return "back"

            # 이름 입력 필드
            name_y = py + 45
            if px + 200 <= mx <= px + 450 and name_y <= my <= name_y + 28:
                self.name_editing = True
            else:
                self.name_editing = False

        if event.type == pygame.MOUSEBUTTONUP:
            self.dragging_slider = None

        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            if self.dragging_slider:
                panel_w = 500
                px = (self.sw - panel_w) // 2
                sx = px + 200
                sw = 250
                ratio = max(0, min(1, (mx - sx) / sw))
                slider = self.sliders[self.dragging_slider]
                value_range = slider["max"] - slider["min"]
                raw = slider["min"] + ratio * value_range
                step = slider["step"]
                value = round(raw / step) * step
                self.settings[self.dragging_slider] = max(slider["min"], min(slider["max"], value))

        if event.type == pygame.KEYDOWN and self.name_editing:
            if event.key == pygame.K_BACKSPACE:
                self.world_name_input = self.world_name_input[:-1]
            elif event.key == pygame.K_RETURN:
                self.name_editing = False
            elif event.unicode and len(self.world_name_input) < 20:
                self.world_name_input += event.unicode
            self.settings["world_name"] = self.world_name_input

        return None

    def draw(self, surface):
        surface.fill(Colors.MENU_BG)

        font_title = FontManager.get(24)
        font = FontManager.get(14)
        font_small = FontManager.get(11)
        font_diff = FontManager.get(16)

        panel_w, panel_h = 500, 520
        px = (self.sw - panel_w) // 2
        py = (self.sh - panel_h) // 2

        draw_rounded_rect(surface, (20, 22, 35, 240), (px, py, panel_w, panel_h), radius=12)
        draw_rounded_rect(surface, Colors.UI_BORDER, (px, py, panel_w, panel_h), radius=12)

        title = font_title.render("새 월드 생성", True, Colors.UI_ACCENT)
        surface.blit(title, (px + (panel_w - title.get_width()) // 2, py + 10))

        # 뒤로 버튼
        back_surf = font_small.render("◀ 뒤로", True, Colors.UI_TEXT_DIM)
        surface.blit(back_surf, (px + 15, py + 15))

        # 월드 이름
        name_y = py + 48
        name_label = font.render("월드 이름:", True, Colors.UI_TEXT)
        surface.blit(name_label, (px + 20, name_y))
        name_box_color = Colors.UI_ACCENT if self.name_editing else Colors.UI_BORDER
        pygame.draw.rect(surface, name_box_color, (px + 200, name_y - 2, 250, 26), 1, border_radius=4)
        name_surf = font.render(self.world_name_input, True, Colors.UI_TEXT)
        surface.blit(name_surf, (px + 208, name_y + 2))

        # 난이도
        diff_y = py + 82
        diff_label = font.render("난이도:", True, Colors.UI_TEXT)
        surface.blit(diff_label, (px + 20, diff_y))

        # 화살표
        arrow_l = font_diff.render("◀", True, Colors.UI_ACCENT)
        surface.blit(arrow_l, (px + 200, diff_y - 2))

        diff_name = self.difficulty_names[self.diff_index]
        diff_color = Colors.UI_SUCCESS
        if self.diff_index >= 3:
            diff_color = Colors.UI_WARNING
        if self.diff_index >= 4:
            diff_color = Colors.UI_DANGER
        diff_text = font_diff.render(diff_name, True, diff_color)
        diff_cx = px + 200 + 125 - diff_text.get_width() // 2
        surface.blit(diff_text, (diff_cx, diff_y - 2))

        arrow_r = font_diff.render("▶", True, Colors.UI_ACCENT)
        surface.blit(arrow_r, (px + 400, diff_y - 2))

        # 난이도 설명
        diff_data = DIFFICULTY_PRESETS.get(diff_name, {})
        desc = diff_data.get("description", "")
        desc_surf = font_small.render(desc[:50], True, Colors.UI_TEXT_DIM)
        surface.blit(desc_surf, (px + 20, diff_y + 22))

        # 슬라이더
        for i, (key, slider) in enumerate(self.sliders.items()):
            sy = py + 130 + i * 45
            label = font.render(slider["label"] + ":", True, Colors.UI_TEXT)
            surface.blit(label, (px + 20, sy))

            sx = px + 200
            sw = 250
            value = self.settings.get(key, slider["min"])
            ratio = (value - slider["min"]) / (slider["max"] - slider["min"])

            # 슬라이더 트랙
            pygame.draw.rect(surface, (40, 42, 55), (sx, sy + 6, sw, 8), border_radius=4)
            # 채워진 부분
            pygame.draw.rect(surface, Colors.UI_ACCENT, (sx, sy + 6, int(sw * ratio), 8), border_radius=4)
            # 핸들
            handle_x = sx + int(sw * ratio)
            pygame.draw.circle(surface, Colors.UI_ACCENT, (handle_x, sy + 10), 7)
            pygame.draw.circle(surface, Colors.WHITE, (handle_x, sy + 10), 4)

            # 값 표시
            if isinstance(value, float):
                val_text = font_small.render(f"{value:.1f}", True, Colors.UI_TEXT)
            else:
                val_text = font_small.render(f"{int(value)}", True, Colors.UI_TEXT)
            surface.blit(val_text, (sx + sw + 10, sy + 2))

        # 샌드박스 토글
        sandbox_y = py + panel_h - 100
        is_sandbox = self.settings.get("sandbox", False)
        check_color = Colors.UI_ACCENT if is_sandbox else Colors.UI_BORDER
        pygame.draw.rect(surface, check_color, (px + 20, sandbox_y, 18, 18), border_radius=3)
        if is_sandbox:
            pygame.draw.rect(surface, Colors.UI_ACCENT, (px + 23, sandbox_y + 3, 12, 12), border_radius=2)
        sandbox_label = font.render("🔧 샌드박스 모드 (모든 아이템 지급)", True,
                                    Colors.UI_ACCENT if is_sandbox else Colors.UI_TEXT_DIM)
        surface.blit(sandbox_label, (px + 44, sandbox_y + 1))

        # 시작 버튼
        btn_w, btn_h = 160, 42
        btn_x = px + (panel_w - btn_w) // 2
        btn_y = py + panel_h - 55
        draw_rounded_rect(surface, Colors.UI_ACCENT + (40,), (btn_x, btn_y, btn_w, btn_h), radius=8)
        pygame.draw.rect(surface, Colors.UI_ACCENT, (btn_x, btn_y, btn_w, btn_h), 2, border_radius=8)
        start = font.render("월드 생성 시작", True, Colors.UI_ACCENT)
        surface.blit(start, (btn_x + (btn_w - start.get_width()) // 2,
                            btn_y + (btn_h - start.get_height()) // 2))

    def get_settings(self):
        return dict(self.settings)


class SettingsUI:
    """게임 설정 화면"""

    def __init__(self, screen_w, screen_h):
        self.sw = screen_w
        self.sh = screen_h
        self.game_settings = GameSettings()
        self.res_index = 0
        for i, res in enumerate(RESOLUTION_OPTIONS):
            if list(res) == self.game_settings.resolution:
                self.res_index = i
                break

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            panel_w, panel_h = 420, 350
            px = (self.sw - panel_w) // 2
            py = (self.sh - panel_h) // 2

            # 해상도 변경
            res_y = py + 60
            if px + 200 <= mx <= px + 220 and res_y <= my <= res_y + 25:
                self.res_index = (self.res_index - 1) % len(RESOLUTION_OPTIONS)
            elif px + 370 <= mx <= px + 390 and res_y <= my <= res_y + 25:
                self.res_index = (self.res_index + 1) % len(RESOLUTION_OPTIONS)

            # 전체화면 토글
            fs_y = py + 100
            if px + 200 <= mx <= px + 350 and fs_y <= my <= fs_y + 30:
                self.game_settings.fullscreen = not self.game_settings.fullscreen

            # 적용 버튼
            apply_y = py + panel_h - 55
            if px + panel_w // 2 - 60 <= mx <= px + panel_w // 2 + 60 and apply_y <= my <= apply_y + 40:
                res = RESOLUTION_OPTIONS[self.res_index]
                self.game_settings.resolution = list(res)
                self.game_settings.save()
                return "apply"

            # 뒤로
            if px + 10 <= mx <= px + 70 and py + 10 <= my <= py + 35:
                return "back"

        return None

    def draw(self, surface):
        surface.fill(Colors.MENU_BG)

        font_title = FontManager.get(24)
        font = FontManager.get(14)
        font_small = FontManager.get(11)

        panel_w, panel_h = 420, 350
        px = (self.sw - panel_w) // 2
        py = (self.sh - panel_h) // 2

        draw_rounded_rect(surface, (20, 22, 35, 240), (px, py, panel_w, panel_h), radius=12)

        title = font_title.render("설정", True, Colors.UI_ACCENT)
        surface.blit(title, (px + (panel_w - title.get_width()) // 2, py + 15))

        back_surf = font_small.render("◀ 뒤로", True, Colors.UI_TEXT_DIM)
        surface.blit(back_surf, (px + 15, py + 15))

        # 해상도
        res_y = py + 60
        res_label = font.render("해상도:", True, Colors.UI_TEXT)
        surface.blit(res_label, (px + 20, res_y))

        arrow_l = font.render("◀", True, Colors.UI_ACCENT)
        surface.blit(arrow_l, (px + 200, res_y))

        res = RESOLUTION_OPTIONS[self.res_index]
        res_text = font.render(f"{res[0]}x{res[1]}", True, Colors.UI_TEXT)
        surface.blit(res_text, (px + 260, res_y))

        arrow_r = font.render("▶", True, Colors.UI_ACCENT)
        surface.blit(arrow_r, (px + 370, res_y))

        # 전체화면
        fs_y = py + 100
        fs_label = font.render("화면 모드:", True, Colors.UI_TEXT)
        surface.blit(fs_label, (px + 20, fs_y))

        fs_text = "전체화면" if self.game_settings.fullscreen else "창 모드"
        fs_color = Colors.UI_SUCCESS if self.game_settings.fullscreen else Colors.UI_TEXT
        fs_surf = font.render(f"[ {fs_text} ]", True, fs_color)
        surface.blit(fs_surf, (px + 200, fs_y))

        # 파티클
        pq_y = py + 140
        pq_label = font.render("파티클 품질:", True, Colors.UI_TEXT)
        surface.blit(pq_label, (px + 20, pq_y))
        pq_names = ["끔", "낮음", "보통", "높음"]
        pq = self.game_settings.particles_quality
        pq_surf = font.render(pq_names[pq], True, Colors.UI_TEXT)
        surface.blit(pq_surf, (px + 200, pq_y))

        # 적용 버튼
        apply_y = py + panel_h - 55
        btn_w, btn_h = 120, 40
        btn_x = px + (panel_w - btn_w) // 2
        draw_rounded_rect(surface, Colors.UI_ACCENT + (40,), (btn_x, apply_y, btn_w, btn_h), radius=8)
        pygame.draw.rect(surface, Colors.UI_ACCENT, (btn_x, apply_y, btn_w, btn_h), 2, border_radius=8)
        apply_text = font.render("적용", True, Colors.UI_ACCENT)
        surface.blit(apply_text, (btn_x + (btn_w - apply_text.get_width()) // 2,
                                 apply_y + (btn_h - apply_text.get_height()) // 2))


class PauseUI:
    """일시정지 메뉴"""

    def __init__(self, screen_w, screen_h):
        self.sw = screen_w
        self.sh = screen_h
        self.buttons = [
            ("게임으로 돌아가기", "resume"),
            ("저장하기", "save"),
            ("설정", "settings"),
            ("메인 메뉴로", "main_menu"),
        ]
        self.hover_index = -1

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "resume"

        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            self.hover_index = -1
            for i in range(len(self.buttons)):
                bw, bh = 220, 40
                bx = (self.sw - bw) // 2
                by = self.sh // 2 - 40 + i * 55
                if bx <= mx <= bx + bw and by <= my <= by + bh:
                    self.hover_index = i

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if 0 <= self.hover_index < len(self.buttons):
                return self.buttons[self.hover_index][1]

        return None

    def draw(self, surface):
        overlay = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        font_title = FontManager.get(28)
        font_btn = FontManager.get(16)

        title = font_title.render("일시정지", True, Colors.UI_TEXT)
        surface.blit(title, ((self.sw - title.get_width()) // 2, self.sh // 2 - 100))

        for i, (text, action) in enumerate(self.buttons):
            bw, bh = 220, 40
            bx = (self.sw - bw) // 2
            by = self.sh // 2 - 40 + i * 55
            is_hover = i == self.hover_index

            if is_hover:
                draw_rounded_rect(surface, (Colors.UI_ACCENT[0], Colors.UI_ACCENT[1], Colors.UI_ACCENT[2], 40),
                                 (bx, by, bw, bh), radius=6)
                pygame.draw.rect(surface, Colors.UI_ACCENT, (bx, by, bw, bh), 2, border_radius=6)
                color = Colors.UI_ACCENT
            else:
                draw_rounded_rect(surface, (30, 35, 50, 180), (bx, by, bw, bh), radius=6)
                color = Colors.UI_TEXT

            btn_surf = font_btn.render(text, True, color)
            surface.blit(btn_surf, (bx + (bw - btn_surf.get_width()) // 2,
                                    by + (bh - btn_surf.get_height()) // 2))


class EndingUI:
    """엔딩 화면"""

    def __init__(self, screen_w, screen_h):
        self.sw = screen_w
        self.sh = screen_h
        self.ending_data = None
        self.player_stats = None
        self.animation_timer = 0
        self.phase = 0  # 0=페이드인, 1=타이틀, 2=설명, 3=통계

    def show(self, ending_data, player):
        self.ending_data = ending_data
        self.player_stats = {
            "days": player.days_survived,
            "kills": player.killed_zombies,
            "crafted": player.items_crafted,
            "explored": player.buildings_explored,
            "hp": int(player.hp),
            "defense": player.shelter_defense,
        }
        self.animation_timer = 0
        self.phase = 0

    def update(self, dt):
        self.animation_timer += dt
        if self.animation_timer > 2 and self.phase < 3:
            self.phase += 1
            self.animation_timer = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            if self.phase >= 3 and self.animation_timer > 1:
                return "main_menu"
            elif self.phase < 3:
                self.phase += 1
                self.animation_timer = 0
        return None

    def draw(self, surface):
        surface.fill((5, 5, 15))

        if not self.ending_data:
            return

        font_title = FontManager.get(28)
        font = FontManager.get(15)
        font_small = FontManager.get(12)

        if self.phase >= 1:
            title = self.ending_data.get("title", "엔딩")
            title_surf = font_title.render(title, True, Colors.UI_ACCENT_WARM)
            tx = (self.sw - title_surf.get_width()) // 2
            surface.blit(title_surf, (tx, self.sh // 4))

        if self.phase >= 2:
            desc = self.ending_data.get("description", "")
            lines = desc.split("\n")
            for i, line in enumerate(lines):
                line_surf = font.render(line, True, Colors.UI_TEXT)
                surface.blit(line_surf, ((self.sw - line_surf.get_width()) // 2,
                                       self.sh // 3 + 40 + i * 24))

        if self.phase >= 3 and self.player_stats:
            stats_y = self.sh // 2 + 40
            stats = [
                f"생존 일수: {self.player_stats['days']}일",
                f"좀비 처치: {self.player_stats['kills']}마리",
                f"크래프팅: {self.player_stats['crafted']}회",
                f"은신처 방어도: {self.player_stats['defense']}",
                f"최종 체력: {self.player_stats['hp']}",
            ]
            for i, stat in enumerate(stats):
                stat_surf = font_small.render(stat, True, Colors.UI_TEXT_DIM)
                surface.blit(stat_surf, ((self.sw - stat_surf.get_width()) // 2,
                                       stats_y + i * 22))

            # 계속하기 안내
            if self.animation_timer > 1:
                hint = font_small.render("클릭하여 메인 메뉴로 돌아가기", True, Colors.UI_ACCENT)
                hint.set_alpha(int(128 + 127 * math.sin(self.animation_timer * 3)))
                surface.blit(hint, ((self.sw - hint.get_width()) // 2, self.sh - 50))
