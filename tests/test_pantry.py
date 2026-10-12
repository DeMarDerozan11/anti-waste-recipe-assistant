from src.i18n import LANGUAGES
from src.matching import tokens
from src.pantry import CATEGORIES, item_label, local_label, match_item


def test_every_item_has_a_label_in_every_language():
    for category in CATEGORIES:
        assert set(category.labels) == set(LANGUAGES)
        for item in category.items:
            assert set(item.labels) == set(LANGUAGES) and all(item.labels.values()), item.en


def test_no_duplicate_items_and_no_two_items_share_the_same_words():
    names = [item.en for c in CATEGORIES for item in c.items]
    assert len(names) == len(set(names))
    assert len({tokens(n) for n in names}) == len(names)


def test_labels_in_the_chosen_language():
    assert item_label("chicken breast", "fr") == "blanc de poulet"
    assert item_label("tofu", "ja") == "豆腐"
    assert item_label("not in the list", "fr") == "not in the list"


def test_local_label_understands_dataset_spellings():
    assert local_label("Chicken Breasts", "es") == "pechuga de pollo"
    assert local_label("tomatoes", "fr") == "tomate"
    assert local_label("dragonfruit", "fr") is None


def test_match_item_maps_free_names_to_the_closest_item():
    assert match_item("red onions") == "onion"
    assert match_item("chicken breast fillets") == "chicken breast"
    assert match_item("tomatoes") == "tomato"
    assert match_item("dragonfruit") is None
    assert match_item("") is None
