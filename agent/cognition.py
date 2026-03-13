import ollama
import json
from agent.prompt import build_prompt
from agent.needs import decide_target, update_needs
from config import MODEL, FIXATION_TARGET_COUNT, CURIOSITY_MIN, CURIOSITY_DECREASE, LANGUAGE, HUNGER_CAMPFIRE_THRESHOLD, ENERGY_TENT_THRESHOLD
from locales import REFLECTION_PROMPT, SYSTEM_MESSAGES
from utils import extract_keywords


def build_context_keywords(digimon):
    keywords = set()

    if digimon.hunger > HUNGER_CAMPFIRE_THRESHOLD:
        keywords.update(["hunger", "campfire", "food", "eat"])
    else:
        keywords.update(["satisfied", "saciado"])

    if digimon.energy < ENERGY_TENT_THRESHOLD:
        keywords.update(["energy", "tent", "rest", "tired"])
    else:
        keywords.update(["rested", "descansado"])

    for obj_name in digimon.memory.spatial.keys():
        keywords.add(obj_name.lower())

    if digimon.memory.entries:
        last_thought_keywords = extract_keywords(digimon.memory.entries[-1])
        keywords.update(last_thought_keywords)

    return list(keywords)


def think(digimon, spatial="", reflections="", context_keywords=None):
    semantic = digimon.memory.get_relevant_context(context_keywords) if context_keywords else digimon.memory.get_semantic_context()

    prompt = build_prompt(
        digimon.lore,
        digimon.hunger,
        digimon.energy,
        digimon.curiosity,
        digimon.memory.get_context(),
        spatial=spatial,
        reflections=reflections,
        semantic=semantic
    )
    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_MESSAGES.get(LANGUAGE, SYSTEM_MESSAGES["en"])},
            {"role": "user", "content": prompt}
        ]
    )
    text = response["message"]["content"].strip().replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}\nRaw LLM output: {text}")
        return {"thought": "..."}


def reflect(digimon):
    if len(digimon.memory.entries) < 5:
        return

    thoughts = "\n".join(digimon.memory.entries[-5:])
    prompt = REFLECTION_PROMPT.get(LANGUAGE, REFLECTION_PROMPT["en"]).format(
        agent_name=digimon.agent_id,
        thoughts=thoughts
    )

    try:
        response = ollama.chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_MESSAGES.get(LANGUAGE, SYSTEM_MESSAGES["en"])},
                {"role": "user", "content": prompt}
            ]
        )
        reflection = response["message"]["content"].strip()
        digimon.memory.add_reflection(reflection)
        digimon.memory.add_thought_node(
            subject=digimon.agent_id,
            predicate="reflects",
            obj="experience",
            description=reflection,
            poignancy=7,
            keywords=extract_keywords(reflection)
        )
        if check_fixation(digimon):
            digimon.memory.force_explore = True
    except Exception as e:
        print(f"Reflection error: {e}")


def check_fixation(digimon):
    if len(digimon.memory.recent_targets) < FIXATION_TARGET_COUNT:
        return False

    last_targets = digimon.memory.recent_targets[-FIXATION_TARGET_COUNT:]
    if len(set(last_targets)) == 1:
        target = last_targets[0]
        if target == "campfire" and digimon.hunger > HUNGER_CAMPFIRE_THRESHOLD:
            return False
        if target == "tent" and digimon.energy < ENERGY_TENT_THRESHOLD:
            return False
        return True

    return False


def run_thought_cycle(digimon):
    update_needs(digimon)

    context_keywords = build_context_keywords(digimon)

    result = think(digimon,
                   digimon.memory.get_spatial_context(),
                   digimon.memory.get_reflections_context(),
                   context_keywords=context_keywords)

    thought = result.get("thought", "")
    target = decide_target(digimon)

    if digimon.memory.force_explore:
        digimon.memory.force_explore = False
        target = "explore"

    digimon.memory.add(thought)
    digimon.memory.add_target(target)
    if target == "explore":
        digimon.curiosity = max(CURIOSITY_MIN, digimon.curiosity - CURIOSITY_DECREASE)
    digimon.memory.cycle_count += 1
    if digimon.memory.cycle_count % 5 == 0:
        reflect(digimon)

    return target, thought