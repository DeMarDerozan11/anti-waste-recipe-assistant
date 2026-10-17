from src.ui_hero import TOKENS, headline_html, hero_html, scene_html, section_html

TEXT = {"eyebrow": "Anti-gaspi", "headline": "Votre frigo, [en repas].", "sub": "Sous-titre",
        "cta": "Commencer", "recipes": "recettes", "languages": "langues", "chef": "Harvey"}


def recipe(title):
    return {"title": title, "NER": [], "image": "https://x/a.jpg", "minutes": 45, "rating": 4.6}


def test_the_bracketed_part_of_the_headline_is_highlighted_and_the_rest_escaped():
    assert headline_html("A & B, [C].") == 'A &amp; B, <span class="accent">C</span>.'


def test_hero_shows_the_recipe_count_in_the_local_format():
    page = hero_html(TEXT, 149335, "<div class='scene'></div>", "fr")
    assert "149 335" in page and "lang-fr" in page and 'href="#pantry"' in page


def test_scene_shows_every_ingredient_token_and_escapes_recipe_titles():
    page = scene_html([recipe("<b>Pie</b>")], {"<b>Pie</b>": "<b>Tarte</b>"}, ("Frigo", "Recettes"), "fr")
    assert page.count('class="token"') == len(TOKENS)
    assert "&lt;b&gt;Tarte" in page and "<b>Tarte" not in page
    assert "45 min" in page and "4.6" in page


def test_section_heading_can_be_a_link_target():
    assert 'id="pantry"' in section_html(1, "Titre", "Aide", anchor="pantry")
    assert "id=" not in section_html(2, "Titre", "Aide")
