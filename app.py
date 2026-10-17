"""Cook Factory : recettes realisables avec ce qu'on a, et menu qui minimise les courses."""
import zlib

import streamlit as st

from src.generate import set_call_guard
from src.i18n import LANGUAGES
from src.retrieve import RecipeRetriever
from src.ui_hero import (APP_NAME, FAVICON_PATH, brand_html, footer_html, hero_html, scene_html,
                         section_html)
from src.ui_localize import localized
from src.ui_pantry import render_pantry
from src.ui_plan import render_plan_tab
from src.ui_recipe import render_detail
from src.ui_search import render_search_tab
from src.ui_state import count_llm_call, init_state, language, sticky_options, t
from src.ui_style import inject_style

st.set_page_config(page_title=APP_NAME, page_icon=str(FAVICON_PATH), layout="wide")

SHOWCASE_SIZE = 3


@st.cache_resource
def load_retriever() -> RecipeRetriever:
    return RecipeRetriever()


@st.cache_data(show_spinner=False)
def showcase(_retriever) -> list[dict]:
    """Quelques recettes bien notees, avec photo et un titre court, pour la page d'accueil."""
    chosen = [
        r for r in _retriever.recipes
        if r.get("image") and (r.get("rating") or 0) >= 4.5 and len(r["title"]) <= 32
    ]
    chosen.sort(key=lambda r: zlib.crc32(r["title"].encode("utf-8")))
    return chosen[:SHOWCASE_SIZE]


def set_language() -> None:
    names = list(LANGUAGES.values())
    st.session_state["language"] = list(LANGUAGES)[names.index(st.session_state["language_widget"])]


def render_topbar() -> None:
    with st.container(key="topbar"):
        left, right = st.columns([3, 2], vertical_alignment="center")
        left.markdown(brand_html(t("tagline")), unsafe_allow_html=True)
        with right:
            st.radio(
                t("language"), list(LANGUAGES.values()), horizontal=True,
                index=list(LANGUAGES).index(language()), label_visibility="collapsed",
                key="language_widget", on_change=set_language,
            )


def render_hero(retriever) -> None:
    recipes = showcase(retriever)
    names = localized([r["title"] for r in recipes])
    scene = scene_html(recipes, names, (t("scene_in"), t("scene_out")), language())
    text = {
        "eyebrow": t("hero_eyebrow"), "headline": t("hero_headline"), "sub": t("hero_sub"),
        "cta": t("hero_cta"), "recipes": t("stat_recipes"), "languages": t("stat_languages"),
        "chef": t("stat_chef"),
    }
    st.markdown(hero_html(text, len(retriever.recipes), scene, language()), unsafe_allow_html=True)


def render_home(retriever) -> None:
    render_hero(retriever)
    render_pantry()
    st.markdown(section_html(2, t("section_find"), t("section_find_hint")), unsafe_allow_html=True)
    sticky_options(st.radio, t("section_find"), "view", ["search", "plan"],
                   lambda v: t(f"tab_{v}"), horizontal=True, label_visibility="collapsed")
    if st.session_state["view"] == "plan":
        render_plan_tab(retriever)
    else:
        render_search_tab(retriever)


init_state()
set_call_guard(count_llm_call)
inject_style()
render_topbar()

try:
    retriever = load_retriever()
except FileNotFoundError:
    st.error(t("err_index_missing"))
    st.stop()

if st.session_state["selected"] is not None:
    render_detail(st.session_state["selected"])
else:
    render_home(retriever)
st.markdown(footer_html(t("footer_by"), t("footer_data")), unsafe_allow_html=True)
