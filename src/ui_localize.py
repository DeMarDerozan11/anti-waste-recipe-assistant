"""Traduction automatique des titres et des aliments affiches a l'ecran."""
import json

import streamlit as st

from src.generate import LLMError, translate_batch, translate_recipe
from src.localize import localize
from src.ui_state import language


@st.cache_data(show_spinner=False, max_entries=256)
def _batch(texts: tuple, lang: str) -> list[str]:
    """Une exception n'est pas mise en cache : un echec ponctuel n'est pas fige."""
    return translate_batch(list(texts), lang)


def localized(texts: list[str]) -> dict[str, str]:
    """Texte anglais -> texte dans la langue choisie ; l'anglais d'origine si la traduction echoue."""
    try:
        return localize(texts, language(), lambda xs, lang: _batch(tuple(xs), lang))
    except LLMError:
        st.session_state["translation_failed"] = True
        return {text: text for text in texts}


@st.cache_data(show_spinner=False, max_entries=128)
def _recipe(recipe_id: str, recipe_json: str, lang: str) -> str:
    return translate_recipe(json.loads(recipe_json), lang)


def translated_recipe(recipe: dict) -> str | None:
    """Recette entiere traduite, ou None si la langue est l'anglais ou si la traduction echoue."""
    if language() == "en":
        return None
    payload = {k: recipe[k] for k in ("title", "ingredients", "directions")}
    try:
        return _recipe(recipe["title"], json.dumps(payload, ensure_ascii=False), language())
    except LLMError:
        st.session_state["translation_failed"] = True
        return None
