"""Construit un jeu de donnees compact (demo/) a partir de data/, publiable avec le code.

Seules les recettes avec photo sont gardees (lancer d'abord `python -m src.check_images`).
Les vecteurs sont recopies depuis l'index existant : pas besoin de recalculer les embeddings.
"""
import argparse
import gzip
import json
import random

from src.ingest import INDEX_PATH, RECIPES_PATH
from src.retrieve import DEMO_DIR, DEMO_INDEX, DEMO_RECIPES

DEFAULT_SIZE = 12000
# GitHub refuse les fichiers de plus de 100 Mo et avertit au-dela de 50 Mo.
WARN_BYTES = 50_000_000


def select_ids(recipes: list[dict], size: int, seed: int = 42) -> list[int]:
    """Indices de recettes avec photo, tires au hasard mais reproductibles, dans l'ordre."""
    with_photo = [i for i, recipe in enumerate(recipes) if recipe.get("image")]
    if len(with_photo) <= size:
        return with_photo
    return sorted(random.Random(seed).sample(with_photo, size))


def write_recipes(recipes: list[dict], path) -> None:
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        json.dump(recipes, handle, ensure_ascii=False)


def main() -> None:
    import faiss
    import numpy as np

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--size", type=int, default=DEFAULT_SIZE)
    args = parser.parse_args()

    recipes = json.loads(RECIPES_PATH.read_text(encoding="utf-8"))
    index = faiss.read_index(str(INDEX_PATH))
    ids = select_ids(recipes, args.size)
    vectors = np.vstack([index.reconstruct(i) for i in ids]).astype("float32")
    demo_index = faiss.IndexFlatL2(vectors.shape[1])
    demo_index.add(vectors)

    DEMO_DIR.mkdir(exist_ok=True)
    faiss.write_index(demo_index, str(DEMO_INDEX))
    write_recipes([recipes[i] for i in ids], DEMO_RECIPES)
    for path in (DEMO_INDEX, DEMO_RECIPES):
        size = path.stat().st_size
        warning = "  <- trop gros pour GitHub, baisser --size" if size > WARN_BYTES else ""
        print(f"{path.name} : {size / 1e6:.1f} Mo{warning}")
    print(f"{len(ids)} recettes avec photo dans {DEMO_DIR}")


if __name__ == "__main__":
    main()
