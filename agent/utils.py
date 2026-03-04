import math

def angle_to_offset(angle, distance=2000):
    rad = math.radians(angle)
    x = math.cos(rad)
    y = math.sin(rad)
    offset_x = round(y * distance)
    offset_y = round(x * distance)
    print(f"Angle: {angle}° → offset_x: {offset_x}, offset_y: {offset_y}")
    return (offset_x, offset_y)
