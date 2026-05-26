# 30 Days of Survival (30일간의 생존)

> ⚠️ **Note**: This codebase was written by an AI based on human ideas.

[한국어 버전 (Korean Version)](./README.ko.md)

An open-world zombie apocalypse survival game built using Python and Pygame-ce. Survive for 30 days until the rescue team arrives, while managing your stats, crafting items, upgrading shelter defenses, and defending against night raids.

---

## Key Features

* **Procedural World Generation & Chunking**: Simplex noise-based procedural map with distinct biomes (City, Forest, Military Base, Hospital District, Wheat Field, etc.) and road networks.
* **Building Interior Exploration**: Enter houses, stores, schools, hospitals, and factories to loot items from drawers, refrigerators, medicine cabinets, and military crates. Beware of stealthy zombies hiding in the dark!
* **Night Raid System**: Every night (with larger hordes every 7th day), zombies will attack your shelter. Install barricades to increase your shelter defense rating, or fight them off directly.
* **Survival Stats & Sneaking**: Manage your health, hunger, thirst, stamina, and stress levels. Toggle sneaking (LCTRL) to halve zombie detection ranges and hide your movement.
* **Data-driven Inventory & Crafting**: Drag-and-drop grid inventory system with weight constraints. Craft essential items such as bandages, modified flashlights, traps, barricades, and long-range radios.
* **NPC Dialogues & Quests**: Meet merchants, soldiers, and survivors. Trade goods or complete rescue/fetch quests tracked by a live quest HUD.
* **Localization & Sound System**: Full multi-language support (English and Korean) and immersive retro-style sound effects.
* **Save/Load System**: F5 quicksave support and autosaves every 5 days.

---

## Installation & Running

### Prerequisites
Make sure you have Python 3.8+ installed.

### Setup
Install dependencies and run the game using the provided batch file or via terminal:

1. Clone or download the repository.
2. Run `run.bat` (on Windows), which will automatically install dependencies and start the game.

Or run manually:
```bash
pip install -r requirements.txt
python src/main.py
```

---

## Controls

* **W, A, S, D** / **Arrow Keys**: Move
* **LSHIFT**: Sprint (consumes stamina)
* **LCTRL**: Sneak (halves noise and detection)
* **Mouse Left Click**: Attack (melee swing or shoot ranged weapons)
* **E**: Interact / Search furniture / Enter and exit buildings / Talk to NPCs
* **I**: Toggle Inventory (Drag & drop to equip/unequip, Left Click to use, Right Click to drop)
* **C**: Toggle Crafting Menu
* **F5**: Quick Save
* **ESC**: Pause Game / Open menu
