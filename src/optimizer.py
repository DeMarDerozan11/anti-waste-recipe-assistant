"""Planifie plusieurs repas en minimisant les achats."""
from collections import Counter

from src.catalog import Catalog, Filters

NEW_INGREDIENT = 2.0
REUSED_INGREDIENT = 0.5
PURCHASE = 1.0
SHARED_BONUS = 0.05
SHARED_CAP = 10
POOL = 400


def _gain(recipe: dict, to_buy: dict, used: set, popularity: Counter) -> float:
    """Un ingredient du frigo pas encore employe vaut 2, un achat deja prevu ne coute rien.

    Un article que d'autres recettes utilisent coute un peu moins : l'acheter servira encore.
    """
    new_use = len(set(recipe["have"]) - used)
    new_items = {m.lower() for m in recipe["missing"]} - set(to_buy)
    shared = sum(min(popularity[item], SHARED_CAP) for item in new_items)
    return (
        NEW_INGREDIENT * new_use
        + REUSED_INGREDIENT * len(recipe["have"])
        - PURCHASE * len(new_items)
        + SHARED_BONUS * shared
    )


def _count_items(recipes: list[dict]) -> int:
    return len({m.lower() for r in recipes for m in r["missing"]})


def plan_meals(
    catalog: Catalog,
    wanted: list[str],
    days: int,
    staples: frozenset = frozenset(),
    filters: Filters = Filters(),
) -> dict:
    """Glouton : a chaque jour, la recette qui utilise le plus du frigo pour le moins d'achats."""
    pool = catalog.search(wanted, staples=staples, filters=filters, limit=POOL, min_have=1)
    popularity = Counter(m.lower() for r in pool for m in r["missing"])
    menu, to_buy, used = [], {}, set()
    remaining = list(pool)
    for day in range(1, days + 1):
        if not remaining:
            break
        best = max(remaining, key=lambda r: _gain(r, to_buy, used, popularity))
        remaining.remove(best)
        used |= set(best["have"])
        for item in best["missing"]:
            to_buy.setdefault(item.lower(), {"item": item, "days": []})["days"].append(day)
        menu.append({"day": day, "recipe": best})
    valid = [w for w in wanted if w.strip()]
    return {
        "menu": menu,
        "shopping": sorted(to_buy.values(), key=lambda s: s["item"].lower()),
        "fridge_used": len(used) / len(valid) if valid else 0.0,
        "unused": [w for w in valid if w not in used],
        "naive_items": _count_items(pool[: len(menu)]),
    }
