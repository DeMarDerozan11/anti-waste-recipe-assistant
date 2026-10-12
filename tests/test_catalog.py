from src.catalog import Catalog, Filters


def r(title, ner, **extra):
    return {"title": title, "ingredients": list(ner), "NER": list(ner), "directions": ["x"], **extra}


RECIPES = [
    r("Chicken Rice", ["chicken", "rice"], minutes=30, calories=500, rating=4.0, image="http://x/a.jpg"),
    r("Chicken Rice Peppers", ["chicken", "rice", "bell pepper"], minutes=60, calories=350),
    r("Chicken Curry Onion", ["chicken", "rice", "curry powder", "onion"], minutes=90),
    r("Plain Rice", ["rice"]),
    r("Beef Stew", ["beef", "potato", "carrot"]),
    r("Chicken Rice Peppers Corn", ["chicken", "rice", "bell pepper", "corn"]),
]
catalog = Catalog(RECIPES)


def titles(results):
    return [x["title"] for x in results]


def test_ready_to_cook_recipes_come_first_and_irrelevant_ones_are_absent():
    results = catalog.search(["chicken", "rice"])
    assert titles(results)[0] == "Chicken Rice"
    assert "Beef Stew" not in titles(results)
    assert results[0]["missing"] == []


def test_recipe_needing_one_more_ingredient_is_flagged():
    found = {x["title"]: x for x in catalog.search(["chicken", "rice"])}
    assert found["Chicken Rice Peppers"]["missing"] == ["bell pepper"]


def test_a_single_wanted_ingredient_finds_recipes_using_it():
    results = titles(catalog.search(["rice"]))
    assert "Plain Rice" in results and "Beef Stew" not in results


def test_max_missing_filter():
    results = catalog.search(["chicken", "rice"], max_missing=0)
    assert titles(results) == ["Chicken Rice"]


def test_time_and_calorie_filters_exclude_unknown_values():
    quick = catalog.search(["chicken", "rice"], filters=Filters(max_minutes=45))
    assert titles(quick) == ["Chicken Rice"]
    light = catalog.search(["chicken", "rice"], filters=Filters(max_calories=400))
    assert titles(light) == ["Chicken Rice Peppers"]


def test_diet_filter():
    veg = catalog.search(["potato", "carrot"], filters=Filters(diets=("vegetarian",)))
    assert veg == []


def test_best_purchase_counts_recipes_unlocked_by_a_single_item():
    result = catalog.opportunities(["chicken", "rice"])
    assert result["cookable"] == 1
    top = result["purchases"][0]
    assert top["item"] == "bell pepper" and top["count"] == 1
    assert top["examples"] == ["Chicken Rice Peppers"]


def test_nothing_wanted_gives_nothing():
    assert catalog.search([]) == []
    assert catalog.opportunities([])["purchases"] == []


def test_photo_filter_keeps_only_recipes_with_an_image():
    results = catalog.search(["chicken", "rice"], filters=Filters(with_photo=True))
    assert titles(results) == ["Chicken Rice"]


def test_photo_share_and_tie_break_in_favour_of_illustrated_recipes():
    assert catalog.photo_share == 1 / len(RECIPES)
    tied = Catalog([
        r("No photo", ["chicken", "rice"], rating=5.0),
        r("With photo", ["chicken", "rice"], rating=1.0, image="http://x/b.jpg"),
    ])
    assert titles(tied.search(["chicken", "rice"])) == ["With photo", "No photo"]
