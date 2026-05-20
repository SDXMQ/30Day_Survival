"""
crafting.py - 크래프팅 시스템
레시피 기반, 데이터 드리븐 설계
"""


# ============================================================
# 크래프팅 레시피 데이터베이스
# ============================================================
CRAFTING_RECIPES = {
    "바리케이드 재료": {
        "ingredients": {"나무": 3, "못": 5},
        "result_count": 1,
        "description": "은신처 방어에 사용되는 바리케이드 세트.",
        "category": "건축",
        "craft_time": 2.0,
    },
    "고급 치료킷": {
        "ingredients": {"구급상자": 1, "약초": 3, "붕대": 2},
        "result_count": 1,
        "description": "전문 의료 키트. 중상도 치료 가능.",
        "category": "의료",
        "craft_time": 3.0,
    },
    "개조 손전등": {
        "ingredients": {"손전등": 1, "비상용 배터리": 1},
        "result_count": 1,
        "description": "초강력 개조 손전등.",
        "category": "도구",
        "craft_time": 1.5,
    },
    "장거리 무전기": {
        "ingredients": {"라디오 부품": 3, "비상용 배터리": 1},
        "result_count": 1,
        "description": "구조 요청이 가능한 장거리 무전기!",
        "category": "퀘스트",
        "craft_time": 5.0,
    },
    "나이프": {
        "ingredients": {"고철": 2, "천": 1},
        "result_count": 1,
        "description": "날카로운 수제 나이프.",
        "category": "무기",
        "craft_time": 2.0,
    },
    "붕대": {
        "ingredients": {"천": 2},
        "result_count": 2,
        "description": "깨끗한 치료용 붕대.",
        "category": "의료",
        "craft_time": 1.0,
    },
    "횃불": {
        "ingredients": {"나무": 1, "천": 1},
        "result_count": 1,
        "description": "주변을 밝히는 횃불.",
        "category": "도구",
        "craft_time": 0.5,
    },
    "함정": {
        "ingredients": {"고철": 3, "못": 5, "나무": 2},
        "result_count": 1,
        "description": "좀비를 잡는 트랩.",
        "category": "건축",
        "craft_time": 3.0,
    },
    "방탄조끼 수리": {
        "ingredients": {"천": 3, "고철": 2},
        "result_count": 0,  # 특수: 기존 방탄조끼 강화
        "description": "방탄조끼를 수리하고 강화한다.",
        "category": "장비",
        "craft_time": 4.0,
        "special": "repair_vest",
    },
}

# 카테고리별 레시피 분류
RECIPE_CATEGORIES = {}
for recipe_name, recipe_data in CRAFTING_RECIPES.items():
    cat = recipe_data.get("category", "기타")
    if cat not in RECIPE_CATEGORIES:
        RECIPE_CATEGORIES[cat] = []
    RECIPE_CATEGORIES[cat].append(recipe_name)


class CraftingSystem:
    """크래프팅 시스템"""

    def __init__(self):
        self.discovered_recipes = set()
        self.craft_queue = None
        self.craft_timer = 0
        self.craft_progress = 0  # 0~1

    def can_craft(self, recipe_name, inventory):
        """크래프팅 가능 여부"""
        recipe = CRAFTING_RECIPES.get(recipe_name)
        if not recipe:
            return False

        for item_name, needed in recipe["ingredients"].items():
            if not inventory.has_item(item_name, needed):
                return False
        return True

    def get_available_recipes(self, inventory):
        """현재 가능한 레시피 목록"""
        available = []
        for name in CRAFTING_RECIPES:
            if self.can_craft(name, inventory):
                available.append(name)
        return available

    def get_all_recipes_with_status(self, inventory):
        """모든 레시피와 가능 여부"""
        recipes = []
        for name, data in CRAFTING_RECIPES.items():
            can = self.can_craft(name, inventory)
            ingredients_status = {}
            for item_name, needed in data["ingredients"].items():
                have = inventory.count_item(item_name)
                ingredients_status[item_name] = (have, needed)
            recipes.append({
                "name": name,
                "data": data,
                "can_craft": can,
                "ingredients_status": ingredients_status,
            })
        return recipes

    def start_craft(self, recipe_name, inventory):
        """크래프팅 시작"""
        if not self.can_craft(recipe_name, inventory):
            return False

        recipe = CRAFTING_RECIPES[recipe_name]
        # 재료 소모
        for item_name, needed in recipe["ingredients"].items():
            inventory.remove_item(item_name, needed)

        self.craft_queue = recipe_name
        self.craft_timer = recipe["craft_time"]
        self.craft_progress = 0
        return True

    def update(self, dt, inventory, world=None, px=0, py=0):
        """크래프팅 진행"""
        if not self.craft_queue:
            return None

        recipe = CRAFTING_RECIPES.get(self.craft_queue)
        if not recipe:
            self.craft_queue = None
            return None

        self.craft_progress += dt / recipe["craft_time"]

        if self.craft_progress >= 1.0:
            result_name = self.craft_queue
            result_count = recipe["result_count"]

            # 결과물 추가
            if result_count > 0:
                success = inventory.add_item(result_name, result_count)
                if not success and world:
                    for _ in range(result_count):
                        world.drop_item(result_name, px, py)

            self.discovered_recipes.add(result_name)
            self.craft_queue = None
            self.craft_progress = 0
            return result_name

        return None

    @property
    def is_crafting(self):
        return self.craft_queue is not None

    def to_dict(self):
        return {
            "discovered": list(self.discovered_recipes),
        }

    @classmethod
    def from_dict(cls, data):
        system = cls()
        system.discovered_recipes = set(data.get("discovered", []))
        return system
