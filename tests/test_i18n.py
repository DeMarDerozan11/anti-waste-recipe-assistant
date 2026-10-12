import string

import pytest

from src.errors import AppError, ValidationError
from src.i18n import LANGUAGES, _TEXTS, describe, translate


def placeholders(text: str) -> set[str]:
    return {name for _, name, _, _ in string.Formatter().parse(text) if name}


def test_every_language_has_exactly_the_same_keys():
    reference = set(_TEXTS["fr"])
    for language, texts in _TEXTS.items():
        assert set(texts) == reference, language


@pytest.mark.parametrize("key", sorted(_TEXTS["fr"]))
def test_every_translation_uses_the_same_placeholders(key):
    expected = placeholders(_TEXTS["fr"][key])
    for language, texts in _TEXTS.items():
        assert placeholders(texts[key]) == expected, (language, key)


def test_no_translation_is_empty_or_left_in_french_by_mistake():
    for language in ("en", "es", "ja"):
        same = [k for k, v in _TEXTS[language].items()
                if v == _TEXTS["fr"][k] and k not in {"other_placeholder", "ready"}]
        assert not [k for k in same if len(_TEXTS["fr"][k]) > 12], (language, same)
        assert all(v.strip() for v in _TEXTS[language].values())


def test_language_switch_lists_the_four_languages():
    assert list(LANGUAGES) == ["fr", "en", "es", "ja"]


def test_translate_formats_parameters_and_falls_back_to_french_for_unknown_language():
    assert translate("to_buy", "en", n=3) == "3 to buy"
    assert translate("to_buy", "xx", n=3) == "3 à acheter"


def test_describe_translates_app_errors_and_keeps_other_messages():
    assert describe(ValidationError("err_chat_long", max=300), "en") == (
        "Question too long (300 characters maximum).")
    assert describe(AppError("err_llm_rate"), "ja").startswith("Groq")
    assert describe(RuntimeError("boom"), "fr") == "boom"
