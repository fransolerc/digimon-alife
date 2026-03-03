# agent/memory.py
import time
from config import MEMORY_MAX_SIZE, MEMORY_CONTEXT_SIZE

class Memory:
    def __init__(self):
        self.entries = []
        self.spatial = {}

    def add(self, thought):
        if thought:
            self.entries.append(thought)
            if len(self.entries) > MEMORY_MAX_SIZE:
                self.entries.pop(0)

    def update_spatial(self, agumon_x, agumon_y, nearby):
        if not nearby or not isinstance(nearby[0], dict):
            return
        import math
        for item in nearby:
            angle_rad = math.radians(item["angle"])
            obj_x = agumon_x + round(math.sin(angle_rad) * item["distance"])
            obj_y = agumon_y + round(math.cos(angle_rad) * item["distance"])
            self.spatial[item["object"]] = {
                "x": obj_x,
                "y": obj_y,
                "last_seen": time.time()
            }
            print(f"Spatial memory: {item['object']} at ({obj_x}, {obj_y})")

    def get_spatial_context(self):
        if not self.spatial:
            return "No known locations yet."
        lines = []
        for obj, data in self.spatial.items():
            lines.append(f"{obj} last seen at ({data['x']:.0f}, {data['y']:.0f})")
        return "\n".join(lines)

    def get_context(self):
        recent = self.entries[-MEMORY_CONTEXT_SIZE:]
        return "\n".join(recent) if recent else "Nothing yet."

    def clear(self):
        self.entries = []
        self.spatial = {}