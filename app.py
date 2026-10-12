"""Assistant recettes anti-gaspi : recherche par faisabilite et planificateur de menu."""
import streamlit as st

from src.generate import set_call_guard
from src.i18n import LANGUAGES
from src.retrieve import RecipeRetriever
from src.ui_pantry import render_pantry
from src.ui_plan import render_plan_tab
from src.ui_recipe import render_detail
from src.ui_search import render_search_tab
from src.ui_state import count_llm_call, init_state, language, t
from src.ui_style import hero_html, inject_style

st.set_page_config(
    page_title="Assistant Recettes anti-gaspi", page_icon=":material/restaurant:", layout="wide"
)


@st.cache_resource
def load_retriever() -> RecipeRetriever:
    return RecipeRetriever()


def render_language_switch() -> None:
    codes = list(LANGUAGES)
    _, right = st.columns([5, 3])
    with right:
        st.radio(
            t("language"), list(LANGUAGES.values()), horizontal=True,
            index=codes.index(language()), label_visibility="collapsed",
            key="language_widget", on_change=set_language,
        )


def set_language() -> None:
    names = list(LANGUAGES.values())
    st.session_state["language"] = list(LANGUAGES)[names.index(st.session_state["language_widget"])]


init_state()
set_call_guard(count_llm_call)
inject_style()
render_language_switch()
st.markdown(hero_html(t("app_title"), t("hero_sub")), unsafe_allow_html=True)

try:
    retriever = load_retriever()
except FileNotFoundError:
    st.error(t("err_index_missing"))
    st.stop()

if st.session_state["selected"] is not None:
    render_detail(st.session_state["selected"])
else:
    render_pantry()
    tab_search, tab_plan = st.tabs([t("tab_search"), t("tab_plan")])
    with tab_search:
        render_search_tab(retriever)
    with tab_plan:
        render_plan_tab(retriever)
