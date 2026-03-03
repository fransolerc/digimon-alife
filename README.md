# Digimon ALife - Artificial Life in Unreal Engine 5

An experiment in artificial life where an Agumon autonomously inhabits a digital forest, making decisions driven by an LLM-based brain with spatial perception and internal needs.

## Description

The agent perceives its environment through spatial awareness, maintains internal states (hunger, energy) and reasons about its situation using a local LLM. The goal is to observe what behaviors emerge from the interaction between the agent and its environment, without explicit programming of those behaviors.

## Architecture

```
UE5 (body) ←→ Python (brain)
```

- **Unreal Engine 5** handles the 3D environment, navigation (NavMesh), animations and action execution
- **Python + Flask** contains the agent's logic: internal states, spatial perception processing, LLM reasoning and memory
- **Ollama + Gemma 3 4B** runs locally as the agent's reasoning engine
- Communication is bidirectional via **local HTTP**, frequency determined by the agent itself

## Current Status

- [x] Bidirectional communication UE5 ↔ Python
- [x] Agumon navigates a forest using NavMesh
- [x] Internal state system (hunger, energy)
- [x] Spatial perception (nearby objects with angle and distance)
- [x] LLM-based reasoning and decision-making in natural language
- [x] Short-term memory (recent thoughts influence future decisions)
- [x] Spatial memory (known object locations persist across perception cycles)
- [x] Target-based movement (agent moves toward specific objects using angle and distance)
- [x] Touching detection (proximity-based interaction with environment)
- [x] Agent-controlled action frequency (wait_time)
- [x] Basic interaction with environment (campfire restores hunger)
- [x] Animations (idle, walk)
- [ ] Persistent memory (save/load across sessions)
- [ ] Reflection and abstraction from episodic memory
- [ ] Multiple Digimon agents
- [ ] AI Perception (vision cone)
- [ ] Causal learning from experience

## Technologies

- Unreal Engine 5.7
- Python 3.x
- Flask
- Ollama + Gemma 3 4B

## Project Structure

```
/
├── main.py              # Flask server entry point
├── config.py            # Configuration and parameters
├── agent/
│   ├── digimon.py       # Agent logic and state
│   ├── memory.py        # Short-term and spatial memory system
│   └── prompt.py        # LLM prompt construction and lore
├── README.md
└── UE5/                 # Unreal Engine project
    └── BP_Agumon        # Agent Character Blueprint
```

## How to Run

**1. Install Ollama and pull the model:**
```bash
ollama pull gemma3:4b
```

**2. Start the Python server:**
```bash
pip install flask ollama
python main.py
```

**3. Open the project in UE5 and press Play**

Agumon will begin perceiving its environment, reasoning about what it finds and deciding where to go autonomously.

## Agent Brain

The agent has two internal states that evolve over time:

- **Hunger**: increases over time. Restored by interacting with food sources like campfires.
- **Energy**: decreases over time. Reserved for future rest behavior.

Each decision cycle the agent receives nearby objects with their angle and distance, reasons about its situation using an LLM and decides a target object or free exploration. Movement is calculated mathematically from the angle and distance to the target, not interpreted by the LLM. Known object locations are stored in spatial memory and provided as context for future decisions.

## Motivation

To explore how far it is possible to simulate believable artificial life in a real-time 3D environment, combining game development tools with modern AI architectures. Inspired by artificial life research from the 90s and the philosophical questions around emergence, intelligence and consciousness in digital entities.
