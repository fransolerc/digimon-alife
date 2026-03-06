from config import (
    HUNGER_MAX, HUNGER_MIN, ENERGY_MAX, ENERGY_MIN, CURIOSITY_MAX,
    HUNGER_INCREASE, ENERGY_DECREASE, CURIOSITY_INCREASE,
    HUNGER_EAT, ENERGY_RESTORE
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


def apply_hard_rules(digimon, target):
    if target == "campfire" and digimon.hunger < 40:
        return "explore"
    if target == "tent" and digimon.energy > 80:
        return "explore"
    return target