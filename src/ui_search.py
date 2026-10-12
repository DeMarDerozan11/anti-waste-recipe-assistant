"""Onglet Recherche : envie particuliere, filtres, cartes de resultats."""
import html

import streamlit as st

from src.catalog import Filters
from src.diets import DIETS
from src.format import recipe_facts
from src.generate import LLMError, translate_to_english
from src.matching import STAPLES
from src.ui_localize import localized
from src.ui_pantry import gather_wanted
from src.ui_state import error_text, language, sticky, sticky_options, t
from src.validation import validate_craving
from src.visuals import cover_html

SHOWN = 12
SEMANTIC_POOL = 60
COLUMNS = 4
LIGHT_KCAL = 400
# Les recettes sans photo sont masquees tant que les illustrations de repli ne sont pas validees.
REQUIRE_PHOTO = True
TIME_FILTERS = {"any": None, "30": 30, "60": 60}
SHOPPING_FILTERS = {"any": None, "max2": 2, "none": 0}


def _filters(diets: tuple, max_minutes, max_calories) -> Filters:
    return Filters(diets=diets, max_minutes=max_minutes, max_calories=max_calories,
                   with_photo=REQUIRE_PHOTO)


@st.cache_data(show_spinner=False, max_entries=64)
def cached_search(_retriever, wanted, basics, diets, max_minutes, max_calories, max_missing, precision):
    """Mis en cache : changer de fiche ou de page ne relance pas le calcul."""
    staples = STAPLES if basics else frozenset()
    found = _retriever.catalog.search(
        list(wanted),
        staples=staples,
        filters=_filters(diets, max_minutes, max_calories),
        max_missing=max_missing,
        limit=SEMANTIC_POOL if precision else SHOWN,
    )
    if precision:
        found = _retriever.semantic_rank(precision, found)
    return found[:SHOWN]


@st.cache_data(show_spinner=False, max_entries=64)
def cached_opportunities(_retriever, wanted, basics, diets, max_minutes, max_calories):
    staples = STAPLES if basics else frozenset()
    return _retriever.catalog.opportunities(
        list(wanted), staples=staples, filters=_filters(diets, max_minutes, max_calories)
    )


def open_recipe(recipe: dict) -> None:
    st.session_state["selected"] = recipe


def add_boost(item: str) -> None:
    st.session_state["boost"] = [*st.session_state["boost"], item]


def clear_boost() -> None:
    st.session_state["boost"] = []


def card_text(recipe: dict, wanted_count: int, title: str, lang: str) -> str:
    """Titre, etat des courses et details d'une carte (le titre vient du jeu de donnees : echappe)."""
    if recipe["missing"]:
        status = f'<span class="pill">{t("to_buy", n=len(recipe["missing"]))}</span>'
    else:
        status = f'<span class="pill ok">{t("ready")}</span>'
    details = [t("used_of", have=len(recipe["have"]), wanted=wanted_count),
               *recipe_facts(recipe, language=lang)]
    return (
        f'<div class="card-title">{html.escape(title)}</div><div>{status}</div>'
        f'<div class="card-sub">{" · ".join(details)}</div>'
    )


def render_card(index: int, recipe: dict, wanted_count: int, title: str) -> None:
    """Toute la carte est cliquable : le bouton, invisible, la recouvre (voir ui_style)."""
    with st.container(key=f"card_{index}"):
        st.markdown(cover_html(recipe), unsafe_allow_html=True)
        st.markdown(card_text(recipe, wanted_count, title, language()), unsafe_allow_html=True)
        st.button(t("open_recipe"), key=f"open_{index}", on_click=open_recipe, args=(recipe,))


def render_results(results: list[dict], wanted_count: int, names: dict) -> None:
    for start in range(0, len(results), COLUMNS):
        columns = st.columns(COLUMNS, gap="medium")
        for offset, column in enumerate(columns):
            index = start + offset
            if index < len(results):
                with column:
                    recipe = results[index]
                    render_card(index, recipe, wanted_count, names.get(recipe["title"], recipe["title"]))


def render_filters() -> None:
    first, second = st.columns(2)
    with first:
        sticky(st.checkbox, t("basics_label"), "pref_basics", value=st.session_state["pref_basics"])
        sticky_options(st.multiselect, t("diet_label"), "pref_diets", list(DIETS),
                       lambda d: t(f"diet_{d}"), multi=True, placeholder=t("none_option"))
    with second:
        sticky_options(st.radio, t("shopping_label"), "pref_shopping", list(SHOPPING_FILTERS),
                       lambda c: t(f"shop_{c}"), horizontal=True)
        sticky_options(st.radio, t("time_label"), "pref_time", list(TIME_FILTERS),
                       lambda c: t("time_any") if c == "any" else t(f"time_{c}"), horizontal=True)
        sticky(st.checkbox, t("light_label", kcal=LIGHT_KCAL), "pref_light",
               value=st.session_state["pref_light"])


def render_opportunities(info: dict) -> None:
    if info["cookable"]:
        st.success(t("cookable", n=info["cookable"]))
    purchases = info["purchases"]
    if purchases:
        texts = [p["item"] for p in purchases] + [e for p in purchases for e in p["examples"]]
        names = localized(texts)
        top = purchases[0]
        st.info(t("best_purchase", item=names[top["item"]], count=top["count"],
                  examples=", ".join(names[e] for e in top["examples"])))
        st.button(t("what_if", item=names[top["item"]]), on_click=add_boost, args=(top["item"],))
        others = [f"{names[p['item']]} ({p['count']})" for p in purchases[1:]]
        if others:
            st.caption(t("other_purchases", items=", ".join(others)))
    if st.session_state["boost"]:
        boost = localized(st.session_state["boost"])
        st.caption(t("simulated", items=", ".join(boost[b] for b in st.session_state["boost"])))
        st.button(t("cancel_simulated"), on_click=clear_boost)


def run_search(ingredients_wanted: list[str], craving: str) -> None:
    craving = validate_craving(craving)
    st.session_state.update(
        searched=True,
        wanted=ingredients_wanted,
        boost=[],
        precision_query=translate_to_english(craving) if craving else "",
        selected=None,
        last_precision=craving,
    )


def render_search_tab(retriever) -> None:
    craving = ""
    if retriever.semantic_available:
        craving = st.text_input(
            t("craving_label"),
            value=st.session_state["last_precision"],
            placeholder=t("craving_placeholder"),
            key="s_prec",
        )
    if st.button(t("search_button"), type="primary"):
        try:
            with st.spinner(t("searching")):
                run_search(gather_wanted(), craving)
        except (ValueError, LLMError) as err:
            st.error(error_text(err))
            return
    if st.session_state["searched"]:
        render_results_section(retriever)


def render_results_section(retriever) -> None:
    render_filters()
    state = st.session_state
    state["translation_failed"] = False
    wanted = tuple(state["wanted"] + state["boost"])
    diets = tuple(state["pref_diets"])
    max_minutes = TIME_FILTERS[state["pref_time"]]
    max_calories = LIGHT_KCAL if state["pref_light"] else None
    render_opportunities(
        cached_opportunities(retriever, wanted, state["pref_basics"], diets, max_minutes, max_calories)
    )
    results = cached_search(
        retriever, wanted, state["pref_basics"], diets, max_minutes, max_calories,
        SHOPPING_FILTERS[state["pref_shopping"]], state["precision_query"],
    )
    if not results:
        st.info(t("no_results"))
        return
    names = localized([r["title"] for r in results])
    if state["translation_failed"]:
        st.caption(t("translation_unavailable"))
    render_results(results, len(wanted), names)
