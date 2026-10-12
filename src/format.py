"""Affichage des durees et des informations d'une recette."""
from src.i18n import DEFAULT_LANGUAGE, translate


_UNITS = {
    "fr": ("j", "h", "min"),
    "en": ("d", "h", "min"),
    "es": ("d", "h", "min"),
    "ja": ("日", "時間", "分"),
}


def format_duration(minutes: float, language: str = DEFAULT_LANGUAGE) -> str:
    """220 -> '3 h 40', 45 -> '45 min', 1560 -> '1 j 2 h'."""
    total = int(minutes)
    days, rest = divmod(total, 1440)
    hours, mins = divmod(rest, 60)
    day_unit, hour_unit, min_unit = _UNITS[language]
    if days:
        parts = [(days, day_unit), (hours, hour_unit)]
    elif hours:
        parts = [(hours, hour_unit), (mins, min_unit if language == "ja" else "")]
    else:
        parts = [(mins, min_unit)]
    glue = "" if language == "ja" else " "
    return glue.join(f"{n}{glue}{unit}".strip() for n, unit in parts if n)


def recipe_facts(recipe: dict, detailed: bool = False, language: str = DEFAULT_LANGUAGE) -> list[str]:
    """Temps et calories pour une carte ; portions, proteines et note en plus sur la fiche."""
    facts = []
    if recipe.get("minutes"):
        facts.append(format_duration(recipe["minutes"], language))
    if detailed and recipe.get("servings"):
        facts.append(translate("servings", language, n=f"{recipe['servings']:.0f}"))
    if recipe.get("calories"):
        facts.append(f"{recipe['calories']:.0f} kcal")
    if detailed and recipe.get("protein"):
        facts.append(translate("protein", language, n=f"{recipe['protein']:.0f}"))
    if detailed and recipe.get("rating"):
        facts.append(translate("rating", language, n=f"{recipe['rating']:.1f}"))
    return facts
