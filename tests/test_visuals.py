import pytest

from src.visuals import (DEFAULT_ICON, ICONS, ICON_BY_WORD, cover_html, harvey_svg, icon_svg,
                         pick_icon, pick_palette)


def recipe(title, ner=(), image=""):
    return {"title": title, "NER": list(ner), "image": image}


def test_title_wins_over_ingredients():
    assert pick_icon(recipe("Apple Pie", ["apple"])) == "pie"
    assert pick_icon(recipe("Chicken Noodle Soup", ["chicken"])) == "soup"


def test_whole_words_only():
    assert pick_icon(recipe("Spiced Pipe Stuff")) == DEFAULT_ICON


def test_falls_back_on_ingredients_then_default():
    assert pick_icon(recipe("Sunday Dish", ["chicken breasts"])) == "poultry"
    assert pick_icon(recipe("Mystery", ["xyz"])) == DEFAULT_ICON


def test_every_icon_referenced_by_a_rule_exists_and_every_icon_is_used():
    assert {icon for _, icon in ICON_BY_WORD} <= set(ICONS)
    assert set(ICONS) - {icon for _, icon in ICON_BY_WORD} == {DEFAULT_ICON}


@pytest.mark.parametrize("name", list(ICONS))
def test_icons_are_well_formed_svg_in_the_requested_colour(name):
    svg = icon_svg(name, "#123456", 80)
    assert svg.startswith("<svg") and svg.endswith("</svg>")
    assert "INK" not in svg and "#123456" in svg


def test_palette_is_stable_for_a_title():
    assert pick_palette("Biryani") == pick_palette("Biryani")


def test_cover_without_photo_shows_the_illustration():
    html = cover_html(recipe("Beef Stew"))
    assert "<svg" in html and "url(" not in html


def test_photo_url_cannot_break_out_of_the_css_string():
    page = cover_html(recipe("A", image="https://x/a.jpg');background:red;('"))
    inside = page.split("url('")[1].split("')")[0]
    assert not {"'", "(", ")", " "} & set(inside)


def test_non_http_image_gives_no_photo_layer():
    assert "url(" not in cover_html(recipe("A", image="javascript:alert(1)"))
    assert "url('https://x/a.jpg')" in cover_html(recipe("A", image="https://x/a.jpg"))


def test_harvey_is_an_svg_of_the_requested_size():
    svg = harvey_svg(64)
    assert svg.startswith("<svg") and 'width="64"' in svg
