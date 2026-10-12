"""Charge un dataset de recettes, le normalise et construit l'index FAISS."""
import argparse
import ast
import json
import re
from pathlib import Path

import pandas as pd

MODEL_NAME = "all-MiniLM-L6-v2"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
INDEX_PATH = DATA_DIR / "recipes.faiss"
RECIPES_PATH = DATA_DIR / "recipes.json"


_ISO_DURATION = re.compile(r"P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?)?")


def parse_minutes(value) -> int | None:
    """'PT1H30M' -> 90. Les durees nulles ou illisibles donnent None."""
    match = _ISO_DURATION.fullmatch(value) if isinstance(value, str) else None
    if not match:
        return None
    days, hours, minutes = (int(g or 0) for g in match.groups())
    total = days * 1440 + hours * 60 + minutes
    return total or None


def _number(value) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return None if number != number else number


def parse_list(value) -> list[str]:
    """Les CSV stockent les listes sous forme de texte : "['a', 'b']"."""
    if isinstance(value, list):
        return [str(v) for v in value]
    if not isinstance(value, str) or not value.strip():
        return []
    try:
        parsed = ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return [value]
    return [str(v) for v in parsed] if isinstance(parsed, (list, tuple)) else [value]


_NO_EXTRA = {"minutes": None, "calories": None, "protein": None, "servings": None, "rating": None}


def normalize_recipenlg(df: pd.DataFrame) -> list[dict]:
    return [
        {
            "title": str(row["title"]).strip(),
            "ingredients": parse_list(row["ingredients"]),
            "directions": parse_list(row["directions"]),
            "NER": parse_list(row["NER"]),
            "image": "",
            **_NO_EXTRA,
        }
        for _, row in df.iterrows()
    ]


R_STRING = re.compile(r'"((?:[^"\\]|\\.)*)"')


def parse_r_vector(value) -> list[str]:
    """Le dataset Food.com recent stocke les listes au format R : c("a", "b")."""
    if not isinstance(value, str):
        return []
    return [m.replace('\\"', '"') for m in R_STRING.findall(value)]


def _foodcom_ingredients(row) -> list[str]:
    parts = parse_r_vector(row["RecipeIngredientParts"])
    quantities = parse_r_vector(row.get("RecipeIngredientQuantities"))
    if len(quantities) != len(parts):
        return parts
    return [f"{q} {p}".strip() if q != "NA" else p for q, p in zip(quantities, parts)]


def _foodcom_image(row) -> str:
    value = row.get("Images")
    urls = parse_r_vector(value)
    if urls:
        return urls[0]
    return value if isinstance(value, str) and value.startswith("http") else ""


def _foodcom_extra(row) -> dict:
    return {
        "minutes": parse_minutes(row.get("TotalTime")),
        "calories": _number(row.get("Calories")),
        "protein": _number(row.get("ProteinContent")),
        "servings": _number(row.get("RecipeServings")),
        "rating": _number(row.get("AggregatedRating")),
    }


def normalize_foodcom(df: pd.DataFrame) -> list[dict]:
    """Gere les deux versions du dataset : RAW_recipes.csv et recipes.csv."""
    recent = "RecipeIngredientParts" in df.columns
    recipes = []
    for _, row in df.iterrows():
        extra = _foodcom_extra(row) if recent else _NO_EXTRA
        image = _foodcom_image(row) if recent else ""
        if recent:
            title = row["Name"]
            ingredients = _foodcom_ingredients(row)
            names = parse_r_vector(row["RecipeIngredientParts"])
            directions = parse_r_vector(row["RecipeInstructions"])
        else:
            title = row["name"]
            ingredients = names = parse_list(row["ingredients"])
            directions = parse_list(row["steps"])
        # Pas de champ NER dans Food.com : on reutilise les ingredients.
        recipes.append(
            {
                "title": str(title).strip().title(),
                "ingredients": ingredients,
                "directions": directions,
                "NER": names,
                "image": image,
                **extra,
            }
        )
    return recipes


NORMALIZERS = {"recipenlg": normalize_recipenlg, "foodcom": normalize_foodcom}

# Evite de charger les colonnes inutiles (le CSV recent fait plusieurs centaines de Mo).
KEEP_COLUMNS = {
    "recipenlg": {"title", "ingredients", "directions", "NER"},
    "foodcom": {
        "name", "ingredients", "steps",
        "Name", "RecipeIngredientParts", "RecipeIngredientQuantities",
        "RecipeInstructions", "Images", "TotalTime", "Calories", "ProteinContent",
        "RecipeServings", "AggregatedRating",
    },
}


def clean(recipes: list[dict]) -> list[dict]:
    return [r for r in recipes if r["title"] and r["NER"] and r["directions"]]


def embedding_text(recipe: dict) -> str:
    return f"{recipe['title']}. Ingredients: {', '.join(recipe['NER'])}"


def build_index(recipes: list[dict]):
    # Imports ici pour que les tests de normalisation n'exigent pas faiss.
    import faiss
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(MODEL_NAME)
    vectors = model.encode(
        [embedding_text(r) for r in recipes],
        batch_size=128,
        show_progress_bar=True,
        convert_to_numpy=True,
    ).astype("float32")
    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)
    return index


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="CSV du dataset")
    parser.add_argument("--format", choices=NORMALIZERS, default="recipenlg")
    parser.add_argument("--sample", type=int, default=30000)
    args = parser.parse_args()

    df = pd.read_csv(args.input, usecols=lambda c: c in KEEP_COLUMNS[args.format])
    if args.sample and len(df) > args.sample:
        df = df.sample(args.sample, random_state=42)
    recipes = clean(NORMALIZERS[args.format](df))
    with_photo = sum(1 for r in recipes if r["image"])
    print(f"{len(recipes)} recettes valides, dont {with_photo} avec une photo")

    index = build_index(recipes)
    import faiss

    DATA_DIR.mkdir(exist_ok=True)
    faiss.write_index(index, str(INDEX_PATH))
    RECIPES_PATH.write_text(json.dumps(recipes), encoding="utf-8")
    print(f"Index ecrit dans {INDEX_PATH}")


if __name__ == "__main__":
    main()
