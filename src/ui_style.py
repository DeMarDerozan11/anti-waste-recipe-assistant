"""Habillage de l'application : feuille de style et bandeau d'accueil."""
import streamlit as st

from src.visuals import icon_svg

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&display=swap');
.block-container { padding-top: 4.5rem; max-width: 1320px; }
h1, h2, h3, .hero-title, .card-title { font-family: 'Playfair Display', Georgia, serif !important; }
h2, h3 { letter-spacing: -0.01em; }
.hero { position: relative; overflow: hidden; border-radius: 22px; padding: 2.4rem 2.6rem;
  margin-bottom: 1.4rem; background: linear-gradient(120deg, #FFFFFF 0%, #FFF1E6 55%, #FFDFC4 100%);
  border: 1px solid #F5E1CF; }
.hero-title { font-size: 2.6rem; font-weight: 700; color: #2B2118; line-height: 1.1; }
.hero-sub { margin-top: .6rem; font-size: 1.1rem; color: #6B5444; max-width: 34rem; }
.hero-art { position: absolute; right: 2.4rem; top: 50%; transform: translateY(-50%); opacity: .55; }
.stTabs [data-baseweb="tab"] { font-weight: 600; padding: .6rem 1.1rem; }
.stButton button[kind="primary"] { border-radius: 999px; padding: .5rem 1.6rem; font-weight: 600; }
.stTextArea textarea, .stTextInput input { border-radius: 12px; }
[class*="st-key-card_"] { position: relative; background: #fff; border: 1px solid #F0E2D4;
  border-radius: 16px; padding: .7rem .7rem .9rem; box-shadow: 0 2px 10px rgba(80, 40, 10, .06);
  transition: transform .18s ease, box-shadow .18s ease; cursor: pointer; }
[class*="st-key-card_"]:hover { transform: translateY(-4px) scale(1.025); z-index: 2;
  box-shadow: 0 16px 32px rgba(80, 40, 10, .16); }
[class*="st-key-card_"] .stButton,
[class*="st-key-card_"] [class*="st-key-open_"] { position: static; }
[class*="st-key-card_"] button { position: absolute; inset: 0; width: 100%; height: 100%;
  opacity: 0; cursor: pointer; z-index: 3; border-radius: 16px; }
.card-title { font-size: 1.08rem; font-weight: 700; line-height: 1.25; margin: .55rem 0 .35rem;
  min-height: 2.7em; color: #2B2118; }
.card-sub { margin-top: .45rem; font-size: .85rem; color: #7A6657; }
.pill { display: inline-block; font-size: .78rem; font-weight: 600; padding: .15rem .6rem;
  border-radius: 999px; background: #F4EEE8; color: #6B5444; }
.pill.ok { background: #DFF3E3; color: #1E6B35; }
.chef-head { display: flex; align-items: center; gap: 1rem; margin: 2rem 0 .6rem; }
.chef-head .chef-title { font-family: 'Playfair Display', Georgia, serif; font-size: 1.6rem;
  font-weight: 700; color: #2B2118; }
.chef-head .chef-sub { color: #6B5444; font-size: .95rem; }
"""


def inject_style() -> None:
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


def hero_html(title: str, subtitle: str) -> str:
    art = icon_svg("soup", "#9A4E1C", 150)
    return (
        f'<div class="hero"><div class="hero-title">{title}</div>'
        f'<div class="hero-sub">{subtitle}</div><div class="hero-art">{art}</div></div>'
    )
