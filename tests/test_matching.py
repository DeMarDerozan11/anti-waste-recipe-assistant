from src.matching import STAPLES, analyze, line_status, tokens

RECIPE = {
    "title": "Tomato Chicken Rice",
    "ingredients": ["2 chicken breasts", "1 cup rice", "3 tomatoes", "1 onion"],
    "NER": ["chicken breasts", "rice", "tomatoes", "onion"],
}


def test_plural_and_singular_forms_match():
    result = analyze(["tomato", "chicken"], RECIPE)
    assert result["have"] == ["tomato", "chicken"]
    assert result["missing"] == ["rice", "onion"]


def test_unused_ingredient_is_not_in_have():
    assert analyze(["pasta"], RECIPE)["have"] == []


def test_whole_words_only_so_rice_does_not_match_licorice():
    recipe = {"title": "x", "ingredients": [], "NER": ["licorice", "peach"]}
    assert analyze(["rice", "pea"], recipe)["have"] == []


def test_more_specific_wanted_term_still_covers_the_generic_ingredient():
    assert analyze(["chicken thigh"], {"title": "x", "ingredients": [], "NER": ["chicken"]})["have"] == ["chicken thigh"]


def test_staples_are_not_counted_as_missing():
    recipe = {"title": "x", "ingredients": [],
              "NER": ["chicken", "salt", "olive oil", "peanut butter"]}
    assert analyze(["chicken"], recipe)["missing"] == ["salt", "olive oil", "peanut butter"]
    assert analyze(["chicken"], recipe, STAPLES)["missing"] == ["peanut butter"]


def test_tokens_are_consistent_on_both_sides():
    assert tokens("Tomatoes") == tokens("tomato")
    assert tokens("berries") == tokens("berry")


def test_each_ingredient_line_is_marked_with_the_most_precise_name():
    lines = ["1 cup chicken broth", "2 boneless chicken breasts", "1 tsp salt", "3 large eggs"]
    assert line_status(lines, have=["chicken", "egg"], missing=["chicken broth"]) == [
        "missing", "have", "", "have"]


def test_lines_are_unmarked_when_nothing_matches():
    assert line_status(["a pinch of love"], have=["rice"], missing=[]) == [""]
