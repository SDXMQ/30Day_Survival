"""
items.py - 아이템 정의, 인벤토리 시스템
데이터 드리븐 방식으로 확장 용이성 확보
"""
import random


# ============================================================
# 아이템 카테고리
# ============================================================
class ItemCategory:
    FOOD = "식량"
    WATER = "음료"
    MEDICAL = "의료"
    WEAPON = "무기"
    TOOL = "도구"
    MATERIAL = "재료"
    EQUIPMENT = "장비"
    QUEST = "퀘스트"
    MISC = "기타"


# ============================================================
# 아이템 데이터베이스 (확장 가능)
# ============================================================
ITEM_DATABASE = {
    # === 식량 ===
    "식량통조림": {
        "category": ItemCategory.FOOD,
        "description": "밀봉된 고기 통조림. 유통기한은 이미 지났지만 아직 먹을 수 있다.",
        "stackable": True,
        "max_stack": 10,
        "weight": 0.5,
        "effects": {"hunger": 30, "hp": 5},
        "rarity": 0.6,  # 0~1 (높을수록 흔함)
    },
    "마른 빵": {
        "category": ItemCategory.FOOD,
        "description": "딱딱하게 굳은 빵. 배는 채울 수 있다.",
        "stackable": True,
        "max_stack": 10,
        "weight": 0.2,
        "effects": {"hunger": 15},
        "rarity": 0.7,
    },
    "에너지바": {
        "category": ItemCategory.FOOD,
        "description": "고칼로리 에너지바. 빠르게 에너지를 보충할 수 있다.",
        "stackable": True,
        "max_stack": 10,
        "weight": 0.1,
        "effects": {"hunger": 20, "stamina": 30},
        "rarity": 0.4,
    },
    "고기 구이": {
        "category": ItemCategory.FOOD,
        "description": "불에 구운 고기. 영양가가 높다.",
        "stackable": True,
        "max_stack": 5,
        "weight": 0.4,
        "effects": {"hunger": 45, "hp": 10},
        "rarity": 0.2,
    },
    "전투 식량": {
        "category": ItemCategory.FOOD,
        "description": "군용 전투 식량. 포만감을 크게 채워주고 에너지를 제공한다.",
        "stackable": True,
        "max_stack": 5,
        "weight": 0.8,
        "effects": {"hunger": 70, "stamina": 20, "hp": 10},
        "rarity": 0.08,
    },

    # === 음료 ===
    "에너지 드링크": {
        "category": ItemCategory.WATER,
        "description": "고농축 카페인 음료. 갈증을 해소하고 스태미나를 대폭 회복한다.",
        "stackable": True,
        "max_stack": 5,
        "weight": 0.3,
        "effects": {"thirst": 20, "stamina": 80, "stress": -10},
        "rarity": 0.12,
    },
    "생수": {
        "category": ItemCategory.WATER,
        "description": "깨끗한 생수 한 병.",
        "stackable": True,
        "max_stack": 10,
        "weight": 0.5,
        "effects": {"thirst": 35, "stress": -5},
        "rarity": 0.6,
    },
    "탄산음료": {
        "category": ItemCategory.WATER,
        "description": "따끈한 탄산음료. 갈증 해소와 기분 전환에 좋다.",
        "stackable": True,
        "max_stack": 5,
        "weight": 0.4,
        "effects": {"thirst": 25, "stress": -10},
        "rarity": 0.4,
    },
    "커피": {
        "category": ItemCategory.WATER,
        "description": "인스턴트 커피. 졸음을 쫓아준다.",
        "stackable": True,
        "max_stack": 5,
        "weight": 0.1,
        "effects": {"thirst": 15, "stamina": 40, "stress": -5},
        "rarity": 0.3,
    },

    # === 의료 ===
    "구급상자": {
        "category": ItemCategory.MEDICAL,
        "description": "기본적인 응급 처치 키트.",
        "stackable": True,
        "max_stack": 3,
        "weight": 1.0,
        "effects": {"hp": 40},
        "rarity": 0.3,
    },
    "진통제": {
        "category": ItemCategory.MEDICAL,
        "description": "강력한 진통제. 통증을 잠시 잊게 해준다.",
        "stackable": True,
        "max_stack": 5,
        "weight": 0.1,
        "effects": {"hp": 25, "stress": -15},
        "rarity": 0.35,
    },
    "고급 치료킷": {
        "category": ItemCategory.MEDICAL,
        "description": "전문 의료 키트. 중상도 치료 가능.",
        "stackable": True,
        "max_stack": 2,
        "weight": 1.5,
        "effects": {"hp": 70, "stress": -10},
        "rarity": 0.1,
        "crafted": True,
    },
    "약초": {
        "category": ItemCategory.MEDICAL,
        "description": "야생에서 채집한 약초. 크래프팅 재료.",
        "stackable": True,
        "max_stack": 10,
        "weight": 0.1,
        "effects": {"hp": 10},
        "rarity": 0.5,
    },
    "붕대": {
        "category": ItemCategory.MEDICAL,
        "description": "깨끗한 붕대. 출혈을 멈출 수 있다.",
        "stackable": True,
        "max_stack": 5,
        "weight": 0.1,
        "effects": {"hp": 15},
        "rarity": 0.5,
    },

    # === 무기 ===
    "무기": {
        "category": ItemCategory.WEAPON,
        "description": "쇠파이프. 기본적인 근접 무기.",
        "stackable": False,
        "weight": 2.0,
        "damage": 15,
        "range": 1.2,
        "attack_speed": 0.6,
        "type": "melee",
        "rarity": 0.3,
    },
    "파이프": {
        "category": ItemCategory.WEAPON,
        "description": "녹슨 쇠파이프.",
        "stackable": False,
        "weight": 1.5,
        "damage": 10,
        "range": 1.0,
        "attack_speed": 0.5,
        "type": "melee",
        "rarity": 0.5,
    },
    "나이프": {
        "category": ItemCategory.WEAPON,
        "description": "날카로운 사냥용 나이프.",
        "stackable": False,
        "weight": 0.5,
        "damage": 12,
        "range": 0.8,
        "attack_speed": 0.3,
        "type": "melee",
        "rarity": 0.35,
    },
    "도끼": {
        "category": ItemCategory.WEAPON,
        "description": "목재 벌목용 도끼. 강력하지만 느리다.",
        "stackable": False,
        "weight": 2.5,
        "damage": 25,
        "range": 1.1,
        "attack_speed": 0.9,
        "type": "melee",
        "rarity": 0.2,
    },
    "야구방망이": {
        "category": ItemCategory.WEAPON,
        "description": "알루미늄 야구방망이. 넓은 타격 범위.",
        "stackable": False,
        "weight": 1.8,
        "damage": 18,
        "range": 1.3,
        "attack_speed": 0.7,
        "type": "melee",
        "rarity": 0.25,
    },
    "권총": {
        "category": ItemCategory.WEAPON,
        "description": "9mm 권총. 탄약 필요.",
        "stackable": False,
        "weight": 1.0,
        "damage": 14,  # 밸런스 조정: 18 -> 14
        "range": 8.0,
        "attack_speed": 0.4,
        "type": "ranged",
        "ammo": "탄약",
        "rarity": 0.1,
    },
    "레버액션 소총": {
        "category": ItemCategory.WEAPON,
        "description": "클래식한 레버액션 소총. 강력하지만 재장전이 느리다.",
        "stackable": False,
        "weight": 3.5,
        "damage": 22,  # 밸런스 조정: 28 -> 22
        "range": 12.0,
        "attack_speed": 1.2,
        "type": "ranged",
        "ammo": "탄약",
        "rarity": 0.05,
    },
    "탄약": {
        "category": ItemCategory.WEAPON,
        "description": "9mm 탄약.",
        "stackable": True,
        "max_stack": 30,
        "weight": 0.05,
        "rarity": 0.15,
    },

    # === 장비 ===
    "가방": {
        "category": ItemCategory.EQUIPMENT,
        "description": "튼튼한 배낭. 인벤토리 최대 무게를 +15.0kg 늘려준다.",
        "stackable": False,
        "weight": 0.5,
        "equip_slot": "back",
        "weight_bonus": 15.0,
        "rarity": 0.15,
    },
    "방독면": {
        "category": ItemCategory.EQUIPMENT,
        "description": "오염된 공기를 차단하는 방독면.",
        "stackable": False,
        "weight": 0.8,
        "equip_slot": "head",
        "effects": {"poison_resist": True},
        "rarity": 0.2,
    },
    "방탄조끼": {
        "category": ItemCategory.EQUIPMENT,
        "description": "방탄 재질의 조끼. 대미지를 크게 줄여준다.",
        "stackable": False,
        "weight": 3.0,
        "equip_slot": "body",
        "defense": 15,
        "rarity": 0.1,
    },
    "운동화": {
        "category": ItemCategory.EQUIPMENT,
        "description": "가볍고 튼튼한 운동화. 이동 속도가 빨라진다.",
        "stackable": False,
        "weight": 0.5,
        "equip_slot": "feet",
        "speed_bonus": 0.3,
        "rarity": 0.3,
    },

    # === 도구 ===
    "손전등": {
        "category": ItemCategory.TOOL,
        "description": "LED 손전등. 밤에 시야를 밝혀준다.",
        "stackable": False,
        "weight": 0.3,
        "effects": {"night_vision": True},
        "rarity": 0.35,
    },
    "비상용 배터리": {
        "category": ItemCategory.TOOL,
        "description": "충전식 비상 배터리. 여러 장비에 사용 가능.",
        "stackable": True,
        "max_stack": 5,
        "weight": 0.5,
        "rarity": 0.25,
    },
    "지도": {
        "category": ItemCategory.TOOL,
        "description": "이 지역의 약도. 미니맵 범위가 넓어진다.",
        "stackable": False,
        "weight": 0.1,
        "effects": {"map_range": 2},
        "rarity": 0.2,
    },
    "개조 손전등": {
        "category": ItemCategory.TOOL,
        "description": "초강력 개조 손전등. 밤에도 낮처럼 볼 수 있다.",
        "stackable": False,
        "weight": 0.8,
        "effects": {"night_vision": True, "blind_enemies": True},
        "rarity": 0.05,
        "crafted": True,
    },

    # === 재료 ===
    "나무": {
        "category": ItemCategory.MATERIAL,
        "description": "건축 및 크래프팅용 목재.",
        "stackable": True,
        "max_stack": 20,
        "weight": 1.0,
        "rarity": 0.7,
    },
    "못": {
        "category": ItemCategory.MATERIAL,
        "description": "건축용 못. 바리케이드 제작에 필요.",
        "stackable": True,
        "max_stack": 30,
        "weight": 0.1,
        "rarity": 0.6,
    },
    "천": {
        "category": ItemCategory.MATERIAL,
        "description": "찢어진 천 조각. 다양한 용도.",
        "stackable": True,
        "max_stack": 15,
        "weight": 0.2,
        "rarity": 0.6,
    },
    "고철": {
        "category": ItemCategory.MATERIAL,
        "description": "재활용 가능한 금속 조각.",
        "stackable": True,
        "max_stack": 15,
        "weight": 0.8,
        "rarity": 0.5,
    },
    "바리케이드 재료": {
        "category": ItemCategory.MATERIAL,
        "description": "바리케이드 구축에 사용되는 재료 묶음.",
        "stackable": True,
        "max_stack": 5,
        "weight": 3.0,
        "rarity": 0.15,
        "crafted": True,
    },

    # === 퀘스트 아이템 ===
    "라디오 부품": {
        "category": ItemCategory.QUEST,
        "description": "장거리 무전기 조립에 필요한 핵심 부품. 3개를 모으면 구조 신호를 보낼 수 있다.",
        "stackable": True,
        "max_stack": 5,
        "weight": 0.5,
        "rarity": 0.08,
    },
    "장거리 무전기": {
        "category": ItemCategory.QUEST,
        "description": "조립 완료된 장거리 무전기! 구조 신호를 보낼 수 있다.",
        "stackable": False,
        "weight": 2.0,
        "rarity": 0.0,
        "crafted": True,
    },
    "군사 문서": {
        "category": ItemCategory.QUEST,
        "description": "기밀 등급의 군사 문서. 감염의 원인에 대한 단서가 적혀있다.",
        "stackable": False,
        "weight": 0.1,
        "rarity": 0.03,
    },
    "사진": {
        "category": ItemCategory.QUEST,
        "description": "누군가의 가족 사진. 뒷면에 메시지가 적혀있다.",
        "stackable": False,
        "weight": 0.01,
        "rarity": 0.05,
    },
    "기계 부품": {
        "category": ItemCategory.MATERIAL,
        "description": "복잡한 기계의 부품. 정밀 장비 개조에 필수적이다.",
        "stackable": True,
        "max_stack": 20,
        "weight": 0.5,
        "rarity": 0.1,
    },
    "농작물": {
        "category": ItemCategory.FOOD,
        "description": "밭에서 자란 싱싱한 농작물. 배를 든든하게 채운다.",
        "stackable": True,
        "max_stack": 5,
        "weight": 1.0,
        "effects": {"hunger": 40, "hp": 5},
        "rarity": 0.2,
    },

    # === 크래프팅 전용 ===
    "횃불": {
        "category": ItemCategory.TOOL,
        "description": "나무와 천으로 만든 횃불. 주변을 밝혀준다.",
        "stackable": True,
        "max_stack": 5,
        "weight": 0.5,
        "effects": {"night_vision": True},
        "rarity": 0.0,
        "crafted": True,
    },
    "함정": {
        "category": ItemCategory.TOOL,
        "description": "고철과 못으로 만든 트랩. 좀비를 잡을 수 있다.",
        "stackable": True,
        "max_stack": 3,
        "weight": 2.0,
        "effects": {"trap_damage": 30},
        "rarity": 0.0,
        "crafted": True,
    },
}


# ============================================================
# 루트 테이블 (건물/위치별 드롭)
# ============================================================
LOOT_TABLES = {
    "house": [
        ("식량통조림", 0.4), ("생수", 0.4), ("마른 빵", 0.3),
        ("나이프", 0.15), ("천", 0.3), ("붕대", 0.2),
        ("못", 0.2), ("탄산음료", 0.15), ("손전등", 0.1),
        ("사진", 0.05),
    ],
    "store": [
        ("식량통조림", 0.5), ("생수", 0.5), ("에너지바", 0.3),
        ("탄산음료", 0.3), ("마른 빵", 0.4), ("천", 0.2),
        ("야구방망이", 0.1), ("커피", 0.15), ("에너지 드링크", 0.2),
    ],
    "hospital": [
        ("구급상자", 0.5), ("진통제", 0.4), ("붕대", 0.5),
        ("약초", 0.2), ("방독면", 0.1), ("생수", 0.2),
    ],
    "police": [
        ("권총", 0.15), ("탄약", 0.3), ("방탄조끼", 0.1),
        ("무기", 0.2), ("손전등", 0.2), ("비상용 배터리", 0.15),
        ("지도", 0.1),
    ],
    "military": [
        ("탄약", 0.4), ("권총", 0.1), ("방탄조끼", 0.15),
        ("구급상자", 0.3), ("비상용 배터리", 0.2), ("라디오 부품", 0.08),
        ("군사 문서", 0.05), ("에너지바", 0.2), ("전투 식량", 0.2), ("에너지 드링크", 0.25),
    ],
    "shelter": [
        ("나무", 0.5), ("못", 0.4), ("천", 0.3),
        ("고철", 0.3), ("식량통조림", 0.2), ("생수", 0.2),
    ],
    "forest": [
        ("나무", 0.6), ("약초", 0.4),
    ],
    "car": [
        ("고철", 0.4), ("비상용 배터리", 0.15), ("생수", 0.1),
        ("에너지바", 0.1), ("지도", 0.05),
    ],
    "radio_tower": [
        ("라디오 부품", 0.4), ("비상용 배터리", 0.3),
        ("고철", 0.3), ("손전등", 0.15),
    ],
    "factory": [
        ("기계 부품", 0.6), ("고철", 0.5), ("못", 0.4),
        ("비상용 배터리", 0.3), ("가방", 0.1),
    ],
    "warehouse": [
        ("나무", 0.5), ("고철", 0.5), ("천", 0.3),
        ("야구방망이", 0.2), ("못", 0.4),
    ],
    "school": [
        ("마른 빵", 0.4), ("생수", 0.4), ("가방", 0.2),
        ("천", 0.3), ("사진", 0.15),
    ],
    "barn": [
        ("농작물", 0.6), ("나무", 0.5), ("고철", 0.2),
        ("생수", 0.3),
    ],
}


def generate_loot(loot_table_name, resource_multiplier=1.0, count_range=(1, 4)):
    """루트 테이블에서 아이템 생성"""
    table = LOOT_TABLES.get(loot_table_name, [])
    if not table:
        return []

    loot = []
    num_rolls = random.randint(*count_range)

    for _ in range(num_rolls):
        for item_name, chance in table:
            if random.random() < chance * resource_multiplier:
                loot.append(item_name)
                break  # 한 롤에 하나씩

    return loot


# ============================================================
# 인벤토리 시스템
# ============================================================
class Inventory:
    """격자형 인벤토리"""

    def __init__(self, slots=24):
        self.slots = slots
        self.items = []  # [(item_name, count), ...]
        self.max_weight = 30.0
        self.is_sandbox = False

    @property
    def current_weight(self):
        total = 0.0
        for name, count in self.items:
            data = ITEM_DATABASE.get(name, {})
            total += data.get("weight", 0.1) * count
        return total

    def add_item(self, item_name, count=1):
        """아이템 추가. 성공 시 True"""
        data = ITEM_DATABASE.get(item_name)
        if not data:
            return False

        # 무게 체크 (샌드박스 제외)
        item_weight = data.get("weight", 0.1)
        if not self.is_sandbox:
            if self.current_weight + (item_weight * count) - 1e-7 > self.max_weight:
                return False  # 무게 초과 시 수급 불가

        # 임시 시뮬레이션용 인벤토리 복제
        temp_items = list(self.items)
        temp_count = count

        # 스택 가능한 아이템 처리 시뮬레이션
        if data.get("stackable"):
            max_stack = data.get("max_stack", 99)
            for i, (name, cnt) in enumerate(temp_items):
                if name == item_name and cnt < max_stack:
                    add = min(temp_count, max_stack - cnt)
                    
                    if not self.is_sandbox:
                        # 임시 무게 계산
                        temp_current_weight = 0.0
                        for t_name, t_cnt in temp_items:
                            t_data = ITEM_DATABASE.get(t_name, {})
                            temp_current_weight += t_data.get("weight", 0.1) * t_cnt
                        
                        rem_weight = self.max_weight - temp_current_weight
                        max_can_add = int((rem_weight + 1e-7) / item_weight) if item_weight > 0 else add
                        add = min(add, max_can_add)
                        if add <= 0:
                            break
                            
                    temp_items[i] = (name, cnt + add)
                    temp_count -= add
                    if temp_count <= 0:
                        break

        # 새 슬롯에 추가 시뮬레이션
        while temp_count > 0 and len(temp_items) < self.slots:
            if data.get("stackable"):
                max_stack = data.get("max_stack", 99)
                add = min(temp_count, max_stack)
                
                if not self.is_sandbox:
                    temp_current_weight = 0.0
                    for t_name, t_cnt in temp_items:
                        t_data = ITEM_DATABASE.get(t_name, {})
                        temp_current_weight += t_data.get("weight", 0.1) * t_cnt
                    
                    rem_weight = self.max_weight - temp_current_weight
                    max_can_add = int((rem_weight + 1e-7) / item_weight) if item_weight > 0 else add
                    add = min(add, max_can_add)
                    if add <= 0:
                        break

                temp_items.append((item_name, add))
                temp_count -= add
            else:
                if not self.is_sandbox:
                    temp_current_weight = 0.0
                    for t_name, t_cnt in temp_items:
                        t_data = ITEM_DATABASE.get(t_name, {})
                        temp_current_weight += t_data.get("weight", 0.1) * t_cnt
                    
                    if temp_current_weight + item_weight - 1e-7 > self.max_weight:
                        break
                temp_items.append((item_name, 1))
                temp_count -= 1

        # 요청한 개수를 모두 담을 수 있는 경우에만 실제 인벤토리 업데이트
        if temp_count <= 0:
            self.items = temp_items
            return True
        return False

    def remove_item(self, item_name, count=1):
        """아이템 제거. 성공 시 True"""
        remaining = count
        to_remove = []

        for i, (name, cnt) in enumerate(self.items):
            if name == item_name:
                if cnt <= remaining:
                    remaining -= cnt
                    to_remove.append(i)
                else:
                    self.items[i] = (name, cnt - remaining)
                    remaining = 0
                if remaining <= 0:
                    break

        for i in reversed(to_remove):
            self.items.pop(i)

        return remaining <= 0

    def has_item(self, item_name, count=1):
        """아이템 보유 확인"""
        total = sum(cnt for name, cnt in self.items if name == item_name)
        return total >= count

    def count_item(self, item_name):
        """아이템 개수"""
        return sum(cnt for name, cnt in self.items if name == item_name)

    def get_items_by_category(self, category):
        """카테고리별 아이템 목록"""
        result = []
        for name, cnt in self.items:
            data = ITEM_DATABASE.get(name, {})
            if data.get("category") == category:
                result.append((name, cnt))
        return result

    @property
    def total_weight(self):
        total = 0
        for name, cnt in self.items:
            data = ITEM_DATABASE.get(name, {})
            total += data.get("weight", 0) * cnt
        return total

    @property
    def is_full(self):
        return len(self.items) >= self.slots

    def get_all_items(self):
        """모든 아이템 (이름, 개수, 데이터) 리스트"""
        result = []
        for name, cnt in self.items:
            data = ITEM_DATABASE.get(name, {})
            result.append((name, cnt, data))
        return result

    def to_dict(self):
        """저장용 딕셔너리"""
        return {"slots": self.slots, "items": list(self.items)}

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 복원"""
        inv = cls(data.get("slots", 24))
        inv.items = [tuple(item) for item in data.get("items", [])]
        return inv
