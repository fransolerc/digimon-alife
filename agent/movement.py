from agent.utils import angle_to_offset


def get_target_offset(digimon, target, nearby):
    if target == "explore":
        return None
    target_lower = target.lower().strip()

    for item in nearby:
        object_lower = item["object"].lower().strip()
        if object_lower == target_lower or object_lower in target_lower or target_lower in object_lower:
            distance = max(item["distance"], 200)
            return angle_to_offset(item["angle"], distance)

    for obj_name, data in digimon.memory.spatial.items():
        if obj_name.lower().strip() == target_lower or target_lower in obj_name.lower().strip():
            return round(data["x"]), round(data["y"])

    return None


def determine_action(digimon, target, nearby):
    if digimon.memory.force_explore:
        digimon.memory.force_explore = False
        return None

    return get_target_offset(digimon, target, nearby)