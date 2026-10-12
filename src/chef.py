"""Harvey, le chef virtuel : repond aux questions sur une recette precise."""
from src.generate import chat, format_recipe
from src.i18n import LLM_NAMES

MAX_TURNS = 8


def ask_chef(recipe: dict, history: list[dict], question: str, language: str = "fr") -> str:
    system = (
        "You are Harvey, a friendly chef in an anti-food-waste kitchen. "
        "Answer questions about THIS recipe only: "
        "substitutions, adapting to a diet or missing equipment, scaling servings, technique. "
        "Be concise and practical. If the recipe does not say, give a safe general guideline "
        f"and say so. Always reply in {LLM_NAMES[language]}.\n\n"
        + format_recipe(recipe)
    )
    messages = [{"role": "system", "content": system}, *history[-MAX_TURNS:]]
    messages.append({"role": "user", "content": question})
    return chat(messages)
