"""Traduction automatique des titres, des aliments et des recettes affiches a l'ecran."""
import streamlit as st

from src.generate import RECIPE_LINES, TITLES, LLMError, translate_batch
from src.localize import localize
from src.ui_state import language


@st.cache_data(show_spinner=False, max_entries=256)
def _batch(texts: tuple, lang: str, kind: str) -> list[str]:
    """Une exception n'est pas mise en cache : un echec ponctuel n'est pas fige."""
    return translate_batch(list(texts), lang, kind)


def localized(texts: list[str]) -> dict[str, str]:
    """Texte anglais -> texte dans la langue choisie ; l'anglais d'origine si la traduction echoue."""
    try:
        return localize(texts, language(), lambda xs, lang: _batch(tuple(xs), lang, TITLES))
    except LLMError:
        st.session_state["translation_failed"] = True
        return {text: text for text in texts}


def translated_lines(recipe: dict) -> tuple[list[str], list[str]] | None:
    """Ingredients et etapes traduits ligne a ligne (un seul appel), pour garder la mise en
    page de la fiche ; None si la langue est l'anglais ou si la traduction echoue."""
    if language() == "en":
        return None
    lines = (*recipe["ingredients"], *recipe["directions"])
    try:
        translated = _batch(lines, language(), RECIPE_LINES)
    except LLMError:
        st.session_state["translation_failed"] = True
        return None
    count = len(recipe["ingredients"])
    return translated[:count], translated[count:]
