"""
particles.py - 파티클 이펙트 시스템
비, 눈, 불, 연기, 피, 먼지 등 다양한 효과
"""
import pygame
import math
import random
from settings import Colors, GameSettings
from utils import lerp


class Particle:
    """개별 파티클"""
    __slots__ = ['x', 'y', 'vx', 'vy', 'life', 'max_life', 'size', 'color',
                 'gravity', 'friction', 'fade', 'shrink', 'glow']

    def __init__(self, x, y, vx, vy, life, size, color,
                 gravity=0, friction=1.0, fade=True, shrink=True, glow=False):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.size = size
        self.color = color
        self.gravity = gravity
        self.friction = friction
        self.fade = fade
        self.shrink = shrink
        self.glow = glow

    def update(self, dt):
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        self.vy += self.gravity * dt * 60
        self.vx *= self.friction
        self.vy *= self.friction
        self.life -= dt
        return self.life > 0

    @property
    def progress(self):
        return 1.0 - (self.life / self.max_life) if self.max_life > 0 else 1.0

    @property
    def alpha(self):
        if self.fade:
            return max(0, min(255, int(255 * (self.life / self.max_life))))
        return 255

    @property
    def current_size(self):
        if self.shrink:
            return max(0.5, self.size * (self.life / self.max_life))
        return self.size


class ParticleSystem:
    """파티클 시스템 관리자"""

    def __init__(self):
        self.particles = []
        self.max_particles = 500
        settings = GameSettings()
        quality_multipliers = {0: 0, 1: 0.3, 2: 0.7, 3: 1.0}
        self.quality = quality_multipliers.get(settings.particles_quality, 0.7)

    def update(self, dt):
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self, surface, camera=None):
        for p in self.particles:
            if camera:
                sx, sy = camera.world_to_screen(p.x / 32, p.y / 32)  # TILE_SIZE = 32
            else:
                sx, sy = int(p.x), int(p.y)

            sz = max(1, int(p.current_size))
            alpha = p.alpha

            if alpha <= 0 or sz <= 0:
                continue

            if len(p.color) >= 3:
                color = (*p.color[:3], alpha) if len(p.color) == 3 else (*p.color[:3], min(p.color[3], alpha))
            else:
                continue

            if p.glow and sz > 2:
                glow_sz = sz * 3
                glow_surf = pygame.Surface((glow_sz * 2, glow_sz * 2), pygame.SRCALPHA)
                glow_alpha = max(0, alpha // 3)
                pygame.draw.circle(glow_surf, (*color[:3], glow_alpha), (glow_sz, glow_sz), glow_sz)
                surface.blit(glow_surf, (sx - glow_sz, sy - glow_sz))

            if sz <= 1:
                try:
                    if 0 <= sx < surface.get_width() and 0 <= sy < surface.get_height():
                        surface.set_at((sx, sy), color)
                except (IndexError, TypeError):
                    pass
            else:
                ps = pygame.Surface((sz * 2, sz * 2), pygame.SRCALPHA)
                pygame.draw.circle(ps, color, (sz, sz), sz)
                surface.blit(ps, (sx - sz, sy - sz))

    def emit(self, emitter_func, count=1):
        """파티클 방출"""
        actual_count = max(1, int(count * self.quality))
        if len(self.particles) + actual_count > self.max_particles:
            actual_count = max(0, self.max_particles - len(self.particles))
        for _ in range(actual_count):
            p = emitter_func()
            if p:
                self.particles.append(p)

    def clear(self):
        self.particles.clear()


# ============================================================
# 파티클 이미터 (프리셋)
# ============================================================
class ParticleEmitters:
    """다양한 파티클 효과 프리셋"""

    @staticmethod
    def blood(x, y):
        """피 튀김"""
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1, 4)
        return Particle(
            x, y,
            math.cos(angle) * speed, math.sin(angle) * speed,
            life=random.uniform(0.3, 0.8),
            size=random.uniform(1, 3),
            color=Colors.BLOOD,
            gravity=0.2,
            friction=0.95,
        )

    @staticmethod
    def dust(x, y):
        """먼지"""
        return Particle(
            x + random.uniform(-5, 5), y + random.uniform(-2, 2),
            random.uniform(-0.5, 0.5), random.uniform(-1, -0.3),
            life=random.uniform(0.5, 1.2),
            size=random.uniform(1, 3),
            color=(180, 170, 150, 120),
            gravity=-0.02,
            friction=0.98,
        )

    @staticmethod
    def spark(x, y):
        """불꽃"""
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 6)
        return Particle(
            x, y,
            math.cos(angle) * speed, math.sin(angle) * speed,
            life=random.uniform(0.2, 0.5),
            size=random.uniform(1, 2),
            color=random.choice([Colors.FIRE_1, Colors.FIRE_2, Colors.FIRE_3]),
            gravity=0.1,
            friction=0.9,
            glow=True,
        )

    @staticmethod
    def smoke(x, y):
        """연기"""
        return Particle(
            x + random.uniform(-3, 3), y,
            random.uniform(-0.3, 0.3), random.uniform(-1.5, -0.5),
            life=random.uniform(1.0, 3.0),
            size=random.uniform(3, 8),
            color=(100, 100, 110, 100),
            gravity=-0.01,
            friction=0.99,
            shrink=False,
        )

    @staticmethod
    def ember(x, y, screen_height=720):
        """잔불 (메뉴용)"""
        return Particle(
            random.uniform(0, x * 2), screen_height + 10,
            random.uniform(-0.3, 0.3), random.uniform(-2, -0.5),
            life=random.uniform(3.0, 7.0),
            size=random.uniform(1, 3),
            color=random.choice([Colors.EMBER, Colors.FIRE_1, (255, 80, 30)]),
            gravity=-0.005,
            friction=0.999,
            glow=True,
        )

    @staticmethod
    def rain_drop(screen_width, wind=0):
        """빗방울"""
        return Particle(
            random.uniform(-50, screen_width + 50), -10,
            wind * 0.5 + random.uniform(-0.5, 0.5), random.uniform(8, 14),
            life=random.uniform(0.5, 1.5),
            size=random.uniform(1, 2),
            color=Colors.RAIN,
            gravity=0.1,
            friction=1.0,
            fade=True,
            shrink=False,
        )

    @staticmethod
    def snow_flake(screen_width):
        """눈송이"""
        return Particle(
            random.uniform(-20, screen_width + 20), -10,
            random.uniform(-1, 1), random.uniform(1, 3),
            life=random.uniform(4.0, 8.0),
            size=random.uniform(1, 3),
            color=Colors.SNOW,
            gravity=0.0,
            friction=0.99,
            shrink=False,
        )

    @staticmethod
    def fog_wisp(screen_width, screen_height):
        """안개"""
        return Particle(
            random.uniform(0, screen_width), random.uniform(0, screen_height),
            random.uniform(-0.2, 0.2), random.uniform(-0.1, 0.1),
            life=random.uniform(3.0, 6.0),
            size=random.uniform(20, 50),
            color=Colors.FOG,
            gravity=0,
            friction=0.999,
            shrink=False,
        )

    @staticmethod
    def hit_effect(x, y):
        """타격 이펙트"""
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1, 3)
        return Particle(
            x, y,
            math.cos(angle) * speed, math.sin(angle) * speed,
            life=random.uniform(0.1, 0.3),
            size=random.uniform(2, 4),
            color=(255, 255, 200),
            gravity=0,
            friction=0.8,
            glow=True,
        )

    @staticmethod
    def pickup_sparkle(x, y):
        """아이템 획득 반짝임"""
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(0.5, 2)
        return Particle(
            x, y,
            math.cos(angle) * speed, math.sin(angle) * speed - 1,
            life=random.uniform(0.3, 0.8),
            size=random.uniform(1, 3),
            color=random.choice([(255, 255, 100), (100, 255, 255), (255, 200, 50)]),
            gravity=-0.05,
            friction=0.95,
            glow=True,
        )

    @staticmethod
    def footstep_dust(x, y):
        """발자국 먼지"""
        return Particle(
            x + random.uniform(-3, 3), y + random.uniform(-1, 1),
            random.uniform(-0.3, 0.3), random.uniform(-0.5, -0.1),
            life=random.uniform(0.3, 0.6),
            size=random.uniform(1, 2),
            color=(160, 150, 130, 80),
            gravity=-0.01,
            friction=0.95,
        )
