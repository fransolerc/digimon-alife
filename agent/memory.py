# agent/memory.py
from config import MEMORY_MAX_SIZE, MEMORY_CONTEXT_SIZE

class Memory:
    def __init__(self):
        self.entries = []

    def add(self, thought):
        if thought:
            self.entries.append(thought)
            if len(self.entries) > MEMORY_MAX_SIZE:
                self.entries.pop(0)

    def get_context(self):
        recent = self.entries[-MEMORY_CONTEXT_SIZE:]
        return "\n".join(recent) if recent else "Nada aún."

    def clear(self):
        self.entries = []