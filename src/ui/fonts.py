import pygame
import math
from settings import Colors, RESOLUTION_OPTIONS, DIFFICULTY_PRESETS, DEFAULT_WORLD_SETTINGS, GameSettings, TILE_SIZE
from renderer import draw_rounded_rect, draw_gradient_rect, draw_glow, ItemIconRenderer
from items import ITEM_DATABASE, ItemCategory
from crafting import CRAFTING_RECIPES, RECIPE_CATEGORIES
from utils import wrap_text, ease_out_cubic, lerp


class FontManager:
    """폰트 관리"""
    _fonts = {}
    _initialized = False

    @classmethod
    def init(cls):
        if cls._initialized:
            return
        cls._initialized = True
        try:
            # 한국어 지원 폰트
            font_candidates = [
                "malgun gothic", "맑은 고딕", "gulim", "dotum",
                "NanumGothic", "arial", None
            ]
            cls._base_font = None
            for font_name in font_candidates:
                try:
                    test = pygame.font.SysFont(font_name, 16)
                    if test:
                        cls._base_font = font_name
                        break
                except Exception:
                    continue
        except Exception:
            cls._base_font = None

    @classmethod
    def get(cls, size):
        if not cls._initialized:
            cls.init()
        if size not in cls._fonts:
            try:
                cls._fonts[size] = pygame.font.SysFont(cls._base_font, size)
            except Exception:
                cls._fonts[size] = pygame.font.Font(None, size)
        return cls._fonts[size]

