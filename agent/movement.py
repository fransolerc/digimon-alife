import random
from agent.utils import angle_to_offset
from config import EXPLORE_ZONE_RADIUS, MAP_HALF_SIZE


def get_target_offset(digimon, target, nearby):
    if target == "explore" or not nearby or not isinstance(nearby[0], dict):
        return None
    target_lower = target.lower().strip()

    for item in nearby:
        object_lower = item["object"].lower().strip()
        if object_lower == target_lower or object_lower in target_lower or target_lower in object_lower:
            distance = max(item["distance"], 200)
            return angle_to_offset(item["angle"], distance)

    for obj_name, data in digimon.memory.spatial.items():
        if obj_name.lower().strip() == target_lower or target_lower in obj_name.lower().strip():
            offset_x = round(data["x"] - digimon.x)
            offset_y = round(data["y"] - digimon.y)
            return offset_x, offset_y

    return None


def get_exploration_offset(digimon):
    candidates = []
    for _ in range(20):
        cx = random.randint(-MAP_HALF_SIZE, MAP_HALF_SIZE)
        cy = random.randint(-MAP_HALF_SIZE, MAP_HALF_SIZE)
        covered = False
        for zone in digimon.memory.explored_zones:
            dx = zone["x"] - cx
            dy = zone["y"] - cy
            if (dx * dx + dy * dy) < EXPLORE_ZONE_RADIUS ** 2:
                covered = True
                break
        if not covered:
            candidates.append((cx, cy))

    if candidates:
        tx, ty = random.choice(candidates)
        return round(tx - digimon.x), round(ty - digimon.y)

    return random.randint(-2000, 2000), random.randint(-2000, 2000)


def determine_action(digimon, target, nearby):
    if digimon.memory.force_explore:
        digimon.memory.force_explore = False
        return get_exploration_offset(digimon)

    offset = get_target_offset(digimon, target, nearby)
    if offset:
        return offset

    return get_exploration_offset(digimon)