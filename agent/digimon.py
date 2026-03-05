import ollama
import json
import random
from agent.memory import Memory
from agent.prompt import build_prompt, REFLECTION_PROMPT
from agent.utils import angle_to_offset
from config import (
    MODEL, HUNGER_INCREASE, ENERGY_DECREASE, CURIOSITY_INCREASE, CURIOSITY_DECREASE,
    HUNGER_MAX, HUNGER_MIN, ENERGY_MAX, ENERGY_MIN, CURIOSITY_MAX, CURIOSITY_MIN,
    TOUCH_DISTANCE, HUNGER_EAT, ENERGY_RESTORE,
    WAIT_TIME_DEFAULT, WAIT_TIME_MIN, WAIT_TIME_MAX,
    FIXATION_TARGET_COUNT
)

class Digimon:
    def __init__(self, agent_id, lore):
        self.agent_id = agent_id
        self.memory = Memory(agent_id)
        self.lore = lore
        self.hunger = self.memory.hunger
        self.energy = self.memory.energy
        self.curiosity = self.memory.curiosity
        self.x = 0.0
        self.y = 0.0
        self.processing = False

    def get_target_offset(self, target, nearby):
        if target == "explore" or not nearby or not isinstance(nearby[0], dict):
            return None
        target_lower = target.lower().strip()

        # Search in nearby first
        for item in nearby:
            object_lower = item["object"].lower().strip()
            if object_lower == target_lower or object_lower in target_lower or target_lower in object_lower:
                distance = max(item["distance"], 200)
                return angle_to_offset(item["angle"], distance)

        # Fallback to spatial memory
        for obj_name, data in self.memory.spatial.items():
            if obj_name.lower().strip() == target_lower or target_lower in obj_name.lower().strip():
                offset_x = round(data["x"] - self.x)
                offset_y = round(data["y"] - self.y)
                return (offset_x, offset_y)

        print(f"Target not found: '{target}'")
        return None

    def update_needs(self):
        self.hunger = min(HUNGER_MAX, self.hunger + HUNGER_INCREASE)
        self.energy = max(ENERGY_MIN, self.energy - ENERGY_DECREASE)
        self.curiosity = min(CURIOSITY_MAX, self.curiosity + CURIOSITY_INCREASE)

    def distance_label(self, distance):
        if distance < 200:
            return "very close"
        elif distance < 500:
            return "nearby"
        elif distance < 1000:
            return "moderate distance"
        else:
            return "far away"

    def parse_nearby(self, nearby):
        if nearby and isinstance(nearby[0], dict):
            return ", ".join([
                f"{item['object'].strip()} ({self.distance_label(item['distance'])})"
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
            self.hunger = max(HUNGER_MIN, self.hunger - HUNGER_EAT)
            print("Digimon eats from the campfire!")
        elif touching == "tent":
            self.energy = min(ENERGY_MAX, self.energy + ENERGY_RESTORE)
            print("Digimon rests in the tent!")

    def think(self, nearby_str, touching="", spatial="", reflections=""):
        prompt = build_prompt(
            self.lore,
            self.hunger,
            self.energy,
            self.curiosity,
            nearby_str,
            self.memory.get_context(),
            touching=touching,
            spatial=spatial,
            reflections=reflections
        )
        response = ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        text = response["message"]["content"].strip().replace("```json", "").replace("```", "").strip()
        return json.loads(text)

    def _update_state(self, data):
        self.x = data.get("x", 0)
        self.y = data.get("y", 0)

    def _handle_environment(self, nearby):
        touching = self.get_touching(nearby)
        self.handle_touching(touching)
        nearby_str = self.parse_nearby(nearby)
        self.memory.update_spatial(self.x, self.y, nearby)
        return touching, nearby_str

    def _run_thought_cycle(self, nearby_str, touching):
        result = self.think(nearby_str, touching, self.memory.get_spatial_context(), self.memory.get_reflections_context())

        thought = result.get("thought", "")
        target = result.get("target", "explore")
        wait_time = max(WAIT_TIME_MIN, min(WAIT_TIME_MAX, int(result.get("wait_time", WAIT_TIME_DEFAULT))))

        self.memory.add(thought)
        self.memory.add_target(target)
        if target == "explore":
            self.curiosity = max(CURIOSITY_MIN, self.curiosity - CURIOSITY_DECREASE)
        self.memory.cycle_count += 1
        if self.memory.cycle_count % 5 == 0:
            self.reflect()

        return target, thought, wait_time

    def _determine_action(self, target, nearby):
        if self.memory.force_explore:
            self.memory.force_explore = False
            offset_x = random.randint(-2000, 2000)
            offset_y = random.randint(-2000, 2000)
        else:
            offset = self.get_target_offset(target, nearby)
            if offset:
                offset_x, offset_y = offset
            else:
                offset_x = random.randint(-2000, 2000)
                offset_y = random.randint(-2000, 2000)

        return offset_x, offset_y

    def process(self, data):
        if self.processing:
            return {"offset_x": 0, "offset_y": 0, "thought": "", "wait_time": WAIT_TIME_DEFAULT}

        self.processing = True
        try:
            self.update_needs()
            self._update_state(data)

            nearby = data.get("nearby", [])
            touching, nearby_str = self._handle_environment(nearby)

            target, thought, wait_time = self._run_thought_cycle(nearby_str, touching)
            offset_x, offset_y = self._determine_action(target, nearby)

            self.memory.hunger = self.hunger
            self.memory.energy = self.energy
            self.memory.curiosity = self.curiosity
            self.memory.save()

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
        prompt = REFLECTION_PROMPT.format(agent_name=self.agent_id, thoughts=thoughts)

        try:
            response = ollama.chat(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            reflection = response["message"]["content"].strip()
            self.memory.add_reflection(reflection)
            self._check_fixation()
        except Exception as e:
            print(f"Reflection error: {e}")


    def _check_fixation(self):
        if len(self.memory.recent_targets) >= FIXATION_TARGET_COUNT:
            if len(set(self.memory.recent_targets)) == 1:
                self.memory.force_explore = True