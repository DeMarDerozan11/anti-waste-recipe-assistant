"""Fiche d'une recette : grande photo, ingredients marques, etapes, et Harvey, le chef virtuel."""
import html
from pathlib import Path

import streamlit as st

from src.chef import ask_chef
from src.diets import satisfied_diets
from src.format import format_duration
from src.generate import LLMError
from src.matching import line_status
from src.ui_localize import localized, translated_lines
from src.ui_search import status_badge
from src.ui_state import error_text, language, scroll_to, t
from src.validation import validate_chat_message
from src.visuals import GLYPHS, cover_html, harvey_svg

HARVEY_AVATAR = str(Path(__file__).resolve().parent.parent / "assets" / "harvey.svg")
QUICK_QUESTIONS = ("chef_q1", "chef_q2", "chef_q3")
BANNER_HEIGHT = 420
PHOTO_HEIGHT = 330


def close_recipe() -> None:
    st.session_state["selected"] = None
    scroll_to("menu" if st.session_state["view"] == "plan" else "results")


def ask(question: str) -> None:
    st.session_state["chef_pending"] = question


def facts_html(recipe: dict, lang: str) -> str:
    facts = []
    if recipe.get("minutes"):
        facts.append(GLYPHS["clock"] + format_duration(recipe["minutes"], lang))
    if recipe.get("servings"):
        facts.append(GLYPHS["users"] + t("servings", n=f"{recipe['servings']:.0f}"))
    if recipe.get("calories"):
        facts.append(GLYPHS["flame"] + f"{recipe['calories']:.0f} kcal")
    if recipe.get("protein"):
        facts.append(GLYPHS["bolt"] + t("protein", n=f"{recipe['protein']:.0f}"))
    if recipe.get("rating"):
        facts.append(GLYPHS["star"] + t("rating", n=f"{recipe['rating']:.1f}"))
    return "".join(f'<span class="fact">{fact}</span>' for fact in facts)


def banner_html(recipe: dict, title: str, lang: str) -> str:
    """Les photos du jeu de donnees sont petites : nettes a droite, floutees en fond."""
    return (
        f'<div class="banner"><div class="banner-bg">{cover_html(recipe, BANNER_HEIGHT)}</div>'
        f'<div class="banner-inner"><div class="banner-text">{status_badge(recipe)}'
        f'<div class="banner-title">{html.escape(title)}</div>'
        f'<div class="facts">{facts_html(recipe, lang)}</div></div>'
        f'<div class="banner-photo">{cover_html(recipe, PHOTO_HEIGHT)}</div></div></div>'
    )


def ingredients_html(recipe: dict, lines: list[str]) -> str:
    """`lines` est la liste affichee (traduite ou non) ; le marquage se fait sur l'anglais."""
    statuses = line_status(recipe["ingredients"], recipe["have"], recipe["missing"])
    marks = {"have": GLYPHS["check"], "missing": GLYPHS["plus"], "": ""}
    rows = "".join(
        f'<div class="ing-row {status}"><span class="mark">{marks[status]}</span>'
        f"<span>{html.escape(line)}</span>"
        + (f'<span class="buy">{t("buy_tag")}</span>' if status == "missing" else "")
        + "</div>"
        for line, status in zip(lines, statuses)
    )
    legend = f'<span class="tag have">{GLYPHS["check"]}{t("count_have", n=len(recipe["have"]))}</span>'
    if recipe["missing"]:
        legend += f'<span class="tag missing">{GLYPHS["plus"]}{t("to_buy", n=len(recipe["missing"]))}</span>'
    ready = "" if recipe["missing"] else f'<div class="ready-note">{t("nothing_to_buy")}</div>'
    return (
        f'<div class="panel-head"><span class="panel-title">{t("ingredients_h")}</span>'
        f'<div class="legend">{legend}</div></div>{rows}{ready}{diets_html(recipe)}'
    )


def diets_html(recipe: dict) -> str:
    diets = [t(f"diet_{d}") for d in satisfied_diets(recipe)] or [t("none_detected")]
    chips = "".join(f'<span class="diet">{d}</span>' for d in diets)
    return (
        f'<div class="diet-row"><b>{t("diets_h")}</b></div><div class="diet-row">{chips}</div>'
        f'<div class="diet-note">{t("diets_note")}</div>'
    )


def steps_html(steps: list[str]) -> str:
    rows = "".join(
        f'<div class="step-row"><span class="step-num">{n}</span>'
        f'<div class="step-text">{html.escape(step)}</div></div>'
        for n, step in enumerate(steps, 1)
    )
    return f'<div class="panel-head"><span class="panel-title">{t("steps_h")}</span></div>{rows}'


def render_chef(recipe: dict) -> None:
    with st.container(key="panel_chef"):
        st.markdown(
            f'<div class="chef-head"><div class="chef-avatar">{harvey_svg(70)}</div><div>'
            f'<div class="chef-title">{t("chef_title")}</div><div class="chef-sub">{t("chef_sub")}</div>'
            "</div></div>",
            unsafe_allow_html=True,
        )
        history = st.session_state["chats"].setdefault(recipe["title"], [])
        messages = st.container()
        for column, key in zip(st.columns(len(QUICK_QUESTIONS)), QUICK_QUESTIONS):
            column.button(t(key), key=f"ask_{key}", on_click=ask, args=(t(key),))
        typed = st.chat_input(t("chef_input"), key="chef_input")
        question = typed or st.session_state["chef_pending"]
        st.session_state["chef_pending"] = ""
        if question:
            try:
                clean = validate_chat_message(question)
                with st.spinner(t("chef_thinking")):
                    reply = ask_chef(recipe, history, clean, language())
                history.extend([{"role": "user", "content": clean},
                                {"role": "assistant", "content": reply}])
            except (ValueError, LLMError) as err:
                st.error(error_text(err))
        with messages:
            with st.chat_message("assistant", avatar=HARVEY_AVATAR):
                st.markdown(t("chef_hello"))
            for message in history:
                avatar = HARVEY_AVATAR if message["role"] == "assistant" else None
                with st.chat_message(message["role"], avatar=avatar):
                    st.markdown(message["content"])


def render_detail(recipe: dict) -> None:
    st.session_state["translation_failed"] = False
    st.button(t("back"), icon=":material/arrow_back:", on_click=close_recipe, key="back_button")
    names = localized([recipe["title"]])
    st.markdown(banner_html(recipe, names[recipe["title"]], language()), unsafe_allow_html=True)
    with st.spinner(t("translating")):
        translated = translated_lines(recipe)
    if translated and st.toggle(t("show_original"), key="show_original"):
        translated = None
    ingredients, steps = translated or (recipe["ingredients"], recipe["directions"])
    if st.session_state["translation_failed"]:
        st.caption(t("translation_unavailable"))
    left, right = st.columns([5, 7], gap="large")
    with left, st.container(key="panel_ingredients"):
        st.markdown(ingredients_html(recipe, ingredients), unsafe_allow_html=True)
    with right, st.container(key="panel_steps"):
        st.markdown(steps_html(steps), unsafe_allow_html=True)
    render_chef(recipe)
