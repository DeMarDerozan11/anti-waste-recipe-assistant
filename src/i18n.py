"""Textes de l'interface dans les langues proposees."""
from src.errors import AppError
from src.texts import en, es, fr, ja

DEFAULT_LANGUAGE = "fr"
LANGUAGES = {"fr": "Français", "en": "English", "es": "Español", "ja": "日本語"}
_TEXTS = {"fr": fr.TEXTS, "en": en.TEXTS, "es": es.TEXTS, "ja": ja.TEXTS}
# Nom de la langue tel que le LLM le comprend le mieux.
LLM_NAMES = {"fr": "French", "en": "English", "es": "Spanish", "ja": "Japanese"}


def translate(key: str, language: str, **params) -> str:
    text = _TEXTS.get(language, fr.TEXTS).get(key) or fr.TEXTS[key]
    return text.format(**params)


def describe(error: Exception, language: str) -> str:
    """Message affichable d'une erreur : traduit pour les erreurs de l'application."""
    if isinstance(error, AppError):
        return translate(error.key, language, **error.params)
    return str(error)
