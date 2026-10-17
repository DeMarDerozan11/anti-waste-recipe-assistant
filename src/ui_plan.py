"""Planificateur : menu de plusieurs jours qui minimise les courses."""
import streamlit as st

from src.catalog import Filters
from src.diets import DIETS
from src.generate import LLMError
from src.matching import STAPLES
from src.optimizer import plan_meals
from src.ui_localize import localized
from src.ui_pantry import gather_wanted
from src.ui_search import COLUMNS, render_card
from src.ui_state import error_text, sticky_options, t


def kpis_html(plan: dict) -> str:
    shopping, naive = len(plan["shopping"]), plan["naive_items"]
    saved = ""
    if naive > shopping:
        saved = f'<div class="delta">{t("metric_saved", n=naive - shopping)}</div>'
    fridge = round(plan["fridge_used"] * 100)
    return (
        '<div class="kpis">'
        f'<div class="kpi"><div><b>{len(plan["menu"])}</b>'
        f'<div class="lbl">{t("metric_meals")}</div></div></div>'
        f'<div class="kpi" title="{t("metric_items_help")}"><div><b>{shopping}</b>'
        f'<div class="lbl">{t("metric_items")}</div>{saved}</div></div>'
        f'<div class="kpi"><div class="ring" style="--p:{fridge}"><span>{fridge}%</span></div>'
        f'<div class="lbl">{t("metric_fridge")}</div></div></div>'
    )


def render_menu(plan: dict, names: dict, wanted_count: int) -> None:
    st.markdown(f'<div class="results-head" id="menu"><span class="title">{t("menu_h")}</span></div>',
                unsafe_allow_html=True)
    menu = plan["menu"]
    for start in range(0, len(menu), COLUMNS):
        for offset, column in enumerate(st.columns(COLUMNS, gap="medium")):
            if start + offset < len(menu):
                entry = menu[start + offset]
                recipe = entry["recipe"]
                with column:
                    render_card(f"plan{entry['day']}", recipe, wanted_count, names[recipe["title"]],
                                label=t("day_label", day=entry["day"]), delay_ms=offset * 60)


def render_shopping(plan: dict, names: dict) -> None:
    with st.container(key="panel_shopping"):
        st.markdown(
            f'<div class="panel-head"><span class="panel-title">{t("shopping_h")}</span>'
            f'<span class="tag missing">{t("shop_count", n=len(plan["shopping"]))}</span></div>',
            unsafe_allow_html=True,
        )
        if not plan["shopping"]:
            st.success(t("shop_nothing"))
        for entry in plan["shopping"]:
            days = ", ".join(str(d) for d in entry["days"])
            st.checkbox(t("shop_item", item=names[entry["item"]], days=days), key=f"shop_{entry['item']}")


def render_plan(plan: dict, wanted_count: int) -> None:
    if not plan["menu"]:
        st.info(t("plan_none"))
        return
    texts = [e["recipe"]["title"] for e in plan["menu"]]
    texts += [s["item"] for s in plan["shopping"]] + plan["unused"]
    names = localized(texts)
    if st.session_state["translation_failed"]:
        st.caption(t("translation_unavailable"))
    st.markdown(kpis_html(plan), unsafe_allow_html=True)
    if plan["unused"]:
        st.caption(t("unused_caption", items=", ".join(names[u] for u in plan["unused"])))
    render_menu(plan, names, wanted_count)
    st.markdown("")
    render_shopping(plan, names)


def build_plan(retriever, days: int, basics: bool, diets: list) -> dict:
    staples = STAPLES if basics else frozenset()
    filters = Filters(diets=tuple(diets), with_photo=True)
    wanted = gather_wanted()
    plan = plan_meals(retriever.catalog, wanted, days, staples, filters)
    return {**plan, "wanted_count": len(wanted)}


def render_plan_tab(retriever) -> None:
    with st.container(key="panel_plan"):
        first, second = st.columns(2, gap="large")
        days = first.slider(t("plan_days"), 1, 7, 3)
        basics = first.checkbox(t("plan_basics"), value=True, key="p_basics")
        with second:
            sticky_options(st.multiselect, t("diet_label"), "plan_diets", list(DIETS),
                           lambda d: t(f"diet_{d}"), multi=True, placeholder=t("none_option"))
            clicked = st.button(t("plan_button"), type="primary", icon=":material/restaurant_menu:")
    if clicked:
        try:
            with st.spinner(t("planning")):
                st.session_state["plan"] = build_plan(
                    retriever, days, basics, st.session_state["plan_diets"])
        except (ValueError, LLMError) as err:
            st.error(error_text(err))
            return
    if st.session_state["plan"]:
        st.session_state["translation_failed"] = False
        render_plan(st.session_state["plan"], st.session_state["plan"]["wanted_count"])
