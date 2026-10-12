import pandas as pd
import pytest

from src.ingest import (clean, normalize_foodcom, normalize_recipenlg, parse_list,
                        parse_minutes, parse_r_vector)


def test_parse_list_handles_stringified_lists():
    assert parse_list("['a', 'b']") == ["a", "b"]
    assert parse_list(None) == []


def test_recipenlg_and_foodcom_share_the_same_schema():
    nlg = pd.DataFrame([{"title": "Soup", "ingredients": "['1 cup milk']",
                         "directions": "['Boil']", "NER": "['milk']"}])
    fc = pd.DataFrame([{"name": "soup", "ingredients": "['milk']", "steps": "['boil']"}])
    a, b = normalize_recipenlg(nlg)[0], normalize_foodcom(fc)[0]
    assert set(a) == set(b) == {"title", "ingredients", "directions", "NER", "image", "minutes",
                                "calories", "protein", "servings", "rating"}
    assert b["NER"] == ["milk"]


def test_clean_drops_incomplete_recipes():
    assert clean([{"title": "", "NER": ["x"], "directions": ["y"]}]) == []


def test_parse_r_vector_handles_quotes_and_missing_values():
    assert parse_r_vector('c("a", "b c")') == ["a", "b c"]
    assert parse_r_vector('c("say \\"hi\\"")') == ['say "hi"']
    assert parse_r_vector("character(0)") == []
    assert parse_r_vector(float("nan")) == []


def test_foodcom_recent_format_is_normalized():
    df = pd.DataFrame([{
        "Name": "low-fat berry dessert",
        "RecipeIngredientParts": 'c("blueberries", "sugar")',
        "RecipeIngredientQuantities": 'c("4", "1/4")',
        "RecipeInstructions": 'c("Toss.", "Freeze.")',
        "Images": 'c("https://img/a.jpg", "https://img/b.jpg")',
        "TotalTime": "PT1H30M", "Calories": 420.5, "ProteinContent": 12.0,
        "RecipeServings": 4, "AggregatedRating": 4.5,
    }])
    recipe = normalize_foodcom(df)[0]
    assert recipe["title"] == "Low-Fat Berry Dessert"
    assert recipe["NER"] == ["blueberries", "sugar"]
    assert recipe["ingredients"] == ["4 blueberries", "1/4 sugar"]
    assert recipe["directions"] == ["Toss.", "Freeze."]
    assert recipe["image"] == "https://img/a.jpg"
    assert (recipe["minutes"], recipe["calories"], recipe["servings"]) == (90, 420.5, 4)
    assert recipe["rating"] == 4.5


def test_foodcom_recipe_without_image_gets_empty_string():
    df = pd.DataFrame([{
        "Name": "x", "RecipeIngredientParts": 'c("a")',
        "RecipeIngredientQuantities": 'c("1")', "RecipeInstructions": 'c("b")',
        "Images": "character(0)",
    }])
    assert normalize_foodcom(df)[0]["image"] == ""


def test_parse_minutes():
    assert parse_minutes("PT30M") == 30
    assert parse_minutes("PT1H30M") == 90
    assert parse_minutes("P1DT2H") == 1560
    assert parse_minutes("PT0S") is None
    assert parse_minutes(None) is None
    assert parse_minutes("n/a") is None
