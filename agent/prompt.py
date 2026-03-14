from config import LANGUAGE, HUNGER_CAMPFIRE_THRESHOLD, ENERGY_TENT_THRESHOLD
from locales import PROMPT_STRINGS, LANGUAGE_INSTRUCTIONS, STATE_LABELS


def _need_instructions(hunger, energy):
    labels = STATE_LABELS.get(LANGUAGE, STATE_LABELS["en"])
    h = f"{hunger:.0f}"
    e = f"{energy:.0f}"
    hunger_str = labels["satisfied"].format(h=h) if hunger < HUNGER_CAMPFIRE_THRESHOLD else labels["hungry"].format(h=h)
    energy_str = labels["rested"].format(e=e) if energy > ENERGY_TENT_THRESHOLD else labels["tired"].format(e=e)
    return f"{hunger_str}\n{energy_str}"


def build_prompt(lore, hunger, energy, curiosity, history,
                 spatial="", reflections="", semantic="",
                 time_str="", period=""):
    s = PROMPT_STRINGS.get(LANGUAGE, PROMPT_STRINGS["en"])
    language_instruction = LANGUAGE_INSTRUCTIONS.get(LANGUAGE, LANGUAGE_INSTRUCTIONS["en"])

    spatial_str = s["known_locations"].format(spatial=spatial) if spatial else s["no_locations"]
    reflections_str = s["reflections"].format(reflections=reflections) if reflections else s["no_reflections"]
    semantic_str = s["learned"].format(semantic=semantic) if semantic else s["not_learned"]
    need_str = _need_instructions(hunger, energy)
    time_line = f"Son las {time_str} ({period})." if time_str else ""

    return f"""{lore}
{language_instruction}
{s["state"].format(h=f"{hunger:.0f}", e=f"{energy:.0f}", c=f"{curiosity:.0f}")}
{time_line}
{need_str}
{spatial_str}
{reflections_str}
{semantic_str}
{s["recent_thoughts"].format(history=history)}

{s["question"]}
{s["reply"]}
{{"thought": "..."}}"""