import faiss
import numpy as np
import pytest

from src import retrieve
from src.build_demo import select_ids, write_recipes


def recipe(i, image):
    return {"title": f"R{i}", "ingredients": ["chicken"], "NER": ["chicken", "rice"],
            "directions": ["Cook."], "image": image}


def test_only_recipes_with_a_photo_are_selected_reproducibly_and_in_order():
    recipes = [recipe(i, "u" if i % 2 else "") for i in range(20)]
    ids = select_ids(recipes, size=5, seed=1)
    assert len(ids) == 5 and ids == sorted(ids)
    assert all(recipes[i]["image"] for i in ids)
    assert ids == select_ids(recipes, size=5, seed=1)
    assert select_ids(recipes, size=100) == [i for i in range(20) if i % 2]


@pytest.fixture
def demo_only(tmp_path, monkeypatch):
    """Pas de data/, seulement un petit demo/ : c'est la situation du deploiement."""
    monkeypatch.setattr(retrieve, "INDEX_PATH", tmp_path / "missing.faiss")
    monkeypatch.setattr(retrieve, "RECIPES_PATH", tmp_path / "missing.json")
    monkeypatch.setattr(retrieve, "DEMO_INDEX", tmp_path / "recipes.faiss")
    monkeypatch.setattr(retrieve, "DEMO_RECIPES", tmp_path / "recipes.json.gz")
    monkeypatch.setattr(retrieve, "_load_model", lambda: None)
    recipes = [recipe(i, "u") for i in range(3)]
    index = faiss.IndexFlatL2(4)
    index.add(np.eye(3, 4, dtype="float32"))
    faiss.write_index(index, str(tmp_path / "recipes.faiss"))
    write_recipes(recipes, tmp_path / "recipes.json.gz")
    return recipes


def test_the_app_loads_the_demo_data_when_full_data_is_absent(demo_only):
    retriever = retrieve.RecipeRetriever()
    assert retriever.recipes == demo_only
    assert retriever.catalog.search(["chicken", "rice"])[0]["missing"] == []


def test_without_the_embedding_model_reranking_is_skipped(demo_only):
    retriever = retrieve.RecipeRetriever()
    found = retriever.catalog.search(["chicken", "rice"])
    assert not retriever.semantic_available
    assert retriever.semantic_rank("dessert", found) == found


def test_missing_data_everywhere_is_reported(tmp_path, monkeypatch):
    for name in ("INDEX_PATH", "RECIPES_PATH", "DEMO_INDEX", "DEMO_RECIPES"):
        monkeypatch.setattr(retrieve, name, tmp_path / name)
    with pytest.raises(FileNotFoundError):
        retrieve.data_paths()
