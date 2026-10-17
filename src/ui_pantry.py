"""Liste d'aliments a cocher, rangee par categories, avec une section « Autre » en texte libre."""
import html
from functools import partial

import streamlit as st

from src.generate import LLMError, translate_to_english
from src.pantry import CATEGORIES, item_label, match_item
from src.ui_hero import section_html
from src.ui_localize import localized
from src.ui_state import error_text, language, pantry_key, sticky, t
from src.validation import split_ingredients, validate_other
from src.errors import ValidationError
from src.vision import detect_ingredients


def selected_items() -> list[str]:
    return [item for c in CATEGORIES for item in st.session_state[pantry_key(c.key)]]


def gather_wanted() -> list[str]:
    """Aliments coches + saisie « Autre » (traduite en anglais) ; au moins un aliment."""
    other = validate_other(st.session_state["other_text"])
    english_other = split_ingredients(translate_to_english(", ".join(other))) if other else []
    wanted = list(dict.fromkeys([*selected_items(), *english_other]))
    if not wanted:
        raise ValidationError("err_need_ingredient")
    return wanted


def _set(pref: str, value) -> None:
    """Change la valeur d'un widget « collant » : la preference et le widget lui-meme."""
    st.session_state[pref] = value
    st.session_state[f"w_{pref}"] = value


def clear_all() -> None:
    for category in CATEGORIES:
        _set(pantry_key(category.key), [])
    _set("other_text", "")


def detect_from_photo() -> None:
    upload = st.session_state.get("photo_upload")
    st.session_state["vision_error"] = st.session_state["vision_done"] = ""
    if upload is None:
        st.session_state["vision_error"] = t("photo_first")
        return
    try:
        names = detect_ingredients(upload.getvalue(), upload.type)
    except (ValueError, LLMError) as err:
        st.session_state["vision_error"] = error_text(err)
        return
    unknown = []
    for name in names:
        match = match_item(name)
        if match is None:
            unknown.append(name)
            continue
        for category in CATEGORIES:
            if any(item.en == match for item in category.items):
                pref = pantry_key(category.key)
                _set(pref, list(dict.fromkeys([*st.session_state[pref], match])))
    if unknown:
        text = ", ".join(filter(None, [st.session_state["other_text"], *unknown]))
        _set("other_text", text)
    st.session_state["vision_done"] = t("photo_done", n=len(names))


def render_photo_input() -> None:
    with st.expander(f":material/photo_camera: {t('photo_expander')}"):
        st.file_uploader(t("photo_label"), type=["jpg", "jpeg", "png", "webp"], key="photo_upload")
        st.button(t("photo_button"), on_click=detect_from_photo)
        if st.session_state["vision_error"]:
            st.error(st.session_state["vision_error"])
        if st.session_state["vision_done"]:
            st.success(st.session_state["vision_done"])


def render_summary() -> None:
    items = selected_items()
    if not items:
        st.markdown(f'<div class="chips empty">{t("nothing_selected")}</div>', unsafe_allow_html=True)
        return
    names = localized(items)
    chips = "".join(f'<span class="chip">{html.escape(names[i])}</span>' for i in items)
    left, right = st.columns([5, 1], vertical_alignment="center")
    left.markdown(
        f'<div class="chips"><span class="count">{t("selected_count", n=len(items))}</span>{chips}</div>',
        unsafe_allow_html=True,
    )
    right.button(t("clear_all"), on_click=clear_all, key="clear_all_button",
                 icon=":material/close:")


def render_pantry() -> None:
    lang = language()
    st.markdown(section_html(1, t("pantry_title"), t("pantry_hint"), anchor="pantry"),
                unsafe_allow_html=True)
    with st.container(key="panel_pantry"):
        tabs = st.tabs([c.labels[lang] for c in CATEGORIES] + [t("other_tab")])
        for tab, category in zip(tabs, CATEGORIES):
            with tab:
                pref = pantry_key(category.key)
                sticky(
                    st.pills, category.labels[lang], pref,
                    options=[item.en for item in category.items],
                    selection_mode="multi",
                    default=st.session_state[pref],
                    format_func=partial(item_label, language=lang),
                    label_visibility="collapsed",
                )
        with tabs[-1]:
            sticky(
                st.text_input, t("other_label"), "other_text",
                value=st.session_state["other_text"], placeholder=t("other_placeholder"),
            )
        render_summary()
        render_photo_input()
