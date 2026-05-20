"""
weather.py - 날씨 시스템 & 낮밤 주기
"""
import pygame
import math
import random
from settings import (Colors, GAME_HOURS_PER_DAY, DAWN_HOUR, DAY_HOUR,
                       DUSK_HOUR, NIGHT_HOUR)
from utils import lerp, lerp_color


class TimeSystem:
    """게임 시간 관리"""

    def __init__(self, day_length_minutes=12):
        self.day_length_seconds = day_length_minutes * 60
        self.seconds_per_game_hour = self.day_length_seconds / GAME_HOURS_PER_DAY
        self.current_day = 1
        self.current_hour = 8.0  # 오전 8시 시작
        self.total_elapsed = 0
        self.time_speed = 1.0  # 시간 배속

    def update(self, dt):
        game_dt = dt * self.time_speed
        hours_passed = game_dt / self.seconds_per_game_hour
        self.current_hour += hours_passed
        self.total_elapsed += game_dt

        if self.current_hour >= 24:
            self.current_hour -= 24
            self.current_day += 1

    @property
    def hour(self):
        return int(self.current_hour)

    @property
    def minute(self):
        return int((self.current_hour % 1) * 60)

    @property
    def time_string(self):
        return f"{self.hour:02d}:{self.minute:02d}"

    @property
    def day_progress(self):
        """하루 진행도 (0~1)"""
        return self.current_hour / 24.0

    @property
    def is_night(self):
        return self.current_hour >= NIGHT_HOUR or self.current_hour < DAWN_HOUR

    @property
    def is_dawn(self):
        return DAWN_HOUR <= self.current_hour < DAY_HOUR

    @property
    def is_day(self):
        return DAY_HOUR <= self.current_hour < DUSK_HOUR

    @property
    def is_dusk(self):
        return DUSK_HOUR <= self.current_hour < NIGHT_HOUR

    @property
    def period_name(self):
        if self.is_dawn:
            return "새벽"
        elif self.is_day:
            return "낮"
        elif self.is_dusk:
            return "저녁"
        else:
            return "밤"

    def get_ambient_color(self):
        """현재 시간에 따른 환경광 색상 (오버레이용)"""
        h = self.current_hour

        if h < DAWN_HOUR:  # 깊은 밤
            return (10, 10, 35, 160)
        elif h < DAY_HOUR:  # 새벽
            t = (h - DAWN_HOUR) / (DAY_HOUR - DAWN_HOUR)
            alpha = max(0, min(255, int(lerp(160, 0, t))))
            color = lerp_color((10, 10, 35), (255, 200, 150), t)
            return (int(color[0]), int(color[1]), int(color[2]), alpha)
        elif h < DUSK_HOUR:  # 낮
            return (0, 0, 0, 0)
        elif h < NIGHT_HOUR:  # 석양
            t = (h - DUSK_HOUR) / (NIGHT_HOUR - DUSK_HOUR)
            alpha = max(0, min(255, int(lerp(0, 160, t))))
            color = lerp_color((200, 120, 60), (10, 10, 35), t)
            return (int(color[0]), int(color[1]), int(color[2]), alpha)
        else:  # 밤
            return (10, 10, 35, 160)

    def get_sky_color(self):
        """하늘 색상"""
        h = self.current_hour
        if h < DAWN_HOUR:
            return Colors.SKY_NIGHT
        elif h < DAY_HOUR:
            t = (h - DAWN_HOUR) / (DAY_HOUR - DAWN_HOUR)
            return lerp_color(Colors.SKY_NIGHT, Colors.SKY_DAWN, t)
        elif h < (DAY_HOUR + DUSK_HOUR) / 2:
            t = (h - DAY_HOUR) / ((DAY_HOUR + DUSK_HOUR) / 2 - DAY_HOUR)
            return lerp_color(Colors.SKY_DAWN, Colors.SKY_DAY, t)
        elif h < DUSK_HOUR:
            t = (h - (DAY_HOUR + DUSK_HOUR) / 2) / (DUSK_HOUR - (DAY_HOUR + DUSK_HOUR) / 2)
            return lerp_color(Colors.SKY_DAY, Colors.SKY_DUSK, t)
        elif h < NIGHT_HOUR:
            t = (h - DUSK_HOUR) / (NIGHT_HOUR - DUSK_HOUR)
            return lerp_color(Colors.SKY_DUSK, Colors.SKY_NIGHT, t)
        else:
            return Colors.SKY_NIGHT


class WeatherType:
    CLEAR = "맑음"
    CLOUDY = "흐림"
    RAIN = "비"
    HEAVY_RAIN = "폭우"
    FOG = "안개"
    STORM = "폭풍"


class WeatherSystem:
    """날씨 시스템"""

    def __init__(self, variability=1.0):
        self.variability = variability
        self.current_weather = WeatherType.CLEAR
        self.target_weather = WeatherType.CLEAR
        self.transition_timer = 0
        self.transition_duration = 5.0  # 날씨 변환 시간
        self.weather_duration = 0  # 현재 날씨 지속 시간
        self.weather_timer = 0
        self.intensity = 0.0  # 현재 날씨 강도 (0~1)

        # 날씨별 확률 가중치
        self.weather_weights = {
            WeatherType.CLEAR: 35,
            WeatherType.CLOUDY: 25,
            WeatherType.RAIN: 18,
            WeatherType.HEAVY_RAIN: 8,
            WeatherType.FOG: 10,
            WeatherType.STORM: 4,
        }

        self._randomize_weather()

    def _randomize_weather(self):
        """랜덤 날씨 선택"""
        weights = []
        weathers = []
        for w, weight in self.weather_weights.items():
            weathers.append(w)
            weights.append(weight * self.variability if w != WeatherType.CLEAR else weight)

        total = sum(weights)
        r = random.uniform(0, total)
        cumulative = 0
        for i, weight in enumerate(weights):
            cumulative += weight
            if r <= cumulative:
                self.target_weather = weathers[i]
                break

        self.weather_duration = random.uniform(60, 300) * self.variability
        self.weather_timer = 0
        self.transition_timer = 0

    def update(self, dt):
        self.weather_timer += dt

        # 날씨 전환
        if self.transition_timer < self.transition_duration:
            self.transition_timer += dt
            t = min(1.0, self.transition_timer / self.transition_duration)
            if self.current_weather != self.target_weather:
                self.intensity = t
                if t >= 1.0:
                    self.current_weather = self.target_weather
        else:
            self.intensity = 1.0

        # 날씨 종료 체크
        if self.weather_timer >= self.weather_duration:
            self._randomize_weather()

    def get_visibility_modifier(self):
        """시야 거리 수정치"""
        modifiers = {
            WeatherType.CLEAR: 1.0,
            WeatherType.CLOUDY: 0.9,
            WeatherType.RAIN: 0.7,
            WeatherType.HEAVY_RAIN: 0.5,
            WeatherType.FOG: 0.3,
            WeatherType.STORM: 0.4,
        }
        return modifiers.get(self.current_weather, 1.0)

    def get_movement_modifier(self):
        """이동 속도 수정치"""
        modifiers = {
            WeatherType.CLEAR: 1.0,
            WeatherType.CLOUDY: 1.0,
            WeatherType.RAIN: 0.9,
            WeatherType.HEAVY_RAIN: 0.75,
            WeatherType.FOG: 0.95,
            WeatherType.STORM: 0.7,
        }
        return modifiers.get(self.current_weather, 1.0)

    def get_danger_modifier(self):
        """위험도 수정치"""
        modifiers = {
            WeatherType.CLEAR: 1.0,
            WeatherType.CLOUDY: 1.1,
            WeatherType.RAIN: 1.2,
            WeatherType.HEAVY_RAIN: 1.5,
            WeatherType.FOG: 1.4,
            WeatherType.STORM: 1.8,
        }
        return modifiers.get(self.current_weather, 1.0)

    def draw_effects(self, surface, dt):
        """날씨 시각 효과 렌더링"""
        w, h = surface.get_size()

        if self.current_weather == WeatherType.RAIN or self.current_weather == WeatherType.HEAVY_RAIN:
            self._draw_rain(surface, w, h)
        elif self.current_weather == WeatherType.FOG:
            self._draw_fog(surface, w, h)
        elif self.current_weather == WeatherType.STORM:
            self._draw_storm(surface, w, h)
        elif self.current_weather == WeatherType.CLOUDY:
            self._draw_clouds(surface, w, h)

    def _draw_rain(self, surface, w, h):
        count = 80 if self.current_weather == WeatherType.HEAVY_RAIN else 35
        count = int(count * self.intensity)
        rain_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        for _ in range(count):
            rx = random.randint(0, w)
            ry = random.randint(0, h)
            length = random.randint(5, 15)
            alpha = random.randint(60, 140)
            wind_offset = 3 if self.current_weather == WeatherType.HEAVY_RAIN else 1
            pygame.draw.line(rain_surf, (150, 180, 220, alpha),
                           (rx, ry), (rx + wind_offset, ry + length), 1)
        surface.blit(rain_surf, (0, 0))

    def _draw_fog(self, surface, w, h):
        fog_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        alpha = int(60 * self.intensity)
        fog_surf.fill((180, 185, 195, alpha))
        # 안개 패턴
        for _ in range(5):
            fx = random.randint(-50, w + 50)
            fy = random.randint(-50, h + 50)
            fr = random.randint(80, 200)
            fa = random.randint(10, 30)
            pygame.draw.circle(fog_surf, (200, 205, 215, fa), (fx, fy), fr)
        surface.blit(fog_surf, (0, 0))

    def _draw_storm(self, surface, w, h):
        # 비 + 가끔 번개
        self._draw_rain(surface, w, h)
        if random.random() < 0.005 * self.intensity:
            flash = pygame.Surface((w, h), pygame.SRCALPHA)
            flash.fill((255, 255, 255, random.randint(100, 200)))
            surface.blit(flash, (0, 0))

    def _draw_clouds(self, surface, w, h):
        cloud_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        alpha = int(25 * self.intensity)
        cloud_surf.fill((150, 155, 165, alpha))
        surface.blit(cloud_surf, (0, 0))

    def draw_ambient(self, surface, time_system):
        """시간대별 환경광 오버레이"""
        ambient = time_system.get_ambient_color()
        if ambient[3] > 0:
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill(ambient)
            surface.blit(overlay, (0, 0))
