import ollama
import json
from agent.prompt import build_prompt
from agent.needs import apply_hard_rules
from config import MODEL, WAIT_TIME_MIN, WAIT_TIME_MAX, WAIT_TIME_DEFAULT, FIXATION_TARGET_COUNT, CURIOSITY_MIN, CURIOSITY_DECREASE, LANGUAGE
from locales import REFLECTION_PROMPT, SYSTEM_MESSAGES, STOPWORDS


def think(digimon, nearby_str, touching="", spatial="", reflections=""):
    prompt = build_prompt(
        digimon.lore,
        digimon.hunger,
        digimon.energy,
        digimon.curiosity,
        nearby_str,
        digimon.memory.get_context(),
        touching=touching,
        spatial=spatial,
        reflections=reflections,
        semantic=digimon.memory.get_semantic_context()
    )
    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_MESSAGES.get(LANGUAGE, SYSTEM_MESSAGES["en"])},
            {"role": "user", "content": prompt}
        ]
    )
    text = response["message"]["content"].strip().replace("```json", "").replace("```", "").strip()
    return json.loads(text)


def extract_keywords(text):
    stopwords = STOPWORDS.get(LANGUAGE, STOPWORDS["en"])
    words = text.lower().split()
    keywords = []
    seen = set()
    for w in words:
        clean = w.strip(".,!?'\"")
        if clean not in stopwords and len(clean) > 3 and clean not in seen:
            seen.add(clean)
            keywords.append(clean)
    return keywords[:8]


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
        if target == "campfire" and digimon.hunger > 60:
            return False
        if target == "tent" and digimon.energy < 40:
            return False
        return True

    return False


def run_thought_cycle(digimon, nearby_str, touching):
    result = think(digimon, nearby_str, touching,
                   digimon.memory.get_spatial_context(),
                   digimon.memory.get_reflections_context())

    thought = result.get("thought", "")
    target = result.get("target", "explore")
    target = apply_hard_rules(digimon, target)
    wait_time = max(WAIT_TIME_MIN, min(WAIT_TIME_MAX, int(result.get("wait_time", WAIT_TIME_DEFAULT))))

    digimon.memory.add(thought)
    digimon.memory.add_target(target)
    if target == "explore":
        digimon.curiosity = max(CURIOSITY_MIN, digimon.curiosity - CURIOSITY_DECREASE)
    digimon.memory.cycle_count += 1
    if digimon.memory.cycle_count % 5 == 0:
        reflect(digimon)

    return target, thought, wait_time