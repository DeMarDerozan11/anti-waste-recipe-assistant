"""Acces aux donnees : catalogue de recettes et index vectoriel FAISS.

Les donnees completes (data/) sont prioritaires ; sinon on charge le jeu de demonstration
compact (demo/), publie avec le code pour le deploiement.
"""
import gzip
import json
from pathlib import Path

import faiss
import numpy as np

from src.catalog import Catalog
from src.ingest import INDEX_PATH, MODEL_NAME, RECIPES_PATH

DEMO_DIR = Path(__file__).resolve().parent.parent / "demo"
DEMO_INDEX = DEMO_DIR / "recipes.faiss"
DEMO_RECIPES = DEMO_DIR / "recipes.json.gz"


def data_paths() -> tuple[Path, Path]:
    if INDEX_PATH.exists() and RECIPES_PATH.exists():
        return INDEX_PATH, RECIPES_PATH
    if DEMO_INDEX.exists() and DEMO_RECIPES.exists():
        return DEMO_INDEX, DEMO_RECIPES
    raise FileNotFoundError("index")


def load_recipes(path: Path) -> list[dict]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def _load_model():
    """Le modele d'embeddings (torch) est optionnel : sans lui, pas de reclassement par envie."""
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        return None
    return SentenceTransformer(MODEL_NAME)


class RecipeRetriever:
    def __init__(self) -> None:
        index_path, recipes_path = data_paths()
        self.index = faiss.read_index(str(index_path))
        self.recipes = load_recipes(recipes_path)
        self.catalog = Catalog(self.recipes)
        self.model = _load_model()

    @property
    def semantic_available(self) -> bool:
        return self.model is not None

    def semantic_rank(self, query: str, recipes: list[dict]) -> list[dict]:
        """Reordonne des recettes (deja realisables) selon leur proximite avec `query`."""
        if not recipes or self.model is None:
            return recipes
        vectors = np.vstack([self.index.reconstruct(r["id"]) for r in recipes])
        target = self.model.encode([query]).astype("float32")
        distances = ((vectors - target) ** 2).sum(axis=1)
        return [recipes[i] for i in np.argsort(distances)]
