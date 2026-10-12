"""Fiche d'une recette : details traduits automatiquement et Harvey, le chef virtuel."""
from pathlib import Path

import streamlit as st

from src.chef import ask_chef
from src.diets import satisfied_diets
from src.format import recipe_facts
from src.generate import LLMError
from src.ui_localize import localized, translated_recipe
from src.ui_state import error_text, language, t
from src.validation import validate_chat_message
from src.visuals import cover_html, harvey_svg

HARVEY_AVATAR = str(Path(__file__).resolve().parent.parent / "assets" / "harvey.svg")


def close_recipe() -> None:
    st.session_state["selected"] = None


def render_recipe_body(recipe: dict) -> None:
    translated = translated_recipe(recipe) if language() != "en" else None
    if translated:
        st.toggle(t("show_original"), key="show_original")
    if translated and not st.session_state["show_original"]:
        st.markdown(translated)
        return
    st.subheader(t("ingredients_h"))
    st.markdown("\n".join(f"- {i}" for i in recipe["ingredients"]))
    st.subheader(t("steps_h"))
    st.markdown("\n".join(f"{n}. {s}" for n, s in enumerate(recipe["directions"], 1)))


def render_chef(recipe: dict) -> None:
    st.markdown(
        f'<div class="chef-head">{harvey_svg(72)}<div><div class="chef-title">{t("chef_title")}</div>'
        f'<div class="chef-sub">{t("chef_sub")}</div></div></div>',
        unsafe_allow_html=True,
    )
    history = st.session_state["chats"].setdefault(recipe["title"], [])
    messages = st.container()
    question = st.chat_input(t("chef_input"), key="chef_input")
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
        for message in history:
            avatar = HARVEY_AVATAR if message["role"] == "assistant" else None
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])


def render_detail(recipe: dict) -> None:
    st.session_state["translation_failed"] = False
    st.button(t("back"), icon=":material/arrow_back:", on_click=close_recipe)
    names = localized([recipe["title"], *recipe["have"], *recipe["missing"]])
    left, right = st.columns([1, 2], gap="large")
    with left:
        st.markdown(cover_html(recipe, 340), unsafe_allow_html=True)
    with right:
        st.header(names[recipe["title"]])
        facts = recipe_facts(recipe, detailed=True, language=language())
        if facts:
            st.caption(" · ".join(facts))
        if recipe["have"]:
            st.success(t("have_already", items=", ".join(names[i] for i in recipe["have"])))
        if recipe["missing"]:
            st.warning(t("to_add", items=", ".join(names[i] for i in recipe["missing"])))
        else:
            st.success(t("nothing_to_buy"))
        diets = ", ".join(t(f"diet_{d}") for d in satisfied_diets(recipe))
        st.caption(t("diets_caption", diets=diets or t("none_detected")))
        with st.spinner(t("translating")):
            render_recipe_body(recipe)
        if st.session_state["translation_failed"]:
            st.caption(t("translation_unavailable"))
    render_chef(recipe)
