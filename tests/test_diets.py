import pytest

from src.diets import satisfied_diets, violates


def recipe(*names):
    return {"title": "x", "NER": list(names)}


@pytest.mark.parametrize("diet, names, expected", [
    ("vegetarian", ["chicken broth", "rice"], True),
    ("vegetarian", ["eggplant", "rice", "tofu"], False),
    ("vegetarian", ["anchovies", "pasta"], True),
    ("vegan", ["milk", "flour"], True),
    ("vegan", ["eggs"], True),
    ("vegan", ["eggplant", "coconut milk"], False),
    ("gluten_free", ["all-purpose flour"], True),
    ("gluten_free", ["rice flour", "rice noodles"], False),
    ("gluten_free", ["soy sauce", "rice"], True),
    ("dairy_free", ["butter"], True),
    ("dairy_free", ["peanut butter", "coconut milk"], False),
    ("pork_free", ["bacon bits"], True),
    ("pork_free", ["turkey bacon", "chicken"], False),
    ("nut_free", ["almonds"], True),
    ("nut_free", ["nutmeg", "coconut", "butternut squash"], False),
])
def test_diet_rules(diet, names, expected):
    assert violates(diet, recipe(*names)) is expected


def test_satisfied_diets_lists_all_compatible_diets():
    result = satisfied_diets(recipe("rice", "carrots"))
    assert set(result) == {"vegetarian", "vegan", "gluten_free", "dairy_free", "pork_free", "nut_free"}
    assert "vegetarian" not in satisfied_diets(recipe("beef"))
