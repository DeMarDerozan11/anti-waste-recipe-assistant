import pytest

from src.errors import ValidationError
from src.validation import (MAX_CHAT_CHARS, MAX_CRAVING_CHARS, MAX_OTHER_CHARS, MAX_OTHER_ITEMS,
                            validate_chat_message, validate_craving, validate_other)


def test_other_is_split_trimmed_and_may_be_empty():
    assert validate_other(" harissa, kimchi ,\nmiso") == ["harissa", "kimchi", "miso"]
    assert validate_other("") == []


def test_other_rejects_too_long_too_many_or_oversized_items():
    with pytest.raises(ValidationError) as long_text:
        validate_other("a" * (MAX_OTHER_CHARS + 1))
    assert long_text.value.key == "err_other_long"
    with pytest.raises(ValidationError) as many:
        validate_other(",".join(["x"] * (MAX_OTHER_ITEMS + 1)))
    assert many.value.key == "err_other_many"
    with pytest.raises(ValidationError) as big_item:
        validate_other("a" * 61)
    assert big_item.value.key == "err_item_long"


def test_validation_errors_are_also_value_errors():
    with pytest.raises(ValueError):
        validate_craving("x" * (MAX_CRAVING_CHARS + 1))


def test_craving_is_trimmed():
    assert validate_craving("  dessert ") == "dessert"


def test_chat_message_rules():
    assert validate_chat_message(" no oven? ") == "no oven?"
    with pytest.raises(ValidationError) as empty:
        validate_chat_message("   ")
    assert empty.value.key == "err_chat_empty"
    with pytest.raises(ValidationError) as long:
        validate_chat_message("x" * (MAX_CHAT_CHARS + 1))
    assert long.value.params == {"max": MAX_CHAT_CHARS}
