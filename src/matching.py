"""Compare les ingredients de l'utilisateur a ceux d'une recette."""
import re

# Noms exacts seulement : 'peanut butter' ou 'flour tortillas' ne sont pas des basiques.
STAPLES = frozenset({
    "salt", "pepper", "black pepper", "salt and pepper", "kosher salt", "sea salt", "water",
    "oil", "olive oil", "vegetable oil", "canola oil", "butter", "sugar", "white sugar",
    "flour", "all-purpose flour", "cooking spray",
})

_WORD = re.compile(r"[a-z]+")


def singular(word: str) -> str:
    """Singulier approximatif, utilise des deux cotes : seule la coherence compte."""
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"
    if word.endswith(("oes", "ches", "shes", "sses", "xes")):
        return word[:-2]
    if word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def tokens(text: str) -> frozenset[str]:
    return frozenset(singular(w) for w in _WORD.findall(text.lower()) if len(w) > 2)


def covers(wanted: frozenset[str], ingredient: frozenset[str]) -> bool:
    """'chicken' couvre 'chicken breasts', et 'chicken breast' couvre 'chicken'."""
    if not wanted or not ingredient:
        return False
    return wanted <= ingredient or ingredient <= wanted


def analyze(wanted: list[str], recipe: dict, staples: frozenset = frozenset()) -> dict:
    """`have` : ingredients de l'utilisateur utilises. `missing` : le reste de la recette."""
    names = recipe["NER"]
    name_tokens = [tokens(n) for n in names]
    wanted_tokens = [tokens(w) for w in wanted]
    have = [
        w for w, wt in zip(wanted, wanted_tokens)
        if any(covers(wt, nt) for nt in name_tokens)
    ]
    missing = []
    for name, nt in zip(names, name_tokens):
        if name in missing or name.lower() in staples:
            continue
        if not any(covers(wt, nt) for wt in wanted_tokens):
            missing.append(name)
    return {"have": have, "missing": missing}


def line_status(lines: list[str], have: list[str], missing: list[str]) -> list[str]:
    """Pour chaque ligne d'ingredient : 'have', 'missing' ou '' (basique, non reconnu).

    Le nom le plus precis l'emporte : '1 cup chicken broth' est 'chicken broth' (a acheter)
    plutot que 'chicken' (deja la).
    """
    names = [(tokens(n), "have") for n in have] + [(tokens(n), "missing") for n in missing]
    result = []
    for line in lines:
        words = tokens(line)
        found = [(len(nt), status) for nt, status in names if nt and nt <= words]
        result.append(max(found)[1] if found else "")
    return result
