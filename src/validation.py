"""Verification des saisies utilisateur, cote serveur (l'interface peut etre contournee)."""
from src.errors import ValidationError

MAX_OTHER_CHARS = 300
MAX_OTHER_ITEMS = 10
MAX_ITEM_CHARS = 60
MAX_CRAVING_CHARS = 200
MAX_CHAT_CHARS = 300


def split_ingredients(text: str) -> list[str]:
    return [i.strip() for i in text.replace("\n", ",").split(",") if i.strip()]


def validate_other(text: str) -> list[str]:
    """Aliments saisis a la main dans « Autre » : peut etre vide."""
    if len(text) > MAX_OTHER_CHARS:
        raise ValidationError("err_other_long", max=MAX_OTHER_CHARS)
    items = split_ingredients(text)
    if len(items) > MAX_OTHER_ITEMS:
        raise ValidationError("err_other_many", max=MAX_OTHER_ITEMS)
    if any(len(i) > MAX_ITEM_CHARS for i in items):
        raise ValidationError("err_item_long", max=MAX_ITEM_CHARS)
    return items


def validate_craving(text: str) -> str:
    text = text.strip()
    if len(text) > MAX_CRAVING_CHARS:
        raise ValidationError("err_craving_long", max=MAX_CRAVING_CHARS)
    return text


def validate_chat_message(text: str) -> str:
    text = text.strip()
    if not text:
        raise ValidationError("err_chat_empty")
    if len(text) > MAX_CHAT_CHARS:
        raise ValidationError("err_chat_long", max=MAX_CHAT_CHARS)
    return text
