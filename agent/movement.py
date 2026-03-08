def get_target_offset(digimon, target):
    if target == "explore":
        return None
    target_lower = target.lower().strip()

    for obj_name, data in digimon.memory.spatial.items():
        if obj_name.lower().strip() == target_lower or target_lower in obj_name.lower().strip():
            return round(data["x"]), round(data["y"])

    return None


def determine_action(digimon, target):
    if digimon.memory.force_explore:
        digimon.memory.force_explore = False
        return None

    return get_target_offset(digimon, target)