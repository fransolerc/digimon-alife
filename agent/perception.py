import math
from config import TOUCH_DISTANCE


def get_touching_from_spatial(agent_x, agent_y, spatial):
    for obj_name, data in spatial.items():
        dx = data["x"] - agent_x
        dy = data["y"] - agent_y
        if math.sqrt(dx * dx + dy * dy) < TOUCH_DISTANCE:
            return obj_name
    return ""