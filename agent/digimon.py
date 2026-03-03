import ollama
import json
from agent.memory import Memory
from agent.prompt import build_prompt
from config import (
    MODEL, HUNGER_INCREASE, ENERGY_DECREASE,
    HUNGER_MAX, ENERGY_MIN, TOUCH_DISTANCE,
    CAMPFIRE_HUNGER_RESTORE, DIRECTIONS_TO_OFFSET,
    WAIT_TIME_DEFAULT, WAIT_TIME_MIN, WAIT_TIME_MAX
)

class Digimon:
    def __init__(self):
        self.hunger = 50.0
        self.energy = 100.0
        self.memory = Memory()
        self.processing = False

    def update_needs(self):
        self.hunger = min(HUNGER_MAX, self.hunger + HUNGER_INCREASE)
        self.energy = max(ENERGY_MIN, self.energy - ENERGY_DECREASE)

    def parse_nearby(self, nearby):
        if nearby and isinstance(nearby[0], dict):
            return ", ".join([
                f"{item['object']} (angle: {item['angle']:.1f}°, distance: {item['distance']:.0f})"
                for item in nearby
            ])
        return "nada en particular"

    def get_touching(self, nearby):
        if nearby and isinstance(nearby[0], dict):
            for item in nearby:
                if item["distance"] < TOUCH_DISTANCE:
                    return item["object"]
        return ""

    def handle_touching(self, touching):
        if touching == "campfire":
            self.hunger = max(ENERGY_MIN, self.hunger - CAMPFIRE_HUNGER_RESTORE)
            print("Digimon eats from the campfire!")

    def think(self, nearby_str):
        prompt = build_prompt(
            self.hunger,
            self.energy,
            nearby_str,
            self.memory.get_context()
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
        touching = self.get_touching(nearby)
        self.handle_touching(touching)
        nearby_str = self.parse_nearby(nearby)

        try:
            result = self.think(nearby_str)

            thought = result.get("thought", "")
            direction = result.get("direction", "north")
            wait_time = max(WAIT_TIME_MIN, min(WAIT_TIME_MAX, int(result.get("wait_time", WAIT_TIME_DEFAULT))))

            self.memory.add(thought)

            print(f"Digimon thinks: {thought}")
            print(f"Direction: {direction} | Wait: {wait_time}s")
            if touching:
                print(f"Touching: {touching}")

            offset_x, offset_y = DIRECTIONS_TO_OFFSET.get(direction, (2000, 0))

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