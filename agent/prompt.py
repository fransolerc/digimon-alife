from config import WAIT_TIME_MIN, WAIT_TIME_MAX


REFLECTION_PROMPT = """You are {agent_name}, a curious Digimon inhabiting a digital forest.
These are your last 5 thoughts:
{thoughts}

Based on these thoughts, write a brief reflection (2-3 sentences) summarizing what you have learned or concluded.
Reply ONLY with the reflection text, no JSON, no extra formatting."""


def build_prompt(lore, hunger, energy, curiosity, nearby_str, history, touching="", spatial="", reflections=""):
    """
    Constructs the prompt for the LLM based on the agent's current state and memory.

    Args:
        lore (str): The Digimon's identity and rules.
        hunger (float): Current hunger level (0-100).
        energy (float): Current energy level (0-100).
        curiosity (float): Current curiosity level (0-100).
        nearby_str (str): String representation of nearby objects.
        history (str): Recent thoughts from memory.
        touching (str, optional): Name of the object currently being touched.
        spatial (str, optional): String representation of known locations.
        reflections (str, optional): String representation of recent reflections.

    Returns:
        str: The complete prompt string to be sent to the LLM.
    """
    touching_str = f"You are currently touching: {touching}." if touching else "You are not touching anything."
    spatial_str = f"Known locations:\n{spatial}" if spatial else "You have not mapped any locations yet."
    reflections_str = f"Your reflections:\n{reflections}" if reflections else "No reflections yet."

    return f"""{lore}
Current state: hunger {hunger:.0f}/100, energy {energy:.0f}/100, curiosity {curiosity:.0f}/100.
Nearby: {nearby_str}.
{touching_str}
{spatial_str}
{reflections_str}
Recent thoughts:
{history}

What are you thinking and where do you want to go?
IMPORTANT: The 'target' value must be copied EXACTLY as it appears in Nearby.
Reply ONLY with valid JSON, no extra text, no markdown:
{{"thought": "...", "target": "<object from Nearby or 'explore'>", "wait_time": <integer between {WAIT_TIME_MIN} and {WAIT_TIME_MAX}>}}"""