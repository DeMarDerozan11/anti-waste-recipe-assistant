import pytest

from src.localize import localize


def test_english_needs_no_translation():
    def fail(*_):
        raise AssertionError("no translation expected")
    assert localize(["Beef Stew"], "en", fail) == {"Beef Stew": "Beef Stew"}


def test_pantry_foods_are_translated_locally_and_the_rest_in_one_batch():
    calls = []

    def batch(texts, language):
        calls.append((list(texts), language))
        return [f"<{t}>" for t in texts]

    result = localize(["chicken", "Beef Stew", "tomatoes", "Beef Stew", "Apple Pie"], "fr", batch)

    assert result == {"chicken": "poulet", "tomatoes": "tomate",
                      "Beef Stew": "<Beef Stew>", "Apple Pie": "<Apple Pie>"}
    assert calls == [(["Beef Stew", "Apple Pie"], "fr")]


def test_no_batch_call_when_everything_is_local():
    assert localize(["chicken", "rice"], "es", lambda *_: pytest.fail("no call")) == {
        "chicken": "pollo", "rice": "arroz"}


def test_translation_failure_reaches_the_caller():
    def failing(*_):
        raise RuntimeError("down")
    with pytest.raises(RuntimeError):
        localize(["Beef Stew"], "fr", failing)
