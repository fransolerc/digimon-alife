from agent.memory.memory import Memory
from agent.needs import update_needs, handle_touching
from agent.movement import determine_action
from agent.perception import get_touching_from_spatial
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
        self.current_target = "explore"

    def _update_state(self, data):
        self.x = data.get("x", 0)
        self.y = data.get("y", 0)

    def think_cycle(self, data):
        if self.processing:
            return {"thought": "", "target": self.current_target, "wait_time": 3}

        self.processing = True
        try:
            self._update_state(data)

            # 1. update needs (hunger increases, energy decreases)
            update_needs(self)

            # 2. apply touching effects BEFORE building prompt
            touching = get_touching_from_spatial(self.x, self.y, self.memory.spatial)
            handle_touching(self, touching)

            # 3. LLM reasons with the fully updated state
            target, thought, wait_time = run_thought_cycle(self, touching)
            self.current_target = target

            self.memory.hunger = self.hunger
            self.memory.energy = self.energy
            self.memory.curiosity = self.curiosity
            self.memory.save()

            return {
                "thought": thought,
                "target": target,
                "wait_time": wait_time
            }

        except Exception as e:
            print(f"Error: {e}")
            return {"thought": "...", "target": "explore", "wait_time": WAIT_TIME_DEFAULT}

        finally:
            self.processing = False

    def move_cycle(self, data):
        self._update_state(data)
        if self.current_target == "idle":
            return {"target_x": 0, "target_y": 0}
        result = determine_action(self, self.current_target)
        if result is None:
            return {"target_x": 0, "target_y": 0}
        x, y = result
        return {"target_x": x, "target_y": y}