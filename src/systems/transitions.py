"""
transitions.py - 화면 전환 효과
페이드, 와이프, 디졸브 등
"""
import pygame
import math
from utils import ease_in_out, ease_out_cubic


class Transition:
    """화면 전환 효과 기본 클래스"""

    def __init__(self, duration=0.5, on_complete=None):
        self.duration = duration
        self.elapsed = 0
        self.active = False
        self.phase = "in"  # "in" or "out"
        self.on_mid = None  # 전환 중간에 호출 (씬 전환)
        self.on_complete = on_complete
        self.mid_called = False

    def start(self, on_mid=None, on_complete=None):
        self.active = True
        self.elapsed = 0
        self.phase = "in"
        self.on_mid = on_mid
        self.on_complete = on_complete or self.on_complete
        self.mid_called = False

    def update(self, dt):
        if not self.active:
            return
        self.elapsed += dt
        progress = min(1.0, self.elapsed / self.duration)

        if progress >= 0.5 and not self.mid_called:
            self.mid_called = True
            if self.on_mid:
                self.on_mid()
            self.phase = "out"

        if progress >= 1.0:
            self.active = False
            if self.on_complete:
                self.on_complete()

    @property
    def progress(self):
        return min(1.0, self.elapsed / self.duration) if self.duration > 0 else 1.0

    def draw(self, surface):
        pass


class FadeTransition(Transition):
    """페이드 인/아웃 전환"""

    def __init__(self, duration=0.8, color=(0, 0, 0)):
        super().__init__(duration)
        self.color = color

    def draw(self, surface):
        if not self.active:
            return
        p = self.progress
        if p <= 0.5:
            alpha = int(255 * ease_out_cubic(p * 2))
        else:
            alpha = int(255 * (1 - ease_out_cubic((p - 0.5) * 2)))

        alpha = max(0, min(255, alpha))
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((*self.color, alpha))
        surface.blit(overlay, (0, 0))


class CircleWipeTransition(Transition):
    """원형 와이프 전환"""

    def __init__(self, duration=1.0, color=(0, 0, 0)):
        super().__init__(duration)
        self.color = color

    def draw(self, surface):
        if not self.active:
            return
        w, h = surface.get_size()
        max_radius = math.sqrt(w * w + h * h) / 2
        p = self.progress

        if p <= 0.5:
            radius = max_radius * (1 - ease_in_out(p * 2))
        else:
            radius = max_radius * ease_in_out((p - 0.5) * 2)

        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((*self.color, 255))
        cx, cy = w // 2, h // 2
        if radius > 0:
            pygame.draw.circle(overlay, (0, 0, 0, 0), (cx, cy), int(radius))
        surface.blit(overlay, (0, 0))


class SlideTransition(Transition):
    """슬라이드 전환"""

    def __init__(self, duration=0.6, direction="left"):
        super().__init__(duration)
        self.direction = direction
        self.old_surface = None

    def start(self, on_mid=None, on_complete=None, capture_surface=None):
        super().start(on_mid, on_complete)
        if capture_surface:
            self.old_surface = capture_surface.copy()

    def draw(self, surface):
        if not self.active:
            return
        w, h = surface.get_size()
        p = ease_in_out(self.progress)

        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(200 * (1 - abs(p * 2 - 1)))))
        surface.blit(overlay, (0, 0))


class DiamondTransition(Transition):
    """다이아몬드 패턴 전환"""

    def __init__(self, duration=1.0, color=(0, 0, 0)):
        super().__init__(duration)
        self.color = color

    def draw(self, surface):
        if not self.active:
            return
        w, h = surface.get_size()
        p = self.progress

        if p <= 0.5:
            size = ease_in_out(p * 2)
        else:
            size = 1 - ease_in_out((p - 0.5) * 2)

        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((*self.color, int(255 * size)))
        surface.blit(overlay, (0, 0))


class TransitionManager:
    """전환 효과 관리자"""

    def __init__(self):
        self.current = None
        self.transitions = {
            "fade": FadeTransition,
            "circle": CircleWipeTransition,
            "slide": SlideTransition,
            "diamond": DiamondTransition,
        }

    def start(self, transition_type="fade", duration=0.8, on_mid=None, on_complete=None, **kwargs):
        cls = self.transitions.get(transition_type, FadeTransition)
        self.current = cls(duration=duration, **kwargs)
        self.current.start(on_mid=on_mid, on_complete=on_complete)

    def update(self, dt):
        if self.current and self.current.active:
            self.current.update(dt)

    def draw(self, surface):
        if self.current and self.current.active:
            self.current.draw(surface)

    @property
    def is_active(self):
        return self.current is not None and self.current.active
