from config import WAIT_TIME_MIN, WAIT_TIME_MAX, LANGUAGE
from locales import PROMPT_STRINGS, LANGUAGE_INSTRUCTIONS


def build_prompt(lore, hunger, energy, curiosity, nearby_str, history, touching="", spatial="", reflections="", semantic=""):
    s = PROMPT_STRINGS.get(LANGUAGE, PROMPT_STRINGS["en"])
    language_instruction = LANGUAGE_INSTRUCTIONS.get(LANGUAGE, LANGUAGE_INSTRUCTIONS["en"])

    touching_str = s["touching"].format(touching=touching) if touching else s["not_touching"]
    spatial_str = s["known_locations"].format(spatial=spatial) if spatial else s["no_locations"]
    reflections_str = s["reflections"].format(reflections=reflections) if reflections else s["no_reflections"]
    semantic_str = s["learned"].format(semantic=semantic) if semantic else s["not_learned"]

    return f"""{lore}
{language_instruction}
{s["state"].format(h=f"{hunger:.0f}", e=f"{energy:.0f}", c=f"{curiosity:.0f}")}
{s["nearby"].format(nearby=nearby_str)}
{touching_str}
{spatial_str}
{reflections_str}
{semantic_str}
{s["recent_thoughts"].format(history=history)}

{s["question"]}
{s["important"]}
{s["reply"]}
{{"thought": "...", "target": "<{s['target_hint']}>", "wait_time": <{"entero" if LANGUAGE == "es" else "integer"} entre {WAIT_TIME_MIN} y {WAIT_TIME_MAX}>}}"""