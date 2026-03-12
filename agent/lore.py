import json
from config import LANGUAGE
from locales import get_behavior_rules, IDENTITY_LORE, DEFAULT_LORE

DIGIMON_DB_PATH = "db/digimon.json"

_db = None


def _load_db():
    global _db
    if _db is None:
        try:
            with open(DIGIMON_DB_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                _db = {entry["Name"].lower(): entry for entry in data}
        except FileNotFoundError:
            print(f"Digimon database not found at {DIGIMON_DB_PATH}. Using default lore.")
            _db = {}
        except json.JSONDecodeError as e:
            print(f"Digimon database is corrupted: {e}. Using default lore.")
            _db = {}
    return _db


def generate_lore(name):
    db = _load_db()
    entry = db.get(name.lower())

    if not entry:
        return _default_lore(name)

    level = entry.get("Level", "Unknown")
    type_ = entry.get("Type", "Unknown")
    speciality1 = entry.get("Speciality #1", "None")
    speciality2 = entry.get("Speciality #2", "None")
    food = entry.get("Favorite Food", "digital food")
    digivolutions = [
        entry.get(f"Digivoluton - To #{i}")
        for i in range(1, 7)
        if entry.get(f"Digivoluton - To #{i}") not in (None, "None")
    ]
    digivolutions_str = ", ".join(digivolutions) if digivolutions else "unknown"

    rules = get_behavior_rules()
    identity = IDENTITY_LORE.get(LANGUAGE, IDENTITY_LORE["en"]).format(
        name=name, level=level, type_=type_,
        speciality1=speciality1, speciality2=speciality2,
        food=food, digivolutions=digivolutions_str
    )
    return identity + rules.get(LANGUAGE, rules["en"])


def _default_lore(name):
    rules = get_behavior_rules()
    identity = DEFAULT_LORE.get(LANGUAGE, DEFAULT_LORE["en"]).format(name=name)
    return identity + rules.get(LANGUAGE, rules["en"])