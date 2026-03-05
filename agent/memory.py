import time
import json
import math
import os
from config import (
    MEMORY_MAX_SIZE, MEMORY_CONTEXT_SIZE,
    ENERGY_MAX, HUNGER_MIN, CURIOSITY_MAX, FIXATION_TARGET_COUNT
)

class Memory:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.file = f"data/{agent_id}.json"
        self.entries = []
        self.spatial = {}
        self.reflections = []
        self.recent_targets = []
        self.cycle_count = 0
        self.hunger = 50.0
        self.energy = 100.0
        self.curiosity = 50.0
        self.force_explore = False
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
            # Calculate object position relative to agent
            # Assuming angle is absolute or relative to a fixed coordinate system
            # x = sin(angle), y = cos(angle) based on angle_to_offset logic
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
            os.makedirs(os.path.dirname(self.file), exist_ok=True)
            with open(self.file, "w") as f:
                json.dump({
                    "entries": self.entries,
                    "spatial": self.spatial,
                    "reflections": self.reflections,
                    "cycle_count": self.cycle_count,
                    "recent_targets": self.recent_targets,
                    "hunger": self.hunger,
                    "energy": self.energy,
                    "curiosity": self.curiosity
                }, f, indent=2)
        except Exception as e:
            print(f"Memory save error: {e}")

    def load(self):
        try:
            if os.path.exists(self.file):
                with open(self.file, "r") as f:
                    data = json.load(f)
                    self.entries = data.get("entries", [])
                    self.spatial = data.get("spatial", {})
                    self.reflections = data.get("reflections", [])
                    self.cycle_count = data.get("cycle_count", 0)
                    self.recent_targets = data.get("recent_targets", [])
                    self.hunger = data.get("hunger", 50.0)
                    self.energy = data.get("energy", 100.0)
                    self.curiosity = data.get("curiosity", 50.0)
                print(f"Memory loaded: {len(self.entries)} thoughts, {len(self.spatial)} locations")
            else:
                print("No previous memory found, starting fresh.")
        except Exception as e:
            print(f"Memory load error: {e}")

    def clear(self):
        self.entries = []
        self.spatial = {}
        self.reflections = []
        self.cycle_count = 0
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

    def add_target(self, target):
        self.recent_targets.append(target)
        if len(self.recent_targets) > FIXATION_TARGET_COUNT:
            self.recent_targets.pop(0)
        self.save()