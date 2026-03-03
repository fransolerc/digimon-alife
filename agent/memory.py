# agent/memory.py
import time
import json
import math
import os
from config import MEMORY_MAX_SIZE, MEMORY_CONTEXT_SIZE

MEMORY_FILE = "data/memory.json"

class Memory:
    def __init__(self):
        self.entries = []
        self.spatial = {}
        self.reflections = []
        self.cycle_count = 0
        self.load()

    def add(self, thought):
        if thought:
            self.entries.append(thought)
            if len(self.entries) > MEMORY_MAX_SIZE:
                self.entries.pop(0)
            self.save()

    def update_spatial(self, agumon_x, agumon_y, nearby):
        if not nearby or not isinstance(nearby[0], dict):
            return
        for item in nearby:
            angle_rad = math.radians(item["angle"])
            obj_x = agumon_x + round(math.sin(angle_rad) * item["distance"])
            obj_y = agumon_y + round(math.cos(angle_rad) * item["distance"])
            obj_name = item["object"].strip()
            self.spatial[obj_name] = {
                "x": obj_x,
                "y": obj_y,
                "last_seen": time.time()
            }
            print(f"Spatial memory: {obj_name} at ({obj_x}, {obj_y})")
        self.save()

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

    def save(self):
        try:
            os.makedirs("data", exist_ok=True)
            with open(MEMORY_FILE, "w") as f:
                json.dump({
                    "entries": self.entries,
                    "spatial": self.spatial,
                    "reflections": self.reflections,
                    "cycle_count": self.cycle_count
                }, f, indent=2)
        except Exception as e:
            print(f"Memory save error: {e}")

    def load(self):
        try:
            if os.path.exists(MEMORY_FILE):
                with open(MEMORY_FILE, "r") as f:
                    data = json.load(f)
                    self.entries = data.get("entries", [])
                    self.spatial = data.get("spatial", {})
                    self.reflections = data.get("reflections", [])
                    self.cycle_count = data.get("cycle_count", 0)
                print(f"Memory loaded: {len(self.entries)} thoughts, {len(self.spatial)} locations")
            else:
                print("No previous memory found, starting fresh.")
        except Exception as e:
            print(f"Memory load error: {e}")

    def clear(self):
        self.entries = []
        self.spatial = {}
        self.save()

    def add_reflection(self, reflection):
        if reflection:
            self.reflections.append(reflection)
            if len(self.reflections) > 5:
                self.reflections.pop(0)
            self.save()

    def get_reflections_context(self):
        if not self.reflections:
            return "No reflections yet."
        return "\n".join(self.reflections)