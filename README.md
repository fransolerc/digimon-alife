# Digimon ALife - Artificial Life in Unreal Engine 5

An experiment in artificial life where a Digimon agent autonomously inhabits a digital forest, making decisions driven by an LLM-based brain with spatial perception, internal needs and simulated time.

## Description

The agent perceives its environment through spatial awareness, maintains internal states (hunger, energy, curiosity) and reasons about its situation using a local LLM. The goal is to observe what behaviors emerge from the interaction between the agent and its environment, without explicit programming of those behaviors.

## Architecture
```
UE5 (body) ←→ Python (brain)
```

- **Unreal Engine 5** handles the 3D environment, navigation (NavMesh), animations, day/night cycle and action execution
- **Python + Flask** contains the agent's logic: internal states, spatial perception processing, LLM reasoning and memory
- **Ollama + Llama 3.2 3B Instruct** runs locally as the agent's reasoning engine
- Communication is bidirectional via **local HTTP**, frequency determined by the agent itself

## Current Status

- [x] Bidirectional communication UE5 ↔ Python
- [x] Agent navigates a forest using NavMesh
- [x] Internal state system (hunger, energy, curiosity)
- [x] Spatial perception (nearby objects with angle and distance)
- [x] LLM-based reasoning — thought generation only (navigation handled by Python)
- [x] Short-term memory (recent thoughts influence future decisions)
- [x] Spatial memory (known object locations persist across perception cycles)
- [x] Target-based movement (agent moves toward specific objects using absolute coordinates)
- [x] Touching detection (proximity-based interaction with environment)
- [x] Agent-controlled action frequency (wait_time)
- [x] Basic interaction with environment (campfire restores hunger, tent restores energy)
- [x] Persistent memory (save/load across sessions)
- [x] Reflection and abstraction from episodic memory
- [x] Fixation detection (forces exploration when agent gets stuck, need-aware)
- [x] AI Perception (vision cone)
- [x] Animations (idle, walk)
- [x] Multiple agent architecture (each Digimon has its own identity and memory)
- [x] Automatic lore generation from Digimon database
- [x] Associative memory (episodic events and semantic thoughts in SPO format)
- [x] Explored zones (UE5 handles exploration, notifies Python of visited zones)
- [x] Separate perception endpoint for real-time spatial memory updates
- [x] Multilanguage support (configurable via LANGUAGE in config.py)
- [x] Causal learning from experience (campfire→hunger_reduction, tent→energy_restoration)
- [x] Explicit need state instructions in prompt (SATISFIED/HUNGRY/RESTED/TIRED)
- [x] Object glossary in prompt to prevent LLM hallucinations on English tags
- [x] LLM/Python responsibility split — LLM generates thought, Python owns all navigation decisions
- [x] Systematic exploration via spatial map (2D grid, directs agent toward unknown cells)
- [x] Context deduplication (filters redundant entries before sending to LLM)
- [x] Simulated time (SimClock synced with UE5 day/night cycle, 1 min real = 1 hour in-game)
- [x] Temporal context in prompt (current time and period injected each cycle)
- [x] Timestamps on causal memory nodes (events annotated with in-game time)
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
├── config.py                    # Configuration and parameters
├── locales.py                   # Localized strings (EN/ES) for lore, prompts and reflections
├── utils.py                     # Shared utilities (keyword extraction)
├── dashboard.html               # Real-time browser monitor (open directly, no build step)
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
│       ├── sim_clock.py         # Simulated time clock, synced with UE5 pitch rotation
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

The agent will begin perceiving its environment, reasoning about what it finds and deciding where to go autonomously.

**4. Open `dashboard.html` in a browser to monitor the agent in real time.**

## Configuration

Key parameters in `config.py`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `LANGUAGE` | `"es"` | Agent language (`"en"` or `"es"`) |
| `TOUCH_DISTANCE` | `200` | Distance to consider an object as touched |
| `FIXATION_TARGET_COUNT` | `10` | Cycles before fixation is detected |
| `WAIT_TIME_MIN` / `MAX` | `8` / `20` | LLM wait time range in seconds |
| `HUNGER_CAMPFIRE_THRESHOLD` | `25` | Below this hunger → agent is satisfied |
| `HUNGER_FORCE_THRESHOLD` | `70` | Above this hunger → force campfire regardless of LLM |
| `ENERGY_TENT_THRESHOLD` | `80` | Above this energy → agent is rested |
| `ENERGY_FORCE_THRESHOLD` | `30` | Below this energy → force tent regardless of LLM |
| `MAX_ASSOCIATIVE_NODES` | `200` | Max nodes in associative memory (trimmed by poignancy) |

All localized strings (lore, prompts, reflections, stopwords, state labels, object glossary) are in `locales.py`.

## HTTP Endpoints

- **POST /think** — main thought cycle. Receives `id`, `x`, `y`, `pitch_rotation`. Returns `thought` and `target`.
- **POST /move** — movement calculation. Returns absolute world coordinates (`target_x`, `target_y`) toward current target.
- **POST /perception** — real-time spatial update. Called on every AI Perception event, updates spatial memory with absolute coordinates of detected objects.
- **POST /explored** — notifies Python when the agent reaches an exploration destination. Stores visited zone coordinates.
- **POST /position** — updates agent position and checks touch interactions.
- **GET /debug/\<agent_id\>** — full agent state for the dashboard (needs, memory, spatial map, sim clock, position).

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

### Simulated Time

`SimClock` maintains an in-game clock synced with UE5's DirectionalLight pitch rotation. One real minute equals one in-game hour (full day = 24 minutes). UE5 sends `pitch_rotation` on each `/think` call; Python converts it to `HH:MM` with a −90° offset (270° = 12:00).

The current time and period (mañana / tarde / noche / madrugada) are injected into the LLM prompt each cycle. Causal memory nodes are annotated with in-game timestamps.

### Systematic Exploration

`SpatialMap` maintains a 40×40 grid over the UE5 world (−10000 to 10000, cell size 500 UU). Cells are marked as explored when the agent visits them and as known when objects are detected via AI Perception. When exploring, `get_explore_target()` returns the world-space center of the nearest unknown cell, replacing random wandering with systematic coverage.

Spatial memory is updated continuously via `/perception` whenever AI Perception detects objects. Every 5 cycles the agent reflects on recent thoughts and generates a higher-level conclusion. Fixation detection fires when the same target is chosen repeatedly, respecting genuine needs.

Each Digimon is identified by a unique ID. The server maintains a separate agent instance and memory file per Digimon. Lore is generated automatically from the Digimon database.

## Memory Architecture

- **Episodic memory**: recent thoughts in natural language, deduplicated by keyword overlap before being sent to the LLM (threshold 0.4, compared against all previously accepted entries)
- **Spatial memory**: known object locations with absolute world coordinates, updated in real-time via AI Perception
- **Spatial map**: 2D grid tracking explored cells and object positions, used to direct exploration toward unknown areas
- **Associative memory**: structured nodes in subject-predicate-object format (events, causal facts and thoughts), with poignancy scores and keyword-based retrieval. Capped at `MAX_ASSOCIATIVE_NODES`, trimmed by poignancy.
- **Explored zones**: coordinates of visited exploration points, populated by UE5 via `/explored`
- **SimClock**: in-game time derived from UE5 pitch rotation, persisted across sessions

## Causal Learning

When the agent interacts with an object, a causal node is stored in associative memory:

- `campfire causes hunger_reduction` — learned after eating
- `tent causes energy_restoration` — learned after resting

These nodes have high poignancy (8), are annotated with in-game timestamps, and appear in the LLM's semantic context on subsequent cycles, grounding its reasoning in learned experience rather than pure instruction-following.

## Dashboard

Open `dashboard.html` directly in a browser (no server required). Connects to the Flask server on `localhost:5000` and polls `/debug/<agent_id>` every 3 seconds. Displays:

- Hunger, energy and curiosity bars
- Current in-game time and period
- Spatial map with explored cells, known objects and agent position
- Thought log and reflections
- Target history
- Associative memory node count

## Motivation

To explore how far it is possible to simulate believable artificial life in a real-time 3D environment, combining game development tools with modern AI architectures. Inspired by artificial life research from the 90s and the philosophical questions around emergence, intelligence and consciousness in digital entities.