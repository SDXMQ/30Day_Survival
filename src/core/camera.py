"""
camera.py - 카메라 시스템 (부드러운 추적, 줌, 화면 흔들림)
"""
import random
import math
from settings import TILE_SIZE, GameSettings
from utils import lerp


class Camera:
    """2D 카메라 (부드러운 추적, 줌, 셰이크 지원)"""

    def __init__(self):
        settings = GameSettings()
        self.x = 0.0
        self.y = 0.0
        self.target_x = 0.0
        self.target_y = 0.0
        self.width = settings.width
        self.height = settings.height
        self.zoom = 1.0
        self.target_zoom = 1.0
        self.smoothness = 0.08  # 카메라 추적 부드러움 (0~1, 낮을수록 부드러움)

        # 화면 흔들림
        self.shake_intensity = 0
        self.shake_duration = 0
        self.shake_timer = 0
        self.shake_offset_x = 0
        self.shake_offset_y = 0

    def set_target(self, world_x, world_y):
        """카메라 추적 대상 설정 (월드 좌표)"""
        self.target_x = world_x * TILE_SIZE - self.width / (2 * self.zoom)
        self.target_y = world_y * TILE_SIZE - self.height / (2 * self.zoom)

    def update(self, dt):
        """카메라 위치 업데이트"""
        # 부드러운 추적
        self.x = lerp(self.x, self.target_x, self.smoothness)
        self.y = lerp(self.y, self.target_y, self.smoothness)

        # 줌 보간
        self.zoom = lerp(self.zoom, self.target_zoom, 0.1)

        # 화면 흔들림
        if self.shake_timer > 0:
            self.shake_timer -= dt
            progress = self.shake_timer / self.shake_duration if self.shake_duration > 0 else 0
            intensity = self.shake_intensity * progress
            self.shake_offset_x = random.uniform(-intensity, intensity)
            self.shake_offset_y = random.uniform(-intensity, intensity)
        else:
            self.shake_offset_x = lerp(self.shake_offset_x, 0, 0.3)
            self.shake_offset_y = lerp(self.shake_offset_y, 0, 0.3)

    def shake(self, intensity=5, duration=0.3):
        """카메라 흔들림 트리거"""
        self.shake_intensity = intensity
        self.shake_duration = duration
        self.shake_timer = duration

    def world_to_screen(self, world_x, world_y):
        """월드 좌표 → 화면 좌표"""
        sx = (world_x * TILE_SIZE - self.x) * self.zoom + self.shake_offset_x
        sy = (world_y * TILE_SIZE - self.y) * self.zoom + self.shake_offset_y
        return (int(sx), int(sy))

    def screen_to_world(self, screen_x, screen_y):
        """화면 좌표 → 월드 좌표"""
        wx = (screen_x - self.shake_offset_x) / self.zoom + self.x
        wy = (screen_y - self.shake_offset_y) / self.zoom + self.y
        return (wx / TILE_SIZE, wy / TILE_SIZE)

    def get_visible_area(self):
        """화면에 보이는 타일 범위 반환 (tile_x1, tile_y1, tile_x2, tile_y2)"""
        margin = 2  # 여유 타일
        x1 = int(self.x / TILE_SIZE) - margin
        y1 = int(self.y / TILE_SIZE) - margin
        x2 = int((self.x + self.width / self.zoom) / TILE_SIZE) + margin
        y2 = int((self.y + self.height / self.zoom) / TILE_SIZE) + margin
        return (x1, y1, x2, y2)

    def is_visible(self, world_x, world_y, margin=2):
        """해당 월드 좌표가 화면에 보이는지 확인"""
        x1, y1, x2, y2 = self.get_visible_area()
        return x1 - margin <= world_x <= x2 + margin and y1 - margin <= world_y <= y2 + margin

    def resize(self, width, height):
        """화면 크기 변경 시"""
        self.width = width
        self.height = height
