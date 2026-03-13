import time
import json
import os
import tempfile
from agent.memory.associative_memory import AssociativeMemory
from config import (
    MEMORY_MAX_SIZE, MEMORY_CONTEXT_SIZE,
    FIXATION_TARGET_COUNT
)
from utils import extract_keywords


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
        self.associative = AssociativeMemory()
        self.explored_zones = []
        self.load()

    def add(self, thought):
        if thought:
            self.entries.append(thought)
            if len(self.entries) > MEMORY_MAX_SIZE:
                self.entries.pop(0)

    def update_spatial(self, nearby):
        for item in nearby:
            obj_name = item["object"].strip()
            self.spatial[obj_name] = {
                "x": item["x"],
                "y": item["y"],
                "last_seen": time.time()
            }
        self.save()

    def get_spatial_context(self):
        from locales import OBJECT_LABELS
        from config import LANGUAGE
        labels = OBJECT_LABELS.get(LANGUAGE, {})
        if not self.spatial:
            return "No known locations yet."
        lines = []
        for obj, data in self.spatial.items():
            display = labels.get(obj, obj)
            lines.append(f"{display} last seen at ({data['x']:.0f}, {data['y']:.0f})")
        return "\n".join(lines)

    def get_context(self):
        if not self.entries:
            return "Nothing yet."

        recent = self.entries[-MEMORY_CONTEXT_SIZE:]
        filtered = [recent[0]]

        for entry in recent[1:]:
            entry_keywords = set(extract_keywords(entry))
            prev_keywords = set(extract_keywords(filtered[-1]))
            if len(entry_keywords) == 0:
                continue
            overlap = len(entry_keywords & prev_keywords) / len(entry_keywords)
            if overlap < 0.4:
                filtered.append(entry)

        return "\n".join(filtered) if filtered else "Nothing yet."

    def save(self):
        try:
            os.makedirs(os.path.dirname(self.file), exist_ok=True)
            data = {
                "entries": self.entries,
                "spatial": self.spatial,
                "reflections": self.reflections,
                "cycle_count": self.cycle_count,
                "recent_targets": self.recent_targets,
                "hunger": self.hunger,
                "energy": self.energy,
                "curiosity": self.curiosity,
                "associative": self.associative.to_dict(),
                "explored_zones": self.explored_zones
            }
            dir_name = os.path.dirname(self.file)
            with tempfile.NamedTemporaryFile(
                    mode="w", dir=dir_name, delete=False, suffix=".tmp"
            ) as tmp:
                json.dump(data, tmp, indent=2)
                tmp_path = tmp.name
            os.replace(tmp_path, self.file)
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
                    self.associative = AssociativeMemory.from_dict(
                        data.get("associative", {"node_count": 0, "nodes": []})
                    )
                    self.explored_zones = data.get("explored_zones", [])
            else:
                print("No previous memory found, starting fresh.")
        except Exception as e:
            print(f"Memory load error: {e}")

    def clear(self):
        self.entries = []
        self.spatial = {}
        self.reflections = []
        self.cycle_count = 0
        self.recent_targets = []
        self.explored_zones = []
        self.associative = AssociativeMemory()
        self.save()

    def add_reflection(self, reflection):
        if reflection:
            self.reflections.append(reflection)
            if len(self.reflections) > 5:
                self.reflections.pop(0)

    def get_reflections_context(self):
        if not self.reflections:
            return "No reflections yet."
        return "\n".join(self.reflections)

    def add_target(self, target):
        self.recent_targets.append(target.strip())
        if len(self.recent_targets) > FIXATION_TARGET_COUNT:
            self.recent_targets.pop(0)

    def get_semantic_context(self):
        return self.associative.get_semantic_context()

    def get_relevant_context(self, keywords, limit=5):
        if not keywords:
            return self.get_semantic_context()
        nodes = self.associative.get_relevant(keywords, limit=limit)
        if not nodes:
            return self.get_semantic_context()
        return "\n".join([f"- {n.description}" for n in nodes])

    def add_event_node(self, subject, predicate, obj, description, poignancy, keywords):
        self.associative.add_event(subject, predicate, obj, description, poignancy, keywords)

    def add_thought_node(self, subject, predicate, obj, description, poignancy, keywords, depth=1):
        self.associative.add_thought(subject, predicate, obj, description, poignancy, keywords, depth)

    def add_explored_zone(self, x, y):
        for zone in self.explored_zones:
            dx = zone["x"] - x
            dy = zone["y"] - y
            if (dx*dx + dy*dy) < 200**2:
                return
        self.explored_zones.append({"x": round(x), "y": round(y)})
        self.save()