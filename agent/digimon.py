from agent.memory.memory import Memory
from agent.movement import determine_action
from agent.cognition import run_thought_cycle
import traceback

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


    def think_cycle(self, pitch_rotation=None):
        if self.processing:
            return {"thought": "", "target": "error"}

        self.processing = True
        try:
            target, thought = run_thought_cycle(self, pitch_rotation=pitch_rotation)
            self.current_target = target

            self.memory.hunger = self.hunger
            self.memory.energy = self.energy
            self.memory.curiosity = self.curiosity
            self.memory.save()

            return {
                "thought": thought,
                "target": target
            }

        except Exception:
            traceback.print_exc()
            return {"thought": "", "target": "error"}

        finally:
            self.processing = False

    def move_cycle(self, data):
        self.x = data.get("x", 0)
        self.y = data.get("y", 0)
        if self.current_target == "idle":
            return {"target_x": 0, "target_y": 0}
        result = determine_action(self, self.current_target)
        if result is None:
            return {"target_x": 0, "target_y": 0}
        x, y = result
        return {"target_x": x, "target_y": y}