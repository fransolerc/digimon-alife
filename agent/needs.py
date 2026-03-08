from config import (
    HUNGER_MAX, HUNGER_MIN, ENERGY_MAX, ENERGY_MIN, CURIOSITY_MAX,
    HUNGER_INCREASE, ENERGY_DECREASE, CURIOSITY_INCREASE,
    HUNGER_EAT, ENERGY_RESTORE,
    HUNGER_CAMPFIRE_THRESHOLD, ENERGY_TENT_THRESHOLD,
    HUNGER_FORCE_THRESHOLD, ENERGY_FORCE_THRESHOLD
)


def update_needs(digimon):
    digimon.hunger = min(HUNGER_MAX, digimon.hunger + HUNGER_INCREASE)
    digimon.energy = max(ENERGY_MIN, digimon.energy - ENERGY_DECREASE)
    digimon.curiosity = min(CURIOSITY_MAX, digimon.curiosity + CURIOSITY_INCREASE)


def handle_touching(digimon, touching):
    if touching == "campfire":
        old_hunger = digimon.hunger
        digimon.hunger = max(HUNGER_MIN, digimon.hunger - HUNGER_EAT)
        digimon.memory.add_event_node(
            subject=digimon.agent_id,
            predicate="touched",
            obj="campfire",
            description=f"{digimon.agent_id} touched campfire, hunger decreased from {old_hunger:.0f} to {digimon.hunger:.0f}",
            poignancy=6,
            keywords=["campfire", "hunger", "food"]
        )
        digimon.memory.add_event_node(
            subject="campfire",
            predicate="causes",
            obj="hunger_reduction",
            description=f"Touching the campfire reduces hunger. After eating, hunger was {digimon.hunger:.0f}/100 — no need to eat again soon.",
            poignancy=8,
            keywords=["campfire", "hunger", "food", "satisfied", "eat"]
        )
    elif touching == "tent":
        old_energy = digimon.energy
        digimon.energy = min(ENERGY_MAX, digimon.energy + ENERGY_RESTORE)
        digimon.memory.add_event_node(
            subject=digimon.agent_id,
            predicate="touched",
            obj="tent",
            description=f"{digimon.agent_id} touched tent, energy increased from {old_energy:.0f} to {digimon.energy:.0f}",
            poignancy=6,
            keywords=["tent", "energy", "rest"]
        )
        digimon.memory.add_event_node(
            subject="tent",
            predicate="causes",
            obj="energy_restoration",
            description=f"Resting in the tent restores energy. After resting, energy was {digimon.energy:.0f}/100 — no need to rest again soon.",
            poignancy=8,
            keywords=["tent", "energy", "rest", "rested", "sleep"]
        )


def apply_hard_rules(digimon, target):
    # Force target when needs are critical
    if digimon.hunger > HUNGER_FORCE_THRESHOLD:
        return "campfire"
    if digimon.energy < ENERGY_FORCE_THRESHOLD:
        return "tent"

    # Block target when need is already satisfied
    if target == "campfire" and digimon.hunger < HUNGER_CAMPFIRE_THRESHOLD:
        return "explore"
    if target == "tent" and digimon.energy > ENERGY_TENT_THRESHOLD:
        return "explore"

    return target