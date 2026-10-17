"""Marque, bandeau d'accueil anime, titres de section et pied de page (HTML pur)."""
import html
from pathlib import Path

from src.format import format_count, format_duration
from src.visuals import GLYPHS, cover_html, harvey_svg

APP_NAME = "Cook Factory"
LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "logo.svg"
FAVICON_PATH = LOGO_PATH.with_suffix(".png")
_LOGO = LOGO_PATH.read_text(encoding="utf-8")

# Ingredients qui avancent sur le tapis roulant (carre de 40 x 40, en couleurs).
TOKENS = [
    '<circle cx="20" cy="22" r="13" fill="#E8483B"/><ellipse cx="15" cy="18" rx="3.5" ry="2.2" '
    'fill="#fff" opacity=".35"/><path d="M13 11 C16 13 19 13 20 9 C21 13 24 13 27 11 C25 15 22 '
    '15 20 14 C18 15 15 15 13 11 Z" fill="#3E8E41"/>',
    '<path d="M27 13 C30 16 29 19 26 22 L13 33 C11 34.5 9.5 33 11 31 L22 16 C24 13 25 12 27 13 Z" '
    'fill="#F28C28"/><path d="M27 13 C27 8 30 6 33 6 C33 10 31 12 27 13 Z M27 13 C31 11 35 12 36 '
    '14 C33 16 30 15 27 13 Z" fill="#4CAF50"/><path d="M17 26 l3 2 M21 21 l3 2" stroke="#C96A12" '
    'stroke-width="1.6" stroke-linecap="round"/>',
    '<ellipse cx="20" cy="21" rx="10.5" ry="13.5" fill="#FFF4E2" stroke="#E2C29B" stroke-width="1.6"/>'
    '<ellipse cx="16" cy="15" rx="3" ry="4" fill="#fff"/>',
    '<path d="M7 27 L29 12 L33 27 Z" fill="#F7C548"/><path d="M7 27 H33 V32 H7 Z" fill="#E9AE2B"/>'
    '<circle cx="22" cy="21" r="2.4" fill="#E0A21F"/><circle cx="15" cy="24.5" r="1.7" fill="#E0A21F"/>',
    '<path d="M20 34 C9 29 8 15 20 6 C32 15 31 29 20 34 Z" fill="#52A55A"/><path d="M20 31 V12" '
    'stroke="#2F7A38" stroke-width="1.6" stroke-linecap="round"/>',
    '<path d="M6 20 C11 12 23 12 29 20 C23 28 11 28 6 20 Z" fill="#6FA8DC"/><path d="M29 20 L36 14 '
    'V26 Z" fill="#5B93C7"/><circle cx="12" cy="18.5" r="1.6" fill="#1F3B57"/>',
]

MACHINE = (
    '<svg viewBox="0 0 200 190" width="200" height="190">'
    '<defs><linearGradient id="cf-body" x1="0" y1="0" x2="0" y2="1">'
    '<stop offset="0" stop-color="#FF8A3D"/><stop offset="1" stop-color="#D9480F"/></linearGradient></defs>'
    '<rect x="128" y="10" width="22" height="54" rx="4" fill="#8C3A12"/>'
    '<rect x="123" y="6" width="32" height="9" rx="3" fill="#6E2C0C"/>'
    '<path d="M30 66 L58 40 V66 L86 40 V66 L114 40 V66 Z" fill="#C2410C"/>'
    '<rect x="16" y="62" width="168" height="17" rx="8.5" fill="#9A3412"/>'
    '<rect x="4" y="94" width="28" height="11" rx="5.5" fill="#9A3412"/>'
    '<rect x="168" y="94" width="28" height="11" rx="5.5" fill="#9A3412"/>'
    '<path d="M28 82 H172 V120 C172 152 148 174 116 174 H84 C52 174 28 152 28 120 Z" fill="url(#cf-body)"/>'
    '<path d="M40 92 H160" stroke="#fff" stroke-opacity=".25" stroke-width="4" stroke-linecap="round"/>'
    '<g fill="#9A3412" opacity=".55"><circle cx="40" cy="104" r="2.6"/><circle cx="160" cy="104" r="2.6"/>'
    '<circle cx="40" cy="150" r="2.6"/><circle cx="160" cy="150" r="2.6"/></g>'
    '<circle cx="124" cy="126" r="21" fill="#FFF8F0" stroke="#9A3412" stroke-width="4"/>'
    '<path d="M110 126 h4 M124 112 v4 M138 126 h-4" stroke="#9A3412" stroke-width="2.4" stroke-linecap="round"/>'
    '<g class="needle"><path d="M124 126 L124 110" stroke="#E8483B" stroke-width="3" stroke-linecap="round"/></g>'
    '<circle cx="124" cy="126" r="3.6" fill="#9A3412"/>'
    '<path d="M64 140 C63 126 74 118 90 119 C91 133 80 142 64 140 Z" fill="#fff" opacity=".9"/>'
    '<path d="M69 136 L83 125" stroke="#E8590C" stroke-width="2.2" stroke-linecap="round"/>'
    '</svg>'
)


def logo_svg(size: int) -> str:
    return _LOGO.replace('width="64" height="64"', f'width="{size}" height="{size}"', 1)


def brand_html(tagline: str) -> str:
    return (
        f'<div class="brand">{logo_svg(44)}<div><div class="brand-name">Cook <span>Factory</span>'
        f'</div><div class="brand-tag">{html.escape(tagline)}</div></div></div>'
    )


def headline_html(text: str) -> str:
    """Le passage entre crochets est mis en valeur : '... [transforme en repas].'"""
    return html.escape(text).replace("[", '<span class="accent">', 1).replace("]", "</span>", 1)


def _mini_card(recipe: dict, title: str, language: str, index: int) -> str:
    meta = []
    if recipe.get("minutes"):
        meta.append(f'{GLYPHS["clock"]}{format_duration(recipe["minutes"], language)}')
    if recipe.get("rating"):
        meta.append(f'{GLYPHS["star"]}{recipe["rating"]:.1f}')
    return (
        f'<div class="mini o{index}">{cover_html(recipe, 112)}<div class="mini-body">'
        f'<div class="mini-title">{html.escape(title)}</div>'
        f'<div class="mini-meta">{"".join(f"<span>{m}</span>" for m in meta)}</div></div></div>'
    )


def scene_html(showcase: list[dict], names: dict, labels: tuple[str, str], language: str) -> str:
    """Le tapis roulant amene les ingredients dans la marmite-usine, les recettes en sortent."""
    tokens = "".join(
        f'<div class="token" style="animation-delay:{-1.2 * i:.1f}s"><svg viewBox="0 0 40 40" '
        f'width="34" height="34">{svg}</svg></div>'
        for i, svg in enumerate(TOKENS)
    )
    cards = "".join(
        _mini_card(r, names.get(r["title"], r["title"]), language, i + 1)
        for i, r in enumerate(showcase)
    )
    steam = "".join(f'<span class="puff p{i}"></span>' for i in range(1, 4))
    return (
        '<div class="scene" aria-hidden="true"><div class="scene-glow"></div>'
        f'<div class="belt"><span></span></div>{tokens}'
        f'<div class="machine">{MACHINE}</div>{steam}<div class="floor"></div>'
        f'<div class="stack s1"></div><div class="stack s2"></div>{cards}'
        f'<div class="scene-label in">{html.escape(labels[0])} {GLYPHS["arrow"]}</div>'
        f'<div class="scene-label out">{GLYPHS["arrow"]} {html.escape(labels[1])}</div></div>'
    )


def hero_html(text: dict, recipe_count: int, scene: str, language: str) -> str:
    stats = (
        f'<div class="stat"><b>{format_count(recipe_count, language)}</b><span>{text["recipes"]}</span></div>'
        f'<div class="stat"><b>4</b><span>{text["languages"]}</span></div>'
        f'<div class="stat chef">{harvey_svg(40)}<span>{text["chef"]}</span></div>'
    )
    return (
        f'<section class="hero lang-{language}"><div class="hero-copy">'
        f'<div class="eyebrow">{GLYPHS["leaf"]}{html.escape(text["eyebrow"])}</div>'
        f'<div class="hero-title" role="heading" aria-level="1">{headline_html(text["headline"])}</div>'
        f'<p class="hero-sub">{html.escape(text["sub"])}</p>'
        f'<div class="hero-actions"><a class="cta" href="#pantry" target="_self">{text["cta"]}'
        f'{GLYPHS["arrow"]}</a></div><div class="stats">{stats}</div></div>{scene}</section>'
    )


def section_html(number: int, title: str, hint: str, anchor: str = "") -> str:
    anchor_attr = f' id="{anchor}"' if anchor else ""
    return (
        f'<div class="section-head"{anchor_attr}><span class="step">{number}</span><div>'
        f'<div class="section-title">{html.escape(title)}</div>'
        f'<div class="section-hint">{html.escape(hint)}</div></div></div>'
    )


def footer_html(by: str, data: str) -> str:
    return (
        f'<footer class="footer">{logo_svg(28)}<div><b>{APP_NAME}</b> · {html.escape(by)}'
        f'<div class="footer-data">{html.escape(data)}</div></div></footer>'
    )
