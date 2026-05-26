"""
utils.py - 유틸리티 함수, 수학 헬퍼, 노이즈 생성
"""
import math
import random
import hashlib


def lerp(a, b, t):
    """선형 보간"""
    return a + (b - a) * max(0, min(1, t))


def lerp_color(c1, c2, t):
    """색상 선형 보간"""
    t = max(0, min(1, t))
    r = int(c1[0] + (c2[0] - c1[0]) * t)
    g = int(c1[1] + (c2[1] - c1[1]) * t)
    b = int(c1[2] + (c2[2] - c1[2]) * t)
    if len(c1) > 3 and len(c2) > 3:
        a = int(c1[3] + (c2[3] - c1[3]) * t)
        return (r, g, b, a)
    return (r, g, b)


def clamp(value, min_val, max_val):
    """값을 범위로 제한"""
    return max(min_val, min(max_val, value))


def distance(x1, y1, x2, y2):
    """두 점 사이의 거리"""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def distance_sq(x1, y1, x2, y2):
    """두 점 사이의 거리의 제곱 (루트 연산 방지용)"""
    return (x2 - x1) ** 2 + (y2 - y1) ** 2


def direction_to(x1, y1, x2, y2):
    """(x1,y1)에서 (x2,y2)로의 정규화된 방향 벡터"""
    dx = x2 - x1
    dy = y2 - y1
    d = math.sqrt(dx * dx + dy * dy)
    if d == 0:
        return (0, 0)
    return (dx / d, dy / d)


def angle_between(x1, y1, x2, y2):
    """두 점 사이의 각도(라디안)"""
    return math.atan2(y2 - y1, x2 - x1)


def ease_in_out(t):
    """이즈 인아웃 커브"""
    t = max(0, min(1, t))
    return t * t * (3 - 2 * t)


def ease_out_cubic(t):
    """이즈 아웃 큐빅"""
    t = max(0, min(1, t))
    return 1 - (1 - t) ** 3


def ease_in_cubic(t):
    """이즈 인 큐빅"""
    t = max(0, min(1, t))
    return t ** 3


def ease_out_elastic(t):
    """이즈 아웃 일래스틱"""
    if t == 0 or t == 1:
        return t
    return pow(2, -10 * t) * math.sin((t * 10 - 0.75) * (2 * math.pi) / 3) + 1


# ============================================================
# 심플 퍼린 노이즈 (월드 생성용)
# ============================================================
class SimplexNoise:
    """간단한 2D 노이즈 생성기 (시드 기반)"""

    def __init__(self, seed=None):
        if seed is None:
            seed = random.randint(0, 2 ** 31)
        self.seed = seed
        self.perm = list(range(256))
        rng = random.Random(seed)
        rng.shuffle(self.perm)
        self.perm = self.perm + self.perm  # 더블링

    def _grad(self, hash_val, x, y):
        h = hash_val & 3
        if h == 0:
            return x + y
        elif h == 1:
            return -x + y
        elif h == 2:
            return x - y
        else:
            return -x - y

    def _fade(self, t):
        return t * t * t * (t * (t * 6 - 15) + 10)

    def noise2d(self, x, y):
        """2D 노이즈 값 반환 (-1 ~ 1)"""
        xi = int(math.floor(x)) & 255
        yi = int(math.floor(y)) & 255
        xf = x - math.floor(x)
        yf = y - math.floor(y)

        u = self._fade(xf)
        v = self._fade(yf)

        aa = self.perm[self.perm[xi] + yi]
        ab = self.perm[self.perm[xi] + yi + 1]
        ba = self.perm[self.perm[xi + 1] + yi]
        bb = self.perm[self.perm[xi + 1] + yi + 1]

        x1 = lerp(self._grad(aa, xf, yf), self._grad(ba, xf - 1, yf), u)
        x2 = lerp(self._grad(ab, xf, yf - 1), self._grad(bb, xf - 1, yf - 1), u)

        return lerp(x1, x2, v)

    def octave_noise(self, x, y, octaves=4, persistence=0.5, scale=1.0):
        """옥타브 노이즈 (여러 레이어 합산)"""
        total = 0
        frequency = scale
        amplitude = 1
        max_value = 0
        for _ in range(octaves):
            total += self.noise2d(x * frequency, y * frequency) * amplitude
            max_value += amplitude
            amplitude *= persistence
            frequency *= 2
        return total / max_value


# ============================================================
# 타이머 유틸리티
# ============================================================
class Timer:
    """범용 타이머"""

    def __init__(self, duration, callback=None, repeat=False):
        self.duration = duration
        self.callback = callback
        self.repeat = repeat
        self.elapsed = 0
        self.active = True
        self.finished = False

    def update(self, dt):
        if not self.active or self.finished:
            return
        self.elapsed += dt
        if self.elapsed >= self.duration:
            if self.callback:
                self.callback()
            if self.repeat:
                self.elapsed -= self.duration
            else:
                self.finished = True
                self.active = False

    def reset(self):
        self.elapsed = 0
        self.finished = False
        self.active = True

    @property
    def progress(self):
        return min(1.0, self.elapsed / self.duration) if self.duration > 0 else 1.0


class CooldownManager:
    """쿨다운 관리"""

    def __init__(self):
        self.cooldowns = {}

    def set_cooldown(self, name, duration):
        self.cooldowns[name] = duration

    def update(self, dt):
        to_remove = []
        for name, remaining in self.cooldowns.items():
            self.cooldowns[name] = remaining - dt
            if self.cooldowns[name] <= 0:
                to_remove.append(name)
        for name in to_remove:
            del self.cooldowns[name]

    def is_ready(self, name):
        return name not in self.cooldowns

    def get_remaining(self, name):
        return max(0, self.cooldowns.get(name, 0))


# ============================================================
# 시드 기반 해시
# ============================================================
def hash_position(x, y, seed=0):
    """위치 기반 결정적 해시값"""
    h = hashlib.md5(f"{x},{y},{seed}".encode()).hexdigest()
    return int(h[:8], 16)


def seeded_random(x, y, seed=0):
    """위치 기반 0~1 난수"""
    return (hash_position(x, y, seed) % 10000) / 10000.0


# ============================================================
# 텍스트 유틸리티
# ============================================================
def wrap_text(text, font, max_width):
    """텍스트를 지정된 너비로 줄바꿈"""
    words = text.split(' ')
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


def format_time(hours, minutes):
    """게임 시간을 문자열로"""
    return f"{int(hours):02d}:{int(minutes):02d}"
