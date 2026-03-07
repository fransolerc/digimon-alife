TOUCH_DISTANCE = None  # imported from config

from config import TOUCH_DISTANCE


def distance_label(distance):
    if distance < 200:
        return "very close"
    elif distance < 500:
        return "nearby"
    elif distance < 1000:
        return "moderate distance"
    else:
        return "far away"


def parse_nearby(nearby):
    if nearby and isinstance(nearby[0], dict):
        return ", ".join([
            f"{item['object'].strip()} ({distance_label(item['distance'])})"
            for item in nearby
        ])
    return "nothing..."


def get_touching(nearby):
    if nearby and isinstance(nearby[0], dict):
        for item in nearby:
            if item["distance"] < TOUCH_DISTANCE:
                return item["object"].strip()
    return ""

def get_touching_from_spatial(agent_x, agent_y, spatial):
    from config import TOUCH_DISTANCE
    import math
    for obj_name, data in spatial.items():
        dx = data["x"] - agent_x
        dy = data["y"] - agent_y
        distance = math.sqrt(dx * dx + dy * dy)
        if distance < TOUCH_DISTANCE:
            return obj_name
    return ""