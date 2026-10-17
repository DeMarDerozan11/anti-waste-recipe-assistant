import pytest

from src.format import coverage, format_count, format_duration, recipe_facts


@pytest.mark.parametrize("minutes, expected", [
    (5, "5 min"), (45, "45 min"), (60, "1 h"), (90, "1 h 30"), (220, "3 h 40"),
    (1440, "1 j"), (1560, "1 j 2 h"), (2880 + 600, "2 j 10 h"),
])
def test_french_durations(minutes, expected):
    assert format_duration(minutes) == expected


def test_other_languages_use_their_own_units():
    assert format_duration(220, "en") == "3 h 40"
    assert format_duration(1560, "en") == "1 d 2 h"
    assert format_duration(220, "ja") == "3時間40分"
    assert format_duration(45, "ja") == "45分"


def test_card_facts_are_short_and_detail_facts_are_complete():
    recipe = {"minutes": 220, "calories": 350.4, "servings": 4, "protein": 12.2, "rating": 4.5}
    assert recipe_facts(recipe) == ["3 h 40", "350 kcal"]
    assert recipe_facts(recipe, detailed=True) == [
        "3 h 40", "4 portions", "350 kcal", "12 g de protéines", "note 4.5/5"]
    assert recipe_facts({}) == []


def test_detail_facts_follow_the_language():
    recipe = {"minutes": 90, "servings": 2, "protein": 5, "rating": 4.0}
    assert recipe_facts(recipe, detailed=True, language="en") == [
        "1 h 30", "2 servings", "5 g protein", "rated 4.0/5"]
    assert recipe_facts(recipe, detailed=True, language="ja")[0] == "1時間30分"


def test_counts_use_the_thousands_separator_of_each_language():
    assert format_count(149335, "fr") == "149 335"
    assert format_count(149335, "en") == "149,335"
    assert format_count(149335, "es") == "149.335"
    assert format_count(999, "ja") == "999"


def test_coverage_is_the_share_of_ingredients_already_at_home():
    assert coverage({"have": ["a", "b"], "missing": ["c"]}) == 67
    assert coverage({"have": ["a"], "missing": []}) == 100
    assert coverage({"have": [], "missing": []}) == 100
