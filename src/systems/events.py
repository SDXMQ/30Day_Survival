"""
events.py - 이벤트 시스템, 퀘스트, 엔딩
원본 게임의 모든 이벤트를 확장 포함
"""
import random
from items import generate_loot


class EventType:
    WEATHER = "weather"
    RAID = "raid"
    MERCHANT = "merchant"
    SUPPLY_DROP = "supply_drop"
    SURVIVOR = "survivor"
    MILITARY_CONVOY = "military_convoy"
    HORDE = "horde"
    MYSTERY = "mystery"
    RADIO_SIGNAL = "radio_signal"


# ============================================================
# 이벤트 정의 (확장 가능)
# ============================================================
RANDOM_EVENTS = {
    "폭우_피해": {
        "type": EventType.WEATHER,
        "title": "폭우가 몰아칩니다",
        "description": "은신처에 비가 새어 들어왔습니다. 습기로 인해 컨디션이 나빠집니다.",
        "effects": {"stress": 5, "hp": -5},
        "chance": 0.08,
        "day_min": 1,
    },
    "맑은_날": {
        "type": EventType.WEATHER,
        "title": "맑은 하늘",
        "description": "오랜만의 맑은 날씨입니다. 마음이 한결 가벼워집니다.",
        "effects": {"stress": -10},
        "chance": 0.1,
        "day_min": 1,
    },
    "야간_습격": {
        "type": EventType.RAID,
        "title": "야간 습격!",
        "description": "밤사이 좀비들이 은신처를 공격했습니다!",
        "effects": {"stress": 15},
        "defense_check": 20,
        "defense_fail_effects": {"hp": -20, "stress": 25},
        "defense_success_msg": "튼튼한 바리케이드 덕분에 좀비들이 물러갔습니다!",
        "defense_fail_msg": "방어도가 낮아 일부 피해를 입었습니다.",
        "chance": 0.1,
        "day_min": 3,
    },
    "물자_투하": {
        "type": EventType.SUPPLY_DROP,
        "title": "물자 투하 발견!",
        "description": "근처에서 군용 물자 투하 상자를 발견했습니다!",
        "loot": ["식량통조림", "생수", "구급상자", "탄약"],
        "chance": 0.04,
        "day_min": 5,
    },
    "좀비_웨이브": {
        "type": EventType.HORDE,
        "title": "좀비 웨이브!",
        "description": "대규모 좀비 무리가 이 지역으로 이동 중입니다!",
        "zombie_count": 8,
        "chance": 0.06,
        "day_min": 7,
    },
    "군사_호송대": {
        "type": EventType.MILITARY_CONVOY,
        "title": "군사 호송대 잔해",
        "description": "파괴된 군용 트럭을 발견했습니다. 물자가 남아있을 수 있습니다.",
        "loot": ["탄약", "구급상자", "라디오 부품"],
        "chance": 0.03,
        "day_min": 10,
    },
    "무전_신호": {
        "type": EventType.RADIO_SIGNAL,
        "title": "미약한 무전 신호",
        "description": "라디오에서 미약한 신호가 잡힙니다... '...구조대... 30일 후... 좌표...'",
        "effects": {"stress": -10},
        "chance": 0.05,
        "day_min": 1,
    },
    "미스터리_상자": {
        "type": EventType.MYSTERY,
        "title": "의문의 상자",
        "description": "길가에 깔끔하게 포장된 상자가 놓여 있습니다. 열어볼까요?",
        "chance": 0.04,
        "day_min": 3,
    },
    "오래된_일기": {
        "type": EventType.MYSTERY,
        "title": "오래된 일기장",
        "description": "이전 생존자가 남긴 일기장을 발견했습니다. 유용한 정보가 적혀있습니다.",
        "effects": {"stress": -5},
        "chance": 0.06,
        "day_min": 1,
    },
}


class GameEvent:
    """게임 이벤트"""

    def __init__(self, event_id, event_data):
        self.id = event_id
        self.data = event_data
        self.title = event_data.get("title", "이벤트")
        self.description = event_data.get("description", "")
        self.active = True
        self.display_timer = 5.0  # 표시 시간

    def apply_effects(self, player):
        effects = self.data.get("effects", {})
        if "hp" in effects:
            player.hp += effects["hp"]
        if "stress" in effects:
            player.stress += effects["stress"]
        if "hunger" in effects:
            player.hunger += effects["hunger"]
        if "thirst" in effects:
            player.thirst += effects["thirst"]

    def get_loot(self):
        return self.data.get("loot", [])


class EventSystem:
    """이벤트 관리 시스템"""

    def __init__(self, difficulty_settings=None):
        self.diff = difficulty_settings or {}
        self.active_events = []
        self.event_history = []
        self.event_log = []  # 최근 이벤트 로그 (UI 표시용)
        self.check_timer = 0
        self.check_interval = 30  # 30초마다 이벤트 체크

    def update(self, dt, player, current_day):
        self.check_timer += dt

        # 이벤트 표시 타이머
        for event in self.active_events:
            event.display_timer -= dt
        self.active_events = [e for e in self.active_events if e.display_timer > 0]

        # 이벤트 로그 타이머
        self.event_log = [(msg, t - dt) for msg, t in self.event_log if t > 0]

        # 주기적 이벤트 체크
        if self.check_timer >= self.check_interval:
            self.check_timer = 0
            self._check_random_events(player, current_day)

    def _check_random_events(self, player, current_day):
        for event_id, event_data in RANDOM_EVENTS.items():
            if current_day < event_data.get("day_min", 1):
                continue

            chance = event_data.get("chance", 0) * self.diff.get("night_danger", 1.0)
            if random.random() < chance:
                event = GameEvent(event_id, event_data)

                # 방어 체크가 필요한 이벤트
                if "defense_check" in event_data:
                    if player.shelter_defense >= event_data["defense_check"]:
                        self.add_log(f"✓ {event.title}: {event_data['defense_success_msg']}")
                    else:
                        effects = event_data.get("defense_fail_effects", {})
                        for stat, val in effects.items():
                            if stat == "hp":
                                player.hp += val
                            elif stat == "stress":
                                player.stress += val
                        self.add_log(f"✗ {event.title}: {event_data['defense_fail_msg']}")
                else:
                    event.apply_effects(player)
                    # 루트
                    for item in event.get_loot():
                        player.inventory.add_item(item)
                    self.add_log(f"★ {event.title}: {event.description}")

                self.active_events.append(event)
                self.event_history.append(event_id)
                break  # 한 번에 하나씩

    def add_log(self, message, duration=8.0):
        """이벤트 로그 추가"""
        self.event_log.insert(0, (message, duration))
        if len(self.event_log) > 8:
            self.event_log = self.event_log[:8]

    def trigger_event(self, event_id, player):
        """수동 이벤트 트리거"""
        event_data = RANDOM_EVENTS.get(event_id)
        if event_data:
            event = GameEvent(event_id, event_data)
            event.apply_effects(player)
            self.active_events.append(event)
            self.event_history.append(event_id)
            return event
        return None

    def check_new_day_events(self, player, current_day):
        """새로운 날 시작 이벤트"""
        events = []

        # 야간 습격 체크
        raid_chance = self.diff.get("raid_chance", 0.1) * (1 + current_day * 0.02)
        if random.random() < raid_chance:
            events.append(self.trigger_event("야간_습격", player))

        # 날씨 이벤트
        weather_roll = random.random()
        if weather_roll < 0.15:
            events.append(self.trigger_event("폭우_피해", player))
        elif weather_roll < 0.3:
            events.append(self.trigger_event("맑은_날", player))

        return [e for e in events if e is not None]


# ============================================================
# 엔딩 시스템
# ============================================================
ENDINGS = {
    "진엔딩": {
        "title": "진(眞) 엔딩: 인류의 희망, 완벽한 사령관",
        "description": "라디오 부품 3개로 장거리 무전기를 조립해 정확한 좌표를 송신했습니다.\n헬리콥터가 은신처 위로 정확히 하강합니다.\n당신의 철저한 생존 일지는 후세에 백과사전으로 남게 될 것입니다.",
        "condition": lambda p: p.inventory.has_item("장거리 무전기") or p.inventory.count_item("라디오 부품") >= 3,
        "priority": 10,
    },
    "해피엔딩": {
        "title": "해피 엔딩: 기지를 발휘한 드라마틱한 구출",
        "description": "무전기는 불안정했지만, 손전등으로 강렬한 SOS 신호를 보냈습니다!\n수색대가 당신을 발견하고 구출합니다.",
        "condition": lambda p: (p.inventory.count_item("라디오 부품") >= 1 and
                               p.inventory.has_item("손전등") and
                               p.inventory.has_item("비상용 배터리")),
        "priority": 8,
    },
    "노말A_철의군주": {
        "title": "노말 엔딩: 폐허 위에 군림하는 철의 군주",
        "description": "헬기는 지나갔지만, 당신의 은신처는 좀비 군단도 뚫지 못하는 요새입니다.\n풍부한 식량과 함께, 이 지역의 왕이 되기로 결심합니다.",
        "condition": lambda p: p.shelter_defense >= 50 and p.inventory.has_item("식량통조림"),
        "priority": 5,
    },
    "노말B_매드맥스": {
        "title": "노말 엔딩: 매드맥스, 끝없는 여정",
        "description": "구조는 실패했지만, 무기와 방어구로 완전 무장한 채 밖으로 걸어나갑니다.\n또 다른 여정이 시작됩니다...",
        "condition": lambda p: p.hp >= 70 and p.equipped.get("weapon") and p.equipped.get("body"),
        "priority": 4,
    },
    "히든_좀비헌터": {
        "title": "히든 엔딩: 전설의 좀비 사냥꾼",
        "description": "100마리 이상의 좀비를 처치한 당신의 이름은 전설이 됩니다.\n생존자들 사이에서 당신은 '사신'이라 불립니다.",
        "condition": lambda p: p.killed_zombies >= 100,
        "priority": 7,
    },
    "히든_과학자": {
        "title": "히든 엔딩: 진실을 밝혀낸 자",
        "description": "군사 문서에서 감염의 원인을 밝혀냈습니다.\n이 진실은 인류를 구할 열쇠가 될 것입니다.",
        "condition": lambda p: p.inventory.has_item("군사 문서"),
        "priority": 6,
    },
    "히든_장인": {
        "title": "히든 엔딩: 폐허의 장인",
        "description": "20개 이상의 아이템을 직접 제작한 당신은 폐허에서의 삶의 달인이 됩니다.",
        "condition": lambda p: p.items_crafted >= 20,
        "priority": 6,
    },
    "배드엔딩": {
        "title": "배드 엔딩: 잊혀진 자의 고독한 최후",
        "description": "헬기가 지나가는 것을 허망하게 바라봅니다...\n라디오도, 빛도, 방어할 힘도 남아있지 않습니다.\n은신처 너머로 좀비 떼의 끔찍한 소리만이 귓가를 맴돕니다.",
        "condition": lambda p: True,  # 기본 엔딩
        "priority": 0,
    },
}


def determine_ending(player):
    """플레이어 상태에 따른 엔딩 결정"""
    possible_endings = []

    for ending_id, ending_data in ENDINGS.items():
        try:
            if ending_data["condition"](player):
                possible_endings.append((ending_data["priority"], ending_id, ending_data))
        except Exception:
            continue

    # 우선순위가 가장 높은 엔딩 선택
    possible_endings.sort(key=lambda x: x[0], reverse=True)

    if possible_endings:
        return possible_endings[0][1], possible_endings[0][2]

    return "배드엔딩", ENDINGS["배드엔딩"]
