from src.i18n import translate
from src.ui_search import card_text


def with_language(monkeypatch, lang):
    monkeypatch.setattr("src.ui_search.t", lambda key, **p: translate(key, lang, **p))


def test_card_text_escapes_the_title_and_formats_the_time(monkeypatch):
    with_language(monkeypatch, "fr")
    recipe = {"title": "x", "missing": [], "have": ["rice"], "minutes": 220, "calories": None}
    html = card_text(recipe, 2, "Mac & <b>Cheese</b>", "fr")
    assert "&lt;b&gt;" in html and "<b>Cheese" not in html
    assert "Prêt à cuisiner" in html
    assert "1/2 de vos ingrédients · 3 h 40" in html


def test_card_text_counts_missing_ingredients_in_the_chosen_language(monkeypatch):
    with_language(monkeypatch, "en")
    html = card_text({"title": "X", "missing": ["a", "b"], "have": [], "minutes": 20}, 3, "X", "en")
    assert "2 to buy" in html and "20 min" in html
