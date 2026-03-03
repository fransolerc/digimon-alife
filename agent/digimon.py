import ollama
import json
from agent.memory import Memory
from agent.prompt import build_prompt
from config import (
    MODEL, HUNGER_INCREASE, ENERGY_DECREASE,
    HUNGER_MAX, ENERGY_MIN, TOUCH_DISTANCE,
    CAMPFIRE_HUNGER_RESTORE,
    WAIT_TIME_DEFAULT, WAIT_TIME_MIN, WAIT_TIME_MAX,
    FIXATION_KEYWORDS
)

class Digimon:
    def __init__(self):
        self.hunger = 50.0
        self.energy = 100.0
        self.x = 0.0
        self.y = 0.0
        self.memory = Memory()
        self.processing = False
        self.memory.force_explore = False

    def angle_to_offset(self, angle, distance=2000):
        import math
        rad = math.radians(angle)
        x = math.cos(rad)
        y = math.sin(rad)
        offset_x = round(y * distance)
        offset_y = round(x * distance)
        print(f"Angle: {angle}° → offset_x: {offset_x}, offset_y: {offset_y}")
        return (offset_x, offset_y)

    def get_target_offset(self, target, nearby):
        if target == "explore" or not nearby or not isinstance(nearby[0], dict):
            return None
        target_lower = target.lower().strip()

        # buscar en nearby primero
        for item in nearby:
            object_lower = item["object"].lower().strip()
            if object_lower == target_lower or object_lower in target_lower or target_lower in object_lower:
                print(f"Target matched in nearby: '{target}'")
                distance = max(item["distance"], 200)
                return self.angle_to_offset(item["angle"], distance)

        # fallback a memoria espacial
        for obj_name, data in self.memory.spatial.items():
            if obj_name.lower().strip() == target_lower or target_lower in obj_name.lower().strip():
                print(f"Target matched in spatial memory: '{target}' at ({data['x']}, {data['y']})")
                offset_x = round(data["x"] - self.x)
                offset_y = round(data["y"] - self.y)
                return (offset_x, offset_y)

        print(f"Target not found: '{target}'")
        return None

    def update_needs(self):
        self.hunger = min(HUNGER_MAX, self.hunger + HUNGER_INCREASE)
        self.energy = max(ENERGY_MIN, self.energy - ENERGY_DECREASE)

    def parse_nearby(self, nearby):
        if nearby and isinstance(nearby[0], dict):
            return ", ".join([
                f"{item['object'].strip()} (angle: {item['angle']:.1f}°, distance: {item['distance']:.0f})"
                for item in nearby
            ])
        return "nothing..."

    def get_touching(self, nearby):
        if nearby and isinstance(nearby[0], dict):
            for item in nearby:
                if item["distance"] < TOUCH_DISTANCE:
                    return item["object"].strip()
        return ""

    def handle_touching(self, touching):
        if touching == "campfire":
            self.hunger = max(ENERGY_MIN, self.hunger - CAMPFIRE_HUNGER_RESTORE)
            print("Digimon eats from the campfire!")

    def think(self, nearby_str, touching="", spatial="", reflections=""):
        prompt = build_prompt(
            self.hunger,
            self.energy,
            nearby_str,
            self.memory.get_context(),
            touching,
            spatial,
            reflections
        )
        response = ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        text = response["message"]["content"].strip().replace("```json", "").replace("```", "").strip()
        return json.loads(text)

    def process(self, data):
        if self.processing:
            print("Still thinking, ignoring request.")
            return {"offset_x": 0, "offset_y": 0, "thought": "", "wait_time": WAIT_TIME_DEFAULT}

        self.processing = True
        self.update_needs()

        nearby = data.get("nearby", [])

        digimon_x = data.get("x", 0)
        digimon_y = data.get("y", 0)
        print(f"Digimon position: {digimon_x}, {digimon_y}")
        self.x = digimon_x
        self.y = digimon_y

        touching = self.get_touching(nearby)
        self.handle_touching(touching)
        nearby_str = self.parse_nearby(nearby)
        self.memory.update_spatial(digimon_x, digimon_y, nearby)

        try:
            result = self.think(nearby_str, touching, self.memory.get_spatial_context(), self.memory.get_reflections_context())

            thought = result.get("thought", "")
            target = result.get("target", "explore")
            wait_time = max(WAIT_TIME_MIN, min(WAIT_TIME_MAX, int(result.get("wait_time", WAIT_TIME_DEFAULT))))

            self.memory.add(thought)

            self.memory.cycle_count += 1
            if self.memory.cycle_count % 5 == 0:
                self.reflect()

            print(f"Digimon thinks: {thought}")
            print(f"Target: {target} | Wait: {wait_time}s")
            if touching:
                print(f"Touching: {touching}")

            if self.memory.force_explore:
                self.memory.force_explore = False
                import random
                offset_x = random.randint(-2000, 2000)
                offset_y = random.randint(-2000, 2000)
            else:
                offset = self.get_target_offset(target, nearby)
                if offset:
                    offset_x, offset_y = offset
                else:
                    import random
                    offset_x = random.randint(-2000, 2000)
                    offset_y = random.randint(-2000, 2000)

            print(f"Sending offset: {offset_x}, {offset_y}")

            return {
                "offset_x": offset_x,
                "offset_y": offset_y,
                "thought": thought,
                "wait_time": wait_time
            }

        except Exception as e:
            print(f"Error: {e}")
            return {"offset_x": 2000, "offset_y": 0, "thought": "...", "wait_time": WAIT_TIME_DEFAULT}

        finally:
            self.processing = False

    def reflect(self):
        if len(self.memory.entries) < 5:
            return

        thoughts = "\n".join(self.memory.entries[-5:])
        prompt = f"""You are Agumon, a curious Digimon inhabiting a digital forest.
    These are your last 5 thoughts:
    {thoughts}

    Based on these thoughts, write a brief reflection (2-3 sentences) summarizing what you have learned or concluded.
    Reply ONLY with the reflection text, no JSON, no extra formatting."""

        try:
            response = ollama.chat(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            reflection = response["message"]["content"].strip()
            self.memory.add_reflection(reflection)
            print(f"Reflection: {reflection}")
            self._check_fixation(reflection)
        except Exception as e:
            print(f"Reflection error: {e}")


    def _check_fixation(self, reflection):
        reflection_lower = reflection.lower()
        if any(word in reflection_lower for word in FIXATION_KEYWORDS):
            print("Fixation detected, forcing exploration.")
            self.memory.force_explore = True