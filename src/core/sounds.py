"""
sounds.py - 코드 기반 사운드 효과 (pygame mixer)
"""
import pygame
import math
import struct
import array
import io


class SoundGenerator:
    """절차적 사운드 생성"""

    _cache = {}
    _initialized = False

    @classmethod
    def init(cls):
        if cls._initialized:
            return
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            cls._initialized = True
        except Exception:
            pass

    @classmethod
    def _generate_tone(cls, frequency, duration, volume=0.3, wave_type="sine", fade_out=True):
        """기본 톤 생성"""
        sample_rate = 22050
        num_samples = int(sample_rate * duration)
        buf = array.array('h', [0] * num_samples)

        for i in range(num_samples):
            t = i / sample_rate
            if wave_type == "sine":
                value = math.sin(2 * math.pi * frequency * t)
            elif wave_type == "square":
                value = 1 if math.sin(2 * math.pi * frequency * t) > 0 else -1
            elif wave_type == "noise":
                import random
                value = random.uniform(-1, 1)
            elif wave_type == "sawtooth":
                value = 2 * (t * frequency % 1) - 1
            else:
                value = math.sin(2 * math.pi * frequency * t)

            # 페이드 아웃
            if fade_out:
                envelope = 1.0 - (i / num_samples)
            else:
                envelope = 1.0

            # 어택
            if i < num_samples * 0.05:
                envelope *= (i / (num_samples * 0.05))

            buf[i] = int(value * volume * 32767 * envelope)

        sound = pygame.mixer.Sound(buffer=buf)
        return sound

    @classmethod
    def get_sound(cls, sound_name):
        if not cls._initialized:
            cls.init()
        if not cls._initialized:
            return None

        if sound_name not in cls._cache:
            cls._cache[sound_name] = cls._create_sound(sound_name)
        return cls._cache[sound_name]

    @classmethod
    def _create_sound(cls, name):
        try:
            if name == "hit_melee":
                return cls._generate_tone(150, 0.15, 0.4, "square")
            elif name == "hit_ranged":
                return cls._generate_tone(800, 0.08, 0.3, "noise")
            elif name == "player_hurt":
                return cls._generate_tone(200, 0.3, 0.3, "sawtooth")
            elif name == "zombie_die":
                return cls._generate_tone(100, 0.4, 0.3, "sawtooth")
            elif name == "pickup":
                return cls._generate_tone(600, 0.1, 0.2, "sine")
            elif name == "craft_complete":
                return cls._generate_tone(800, 0.15, 0.2, "sine")
            elif name == "menu_hover":
                return cls._generate_tone(400, 0.05, 0.1, "sine")
            elif name == "menu_select":
                return cls._generate_tone(500, 0.1, 0.15, "sine")
            elif name == "door_open":
                return cls._generate_tone(250, 0.2, 0.2, "square")
            elif name == "footstep":
                return cls._generate_tone(80, 0.05, 0.1, "noise")
            elif name == "alert":
                return cls._generate_tone(700, 0.3, 0.3, "square")
            elif name == "game_over":
                return cls._generate_tone(150, 0.8, 0.4, "sawtooth")
            elif name == "day_start":
                return cls._generate_tone(440, 0.3, 0.2, "sine")
            else:
                return cls._generate_tone(440, 0.1, 0.1)
        except Exception:
            return None

    @classmethod
    def play(cls, sound_name, volume=1.0):
        sound = cls.get_sound(sound_name)
        if sound:
            try:
                sound.set_volume(volume)
                sound.play()
            except Exception:
                pass
