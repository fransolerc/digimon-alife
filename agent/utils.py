import math
from config import MAX_VIEW_DISTANCE

def angle_to_offset(angle, distance=MAX_VIEW_DISTANCE):
    rad = math.radians(angle)
    x = math.cos(rad)
    y = math.sin(rad)
    offset_x = round(y * distance)
    offset_y = round(x * distance)
    return offset_x, offset_y
