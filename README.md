# Digimon ALife - Artificial Life in Unreal Engine 5

An experiment in artificial life where an Agumon autonomously inhabits a digital forest, making decisions driven by an LLM-based brain with spatial perception and internal needs.

## Description

The agent perceives its environment through spatial awareness, maintains internal states (hunger, energy, curiosity) and reasons about its situation using a local LLM. The goal is to observe what behaviors emerge from the interaction between the agent and its environment, without explicit programming of those behaviors.

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
- [x] Internal state system (hunger, energy, curiosity)
- [x] Spatial perception (nearby objects with angle and distance)
- [x] LLM-based reasoning and decision-making in natural language
- [x] Short-term memory (recent thoughts influence future decisions)
- [x] Spatial memory (known object locations persist across perception cycles)
- [x] Target-based movement (agent moves toward specific objects using angle and distance)
- [x] Touching detection (proximity-based interaction with environment)
- [x] Agent-controlled action frequency (wait_time)
- [x] Basic interaction with environment (campfire restores hunger, tent restores energy)
- [x] Persistent memory (save/load across sessions)
- [x] Reflection and abstraction from episodic memory
- [x] Fixation detection (forces exploration when agent gets stuck)
- [x] AI Perception (vision cone)
- [x] Animations (idle, walk)
- [x] Multiple agent architecture (each Digimon has its own identity and memory)
- [x] Automatic lore generation from Digimon database
- [x] Associative memory (episodic events and semantic thoughts in SPO format)
- [x] Explored zones (intelligent exploration of unvisited areas)
- [x] Separate perception endpoint for real-time spatial memory updates
- [ ] Multiple Digimon agents (second agent in UE5)
- [ ] Causal learning from experience

## Technologies

- Unreal Engine 5.7
- Python 3.x
- Flask
- Ollama + Gemma 3 4B

## Project Structure

```
/
├── main.py                      # Flask server entry point, agent registry
├── config.py                    # Configuration and parameters
├── agent/
│   ├── digimon.py               # Agent orchestrator
│   ├── cognition.py             # LLM reasoning, reflection, fixation detection
│   ├── perception.py            # Nearby object parsing and touch detection
│   ├── needs.py                 # Internal state updates and hard behavioral rules
│   ├── movement.py              # Target resolution and exploration offset
│   ├── lore.py                  # Automatic lore generation from Digimon database
│   ├── prompt.py                # LLM prompt construction
│   ├── utils.py                 # Mathematical utility functions
│   └── memory/
│       ├── __init__.py
│       ├── memory.py            # Main memory manager (episodic, spatial, associative)
│       ├── associative_memory.py # Associative memory with keyword-based retrieval
│       └── concept_node.py      # ConceptNode: SPO-structured memory unit
├── db/
│   └── digimon.json             # Digimon database (name, level, type, digivolutions)
├── data/                        # Persistent memory per agent (local only, not tracked)
├── README.md
└── UE5/                         # Unreal Engine project
    └── BP_Digimon               # Agent Character Blueprint (base class)
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

## HTTP Endpoints

- **POST /state** — main thought cycle. Receives agent position, returns movement offset and thought.
- **POST /perception** — real-time spatial update. Called on every AI Perception event, updates spatial memory independently of the thought cycle.
- **GET /status** — debug endpoint. Returns current internal states for all agents.

## Agent Brain

The agent has three internal states that evolve over time:

- **Hunger**: increases over time. Restored by interacting with campfires.
- **Energy**: decreases over time. Restored by resting in the tent.
- **Curiosity**: increases over time. Decreases when exploring new areas.

Each decision cycle the agent receives its current position, reasons about its situation using an LLM and decides a target object or free exploration. Movement is calculated mathematically from known object coordinates in spatial memory, not interpreted by the LLM. Spatial memory is updated continuously via the `/perception` endpoint whenever AI Perception detects new objects.

Every 5 cycles Agumon reflects on its recent thoughts and generates a higher-level conclusion. If fixation is detected (same target chosen repeatedly), exploration is forced to break the loop. When exploring, Agumon prefers unvisited areas of the map using an explored zones system.

Each Digimon is identified by a unique ID sent in the POST payload. The server maintains a separate agent instance and memory file per Digimon, making it straightforward to add new agents with different identities and lore. Lore is generated automatically from the Digimon database based on the agent ID.

## Memory Architecture

The agent maintains three distinct memory systems:

- **Episodic memory**: recent thoughts in natural language, provides short-term context
- **Spatial memory**: known object locations with coordinates and timestamps, updated in real-time via AI Perception
- **Associative memory**: structured nodes in subject-predicate-object format, split into events (concrete interactions) and thoughts (abstract reflections). Each node has a poignancy score and keywords for relevance-based retrieval.

## Motivation

To explore how far it is possible to simulate believable artificial life in a real-time 3D environment, combining game development tools with modern AI architectures. Inspired by artificial life research from the 90s and the philosophical questions around emergence, intelligence and consciousness in digital entities.
