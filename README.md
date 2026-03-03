# Agumon AI - Artificial Life in Unreal Engine 5

A personal experiment in artificial life where an Agumon autonomously inhabits a virtual forest, making decisions driven by an external Python-based brain.

## Description

The agent perceives its environment, maintains internal states (hunger, energy) and decides its actions without any user input. The goal is to observe what behaviors emerge from the interaction between the agent and its environment.

## Architecture

```
UE5 (body) ←→ Python (brain)
```

- **Unreal Engine 5** handles the 3D environment, navigation (NavMesh), animations and action execution
- **Python + Flask** contains the agent's logic: internal states, decision-making, and in the future memory and language
- Communication is bidirectional via **local HTTP** every N seconds

## Current Status

- [x] Bidirectional communication UE5 ↔ Python
- [x] Agumon navigates a forest using NavMesh
- [x] Internal state system (hunger, energy)
- [x] Autonomous decision-making based on needs
- [x] Animations (idle, walk)
- [ ] Environment perception (semantic zones)
- [ ] Persistent memory
- [ ] Natural language interaction (LLM)

## Technologies

- Unreal Engine 5.7
- Python 3.x
- Flask

## Project Structure

```
/
├── servidor.py          # Agent brain in Python
├── README.md
└── UE5/                 # Unreal Engine project
    └── BP_Agumon        # Agent Character Blueprint
```

## How to Run

**1. Start the Python server:**
```bash
pip install flask
python servidor.py
```

**2. Open the project in UE5 and press Play**

Agumon will start sending its position to Python every 5 seconds and receiving movement orders in return.

## Agent Brain (servidor.py)

The agent has three internal states that change over time:

- **Hunger**: increases over time. If it exceeds 70, the agent looks for food.
- **Energy**: decreases over time. If it drops below 30, the agent rests.
- **Curiosity**: reserved for future exploratory behavior.

The most urgent need determines the action.

## Motivation

To explore how far it is possible to simulate believable artificial life in a real-time 3D environment, combining game development tools with modern AI architectures.
