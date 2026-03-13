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
- **Ollama + Llama 3.2 3B Instruct** runs locally as the agent's reasoning engine
- Communication is bidirectional via **local HTTP**, frequency determined by the agent itself

## Current Status

- [x] Bidirectional communication UE5 ↔ Python
- [x] Agumon navigates a forest using NavMesh
- [x] Internal state system (hunger, energy, curiosity)
- [x] Spatial perception (nearby objects with angle and distance)
- [x] LLM-based reasoning — thought generation only (navigation handled by Python)
- [x] Short-term memory (recent thoughts influence future decisions)
- [x] Spatial memory (known object locations persist across perception cycles)
- [x] Target-based movement (agent moves toward specific objects using absolute coordinates)
- [x] Touching detection (proximity-based interaction with environment, via /position)
- [x] Basic interaction with environment (campfire restores hunger, tent restores energy)
- [x] Persistent memory (save/load across sessions)
- [x] Reflection and abstraction from episodic memory
- [x] Fixation detection (forces exploration when agent gets stuck, need-aware)
- [x] AI Perception (vision cone)
- [x] Animations (idle, walk)
- [x] Multiple agent architecture (each Digimon has its own identity and memory)
- [x] Automatic lore generation from Digimon database
- [x] Associative memory (episodic events and semantic thoughts in SPO format)
- [x] Active associative memory retrieval (keyword-based, context-aware)
- [x] Explored zones (UE5 handles exploration, notifies Python of visited zones)
- [x] Separate perception endpoint for real-time spatial memory updates
- [x] Multilanguage support (configurable via LANGUAGE in config.py)
- [x] Causal learning from experience (campfire→hunger_reduction, tent→energy_restoration)
- [x] Explicit need state instructions in prompt (SATISFIED/HUNGRY/RESTED/TIRED)
- [x] Object glossary in prompt to prevent LLM hallucinations on English tags
- [x] Full separation of LLM thought and Python-driven target selection
- [x] Terminal communication device (experimental branch)
- [x] Browser-based real-time dashboard (dashboard.html, polls /debug every 3s)
- [ ] Multiple Digimon agents (second agent in UE5)

## Technologies

- Unreal Engine 5.7
- Python 3.x
- Flask
- Ollama + Llama 3.2 3B Instruct

## Project Structure
```
/
├── main.py                      # Flask server entry point, agent registry
├── dashboard.html               # Real-time dashboard for debugging and visualization
├── config.py                    # Configuration and parameters
├── locales.py                   # Localized strings (EN/ES) for lore, prompts and reflections
├── utils.py                     # Shared utilities (keyword extraction)
├── agent/
│   ├── digimon.py               # Agent orchestrator
│   ├── cognition.py             # LLM reasoning, reflection, fixation detection
│   ├── perception.py            # Touch detection
│   ├── needs.py                 # Internal state updates and need-based target selection
│   ├── movement.py              # Target resolution toward known objects or spatial map
│   ├── lore.py                  # Automatic lore generation from Digimon database
│   ├── prompt.py                # LLM prompt construction
│   └── memory/
│       ├── __init__.py
│       ├── memory.py            # Main memory manager (episodic, spatial, associative, spatial map)
│       ├── associative_memory.py # Associative memory with keyword-based retrieval
│       ├── spatial_map.py       # 2D grid map for systematic exploration
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
ollama pull llama3.2:3b
```

**2. Start the Python server:**
```bash
pip install flask ollama
python main.py
```

**3. Open the project in UE5 and press Play**

Agumon will begin perceiving its environment, reasoning about what it finds and deciding where to go autonomously.

## Configuration

Key parameters in `config.py`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `LANGUAGE` | `"es"` | Agent language (`"en"` or `"es"`) |
| `TOUCH_DISTANCE` | `200` | Distance to consider an object as touched |
| `FIXATION_TARGET_COUNT` | `10` | Cycles before fixation is detected |
| `HUNGER_CAMPFIRE_THRESHOLD` | `25` | Below this hunger → agent is satisfied |
| `HUNGER_FORCE_THRESHOLD` | `70` | Above this hunger → force campfire |
| `ENERGY_TENT_THRESHOLD` | `80` | Above this energy → agent is rested |
| `ENERGY_FORCE_THRESHOLD` | `30` | Below this energy → force tent |
| `MEMORY_CONTEXT_SIZE` | `5` | Number of recent thoughts passed to LLM |
| `MAX_ASSOCIATIVE_NODES` | `200` | Max nodes in associative memory (trimmed by poignancy) |

All localized strings (lore, prompts, reflections, stopwords, state labels, object glossary) are in `locales.py`.

## HTTP Endpoints

- **POST /think** — main thought cycle. Receives `id`, returns `thought` and `target`.
- **POST /position** — position update and touch detection. Receives `id`, `x`, `y`. Returns `touching`.
- **POST /move** — movement calculation. Returns absolute world coordinates (`target_x`, `target_y`) toward current target.
- **POST /perception** — real-time spatial update. Called on every AI Perception event, updates spatial memory with absolute coordinates of detected objects.
- **POST /explored** — notifies Python when Agumon reaches an exploration destination. Stores visited zone coordinates.
- **GET /status** — debug endpoint. Returns current internal states for all agents.
- **GET /debug/\<agent_id\>** — full agent state for the dashboard (needs, memory, spatial map, position).

## Agent Brain

The agent has three internal states that evolve over time:

- **Hunger**: increases over time. Restored by interacting with campfires.
- **Energy**: decreases over time. Restored by resting in the tent.
- **Curiosity**: increases over time. Decreases when exploring new areas.

### LLM / Python Responsibility Split

The LLM is responsible only for generating a free internal `thought` — an expression of the agent's current mental state. All navigation decisions are owned by Python via `decide_target()` in `needs.py`, which applies a priority-ordered need hierarchy:

1. Force campfire if hunger > `HUNGER_FORCE_THRESHOLD`
2. Force tent if energy < `ENERGY_FORCE_THRESHOLD`
3. Go to campfire if hunger > `HUNGER_CAMPFIRE_THRESHOLD`
4. Go to tent if energy < `ENERGY_TENT_THRESHOLD`
5. Explore otherwise

This separation eliminates cognitive dissonance where the agent's thoughts contradicted its actions, and produces noticeably richer, more introspective LLM output.

On each think cycle UE5 routes the decision via Switch on String:

- **Known object** (campfire, tent, etc.) → calls `/move` → receives absolute coordinates → AI MoveTo
- **explore** → calls `/move` → receives spatial map target → uses as center for `Get Random Reachable Point in Radius` → AI MoveTo → notifies `/explored` on success
- **idle** → waits wait_time seconds → new think cycle

### Systematic Exploration

`SpatialMap` maintains a 40×40 grid over the UE5 world (−10000 to 10000, cell size 500 UU). Cells are marked as explored when Agumon visits them and as known when objects are detected via AI Perception. When the agent explores, `get_explore_target()` returns the world-space center of the nearest unknown cell, replacing random wandering with systematic coverage. The map is serialized to `spatial_map` in the memory JSON file.

Spatial memory is updated continuously via `/perception` whenever AI Perception detects objects. Every 5 cycles Agumon reflects on recent thoughts and generates a higher-level conclusion. Fixation detection fires when the same target is chosen repeatedly, respecting genuine needs.

Each Digimon is identified by a unique ID. The server maintains a separate agent instance and memory file per Digimon. Lore is generated automatically from the Digimon database.

## Memory Architecture

- **Episodic memory**: recent thoughts in natural language, deduplicated by keyword overlap before being sent to the LLM (threshold 0.4, compared against all previously accepted entries)
- **Spatial memory**: known object locations with absolute world coordinates, updated in real-time via AI Perception
- **Spatial map**: 2D grid tracking explored cells and object positions, used to direct exploration toward unknown areas
- **Associative memory**: structured nodes in subject-predicate-object format (events, causal facts and thoughts), with poignancy scores and keyword-based retrieval. Capped at `MAX_ASSOCIATIVE_NODES`, trimmed by poignancy.
- **Explored zones**: coordinates of visited exploration points, populated by UE5 via `/explored`

## Associative Memory Retrieval

On each think cycle, keywords are derived from the agent's current state — active needs, known spatial objects, and last thought. These keywords drive a scored retrieval over the associative memory nodes, combining keyword overlap with poignancy. The LLM receives the most contextually relevant nodes rather than always the same high-poignancy ones, grounding its reasoning in what matters right now.

## Causal Learning

When Agumon interacts with an object, a causal node is stored in associative memory:

- `campfire causes hunger_reduction` — learned after eating
- `tent causes energy_restoration` — learned after resting

These nodes have high poignancy (8) and are retrieved when relevant needs are active, grounding the agent's reasoning in learned experience.

## Design Principles

- **LLM provides expression, Python handles logic** — the LLM generates `thought` as a free internal reflection. Python owns all navigation, state management and rule enforcement.
- **Python owns reliability-critical decisions** — need thresholds, target selection, fixation detection, coordinate math.
- **Context relevance over static ranking** — associative memory retrieval is driven by the current moment, not fixed poignancy scores.
- **Constants centralized in `config.py`** — all tunable parameters in one place.
- **Localized strings in `locales.py`** — all prompt text, lore, and labels support EN/ES.

## Motivation

To explore how far it is possible to simulate believable artificial life in a real-time 3D environment, combining game development tools with modern AI architectures. Inspired by artificial life research from the 90s and the philosophical questions around emergence, intelligence and consciousness in digital entities.