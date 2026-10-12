"""Onglet Planificateur : menu de plusieurs jours qui minimise les courses."""
import streamlit as st

from src.catalog import Filters
from src.diets import DIETS
from src.generate import LLMError
from src.matching import STAPLES
from src.optimizer import plan_meals
from src.ui_localize import localized
from src.ui_pantry import gather_wanted
from src.ui_state import error_text, sticky_options, t
from src.visuals import cover_html


def render_metrics(plan: dict, names: dict) -> None:
    shopping, naive = len(plan["shopping"]), plan["naive_items"]
    first, second, third = st.columns(3)
    first.metric(t("metric_meals"), len(plan["menu"]))
    second.metric(
        t("metric_items"), shopping, delta=shopping - naive, delta_color="inverse",
        help=t("metric_items_help"),
    )
    third.metric(t("metric_fridge"), f"{plan['fridge_used']:.0%}")
    if plan["unused"]:
        st.caption(t("unused_caption", items=", ".join(names[u] for u in plan["unused"])))


def render_menu(plan: dict, names: dict) -> None:
    for entry in plan["menu"]:
        recipe = entry["recipe"]
        with st.expander(t("day_title", day=entry["day"], title=names[recipe["title"]])):
            left, right = st.columns([1, 3])
            with left:
                st.markdown(cover_html(recipe, 120), unsafe_allow_html=True)
            with right:
                used = ", ".join(names[h] for h in recipe["have"]) or "-"
                st.write(t("you_use"), used)
                st.write(t("ingredients_colon"), "; ".join(recipe["ingredients"]))
                for n, step in enumerate(recipe["directions"], 1):
                    st.write(f"{n}. {step}")


def render_shopping(plan: dict, names: dict) -> None:
    st.subheader(t("shopping_h"))
    if not plan["shopping"]:
        st.success(t("shop_nothing"))
    for entry in plan["shopping"]:
        days = ", ".join(str(d) for d in entry["days"])
        st.checkbox(t("shop_item", item=names[entry["item"]], days=days), key=f"shop_{entry['item']}")


def render_plan(plan: dict) -> None:
    if not plan["menu"]:
        st.info(t("plan_none"))
        return
    texts = [e["recipe"]["title"] for e in plan["menu"]]
    texts += [s["item"] for s in plan["shopping"]] + plan["unused"]
    texts += [h for e in plan["menu"] for h in e["recipe"]["have"]]
    names = localized(texts)
    if st.session_state["translation_failed"]:
        st.caption(t("translation_unavailable"))
    render_metrics(plan, names)
    render_menu(plan, names)
    render_shopping(plan, names)


def build_plan(retriever, days: int, basics: bool, diets: list) -> dict:
    staples = STAPLES if basics else frozenset()
    filters = Filters(diets=tuple(diets), with_photo=True)
    return plan_meals(retriever.catalog, gather_wanted(), days, staples, filters)


def render_plan_tab(retriever) -> None:
    days = st.slider(t("plan_days"), 1, 7, 3)
    first, second = st.columns(2)
    basics = first.checkbox(t("plan_basics"), value=True, key="p_basics")
    with second:
        sticky_options(st.multiselect, t("diet_label"), "plan_diets", list(DIETS),
                       lambda d: t(f"diet_{d}"), multi=True, placeholder=t("none_option"))
    diets = st.session_state["plan_diets"]
    if st.button(t("plan_button"), type="primary"):
        try:
            with st.spinner(t("planning")):
                st.session_state["plan"] = build_plan(retriever, days, basics, diets)
        except (ValueError, LLMError) as err:
            st.error(error_text(err))
            return
    if st.session_state["plan"]:
        st.session_state["translation_failed"] = False
        render_plan(st.session_state["plan"])
