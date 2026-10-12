from src.catalog import Catalog
from src.optimizer import plan_meals


def r(title, ner):
    return {"title": title, "ingredients": list(ner), "NER": list(ner), "directions": ["x"]}


def test_optimizer_buys_fewer_items_than_picking_recipes_one_by_one():
    recipes = [
        r("Q1 chicken", ["chicken", "q1"]), r("Q2 rice", ["rice", "q2"]),
        r("P1 chicken pepper", ["chicken", "bell pepper"]),
        r("P2 rice pepper", ["rice", "bell pepper"]),
    ]
    plan = plan_meals(Catalog(recipes), ["chicken", "rice"], days=2)
    assert [s["item"] for s in plan["shopping"]] == ["bell pepper"]
    assert plan["naive_items"] == 2
    assert plan["fridge_used"] == 1.0


def test_shopping_list_records_the_days_that_need_each_item():
    recipes = [r("P1 chicken pepper", ["chicken", "bell pepper"]),
               r("P2 rice pepper", ["rice", "bell pepper"])]
    plan = plan_meals(Catalog(recipes), ["chicken", "rice"], days=2)
    assert plan["shopping"] == [{"item": "bell pepper", "days": [1, 2]}]


def test_plan_never_repeats_a_recipe_and_reports_unused_ingredients():
    recipes = [r("Only chicken dish", ["chicken"])]
    plan = plan_meals(Catalog(recipes), ["chicken", "tofu"], days=3)
    assert len(plan["menu"]) == 1
    assert plan["unused"] == ["tofu"]
    assert plan["fridge_used"] == 0.5


def test_no_matching_recipe_gives_an_empty_plan():
    plan = plan_meals(Catalog([r("Beef", ["beef"])]), ["tofu"], days=3)
    assert plan["menu"] == [] and plan["shopping"] == []
