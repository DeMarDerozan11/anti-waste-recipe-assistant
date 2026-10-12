import json

from src.catalog import Catalog, Filters
from src.evaluate import QUERIES_PATH, evaluate, report, run_query
from src.matching import tokens
from src.pantry import match_item


def r(title, ner, image="x"):
    return {"title": title, "ingredients": list(ner), "NER": list(ner), "directions": ["x"], "image": image}


CATALOG = Catalog([
    r("Chicken Rice", ["chicken", "rice"]),
    r("Chicken Rice Peppers", ["chicken", "rice", "bell pepper"]),
    r("Chicken Rice Peppers Corn Beans", ["chicken", "rice", "bell pepper", "corn", "bean"]),
])


def test_metrics_on_a_known_catalog():
    row = run_query(CATALOG, ["chicken", "rice"], frozenset(), Filters())
    assert row["resultats"] == 3 and row["pretes"] == 1 and row["a_2_pres"] == 2
    assert row["manque_moyen"] == (0 + 1 + 3) / 3
    assert row["couverture"] == 1.0


def test_summary_counts_queries_without_any_result():
    queries = [{"wanted": ["chicken", "rice"]}, {"wanted": ["dragonfruit", "yuzu"]}]
    summary = evaluate(CATALOG, queries, frozenset(), Filters())
    assert summary["requetes"] == 2 and summary["sans_resultat"] == 1
    assert summary["avec_une_recette_prete"] == 1


def test_report_is_a_markdown_table_with_three_variants():
    text = report(CATALOG, [{"name": "q", "wanted": ["chicken", "rice"]}])
    assert text.count("\n| Avec") + text.count("\n| Sans") == 3
    assert "Limites" in text


def test_every_benchmark_query_uses_items_from_the_pantry_list():
    queries = json.loads(QUERIES_PATH.read_text(encoding="utf-8"))
    assert len(queries) >= 30
    unknown = [(q["name"], w) for q in queries for w in q["wanted"]
               if match_item(w) is None or tokens(match_item(w)) != tokens(w)]
    assert unknown == []
