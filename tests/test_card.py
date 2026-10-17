from src.i18n import translate
from src.ui_search import card_html


def with_language(monkeypatch, lang):
    monkeypatch.setattr("src.ui_search.t", lambda key, **p: translate(key, lang, **p))


def test_card_escapes_the_title_and_formats_the_time(monkeypatch):
    with_language(monkeypatch, "fr")
    recipe = {"title": "x", "NER": [], "missing": [], "have": ["rice"], "minutes": 220, "calories": None}
    html = card_html(recipe, 2, "Mac & <b>Cheese</b>", "fr")
    assert "&lt;b&gt;" in html and "<b>Cheese" not in html
    assert "Prêt à cuisiner" in html
    assert "3 h 40" in html and "1/2 de vos ingrédients" in html


def test_card_shows_what_is_missing_and_the_share_already_at_home(monkeypatch):
    with_language(monkeypatch, "en")
    recipe = {"title": "X", "NER": [], "missing": ["a", "b"], "have": ["c", "d", "e"], "minutes": 20}
    html = card_html(recipe, 3, "X", "en")
    assert "2 to buy" in html and "20 min" in html
    assert "60% already at home" in html and "width:60%" in html


def test_a_day_label_moves_the_shopping_badge_to_the_right(monkeypatch):
    with_language(monkeypatch, "fr")
    recipe = {"title": "X", "NER": [], "missing": [], "have": ["a"]}
    html = card_html(recipe, 1, "X", "fr", label="Jour 2")
    assert '<span class="badge day">Jour 2</span>' in html
    assert 'class="badge ok right"' in html
