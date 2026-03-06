from agent.memory.memory import Memory
from agent.perception import parse_nearby, get_touching
from agent.needs import update_needs, handle_touching
from agent.movement import determine_action
from agent.cognition import run_thought_cycle
from config import WAIT_TIME_DEFAULT


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

    def _update_state(self, data):
        self.x = data.get("x", 0)
        self.y = data.get("y", 0)
        self.memory.add_explored_zone(self.x, self.y)

    def process(self, data):
        if self.processing:
            return {"offset_x": 0, "offset_y": 0, "thought": "", "wait_time": WAIT_TIME_DEFAULT}

        self.processing = True
        try:
            update_needs(self)
            self._update_state(data)

            nearby = data.get("nearby", [])
            touching = get_touching(nearby)
            handle_touching(self, touching)
            nearby_str = parse_nearby(nearby)
            self.memory.update_spatial(self.x, self.y, nearby)

            target, thought, wait_time = run_thought_cycle(self, nearby_str, touching)
            offset_x, offset_y = determine_action(self, target, nearby)

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