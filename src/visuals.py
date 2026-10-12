"""Visuel d'une recette : photo si elle existe, sinon une illustration du type de plat."""
import html
import re
import zlib
from urllib.parse import quote

# Chaque pictogramme tient dans un carre de 100 x 100 ; INK est remplace par la couleur du fond.
_BOWL = "M16 48 H84 C84 66 70 80 50 80 C30 80 16 66 16 48 Z"
ICONS = {
    "soup": f'<path d="{_BOWL}" fill="INK" fill-opacity=".14"/><path d="M36 88 H64"/>'
            '<path d="M38 38 C33 32 43 28 38 21"/><path d="M50 38 C45 32 55 28 50 21"/>'
            '<path d="M62 38 C57 32 67 28 62 21"/>',
    "noodles": f'<path d="{_BOWL}" fill="INK" fill-opacity=".14"/><path d="M36 88 H64"/>'
               '<path d="M24 48 C28 36 34 56 40 42 C46 30 52 56 58 42 C63 32 68 52 76 40"/>'
               '<path d="M64 12 L48 44"/><path d="M74 14 L58 46"/>',
    "salad": f'<path d="{_BOWL}" fill="INK" fill-opacity=".14"/><path d="M36 88 H64"/>'
             '<path d="M26 48 C20 36 30 28 38 34 C40 24 54 22 58 32 C66 26 78 34 72 48"/>'
             '<circle cx="50" cy="40" r="6" fill="INK" fill-opacity=".3"/>',
    "cake": '<path d="M22 62 H78 V78 H22 Z" fill="INK" fill-opacity=".14"/>'
            '<path d="M22 62 C22 50 34 56 40 50 C46 56 54 50 60 56 C66 52 78 54 78 62"/>'
            '<circle cx="50" cy="40" r="5" fill="INK" fill-opacity=".3"/>'
            '<path d="M50 35 C50 30 54 28 57 28"/><path d="M14 84 H86"/>',
    "pie": '<path d="M14 58 H86 L78 80 H22 Z" fill="INK" fill-opacity=".14"/>'
           '<path d="M14 58 C18 40 82 40 86 58"/><path d="M34 46 L44 58"/><path d="M50 43 L56 58"/>'
           '<path d="M66 46 L62 58"/>',
    "cookie": '<circle cx="50" cy="50" r="30" fill="INK" fill-opacity=".14"/>'
              '<circle cx="40" cy="42" r="3" fill="INK"/><circle cx="58" cy="38" r="3" fill="INK"/>'
              '<circle cx="62" cy="58" r="3" fill="INK"/><circle cx="42" cy="62" r="3" fill="INK"/>'
              '<circle cx="51" cy="51" r="2.5" fill="INK"/>',
    "sandwich": '<path d="M18 46 C18 30 82 30 82 46 Z" fill="INK" fill-opacity=".14"/>'
                '<path d="M16 54 C24 62 32 50 40 58 S56 50 64 58 S76 52 84 56"/><path d="M18 64 H82"/>'
                '<path d="M18 70 H82 V74 C82 80 18 80 18 74 Z" fill="INK" fill-opacity=".14"/>',
    "bread": '<path d="M20 72 C12 60 16 42 32 36 C44 30 56 30 68 36 C84 42 88 60 80 72 Z" '
             'fill="INK" fill-opacity=".14"/><path d="M36 44 L42 60"/><path d="M50 40 L56 58"/>'
             '<path d="M64 44 L68 60"/>',
    "pizza": '<path d="M50 84 L16 32 C36 22 64 22 84 32 Z" fill="INK" fill-opacity=".14"/>'
             '<path d="M16 32 C36 22 64 22 84 32" stroke-width="6"/>'
             '<circle cx="44" cy="42" r="5" fill="INK" fill-opacity=".35"/>'
             '<circle cx="60" cy="46" r="5" fill="INK" fill-opacity=".35"/>'
             '<circle cx="51" cy="62" r="4.5" fill="INK" fill-opacity=".35"/>',
    "fish": '<path d="M14 50 C28 30 60 30 74 50 C60 70 28 70 14 50 Z" fill="INK" fill-opacity=".14"/>'
            '<path d="M74 50 L90 36 V64 Z" fill="INK" fill-opacity=".14"/>'
            '<circle cx="32" cy="46" r="2.8" fill="INK"/><path d="M46 40 C50 46 50 54 46 60"/>',
    "meat": '<path d="M14 54 C10 34 30 22 52 24 C74 26 90 42 82 62 C74 80 38 84 24 72 '
            'C18 66 15 60 14 54 Z" fill="INK" fill-opacity=".14"/>'
            '<path d="M32 44 L44 62"/><path d="M46 36 L60 58"/><path d="M60 34 L72 52"/>',
    "poultry": '<path d="M26 60 C14 44 26 24 46 26 C66 28 74 46 62 58 C54 66 46 70 38 70 '
               'C32 70 29 64 26 60 Z" fill="INK" fill-opacity=".14"/><path d="M58 62 L76 80"/>'
               '<circle cx="80" cy="76" r="4.5"/><circle cx="74" cy="84" r="4.5"/>',
    "egg": '<path d="M20 52 C16 34 38 22 56 28 C76 28 86 48 76 64 C66 78 38 80 28 68 '
           'C24 64 22 58 20 52 Z" fill="INK" fill-opacity=".1"/>'
           '<circle cx="52" cy="52" r="12" fill="INK" fill-opacity=".3"/>',
    "rice": '<path d="M16 50 H84 C84 68 70 82 50 82 C30 82 16 68 16 50 Z" fill="INK" '
            'fill-opacity=".14"/><path d="M24 50 C28 30 72 30 76 50"/>'
            '<path d="M38 40 l4 3 M50 36 l4 3 M60 42 l4 3 M46 46 l4 3"/><path d="M36 90 H64"/>',
    "veggie": '<circle cx="36" cy="42" r="13" fill="INK" fill-opacity=".14"/>'
              '<circle cx="52" cy="34" r="15" fill="INK" fill-opacity=".14"/>'
              '<circle cx="67" cy="43" r="12" fill="INK" fill-opacity=".14"/>'
              '<path d="M42 52 L44 78 H58 L60 54"/>',
    "pot": '<path d="M22 48 H78 V72 C78 80 72 82 66 82 H34 C28 82 22 80 22 72 Z" fill="INK" '
           'fill-opacity=".14"/><path d="M18 48 H82"/><path d="M22 56 H12"/><path d="M78 56 H88"/>'
           '<path d="M40 38 C36 32 44 28 40 21"/><path d="M60 38 C56 32 64 28 60 21"/>',
    "drink": '<path d="M30 28 H70 L64 82 H36 Z" fill="INK" fill-opacity=".14"/>'
             '<path d="M32 44 H68"/><path d="M58 28 L66 12"/>',
    "dish": '<path d="M16 70 C16 42 84 42 84 70 Z" fill="INK" fill-opacity=".14"/>'
            '<circle cx="50" cy="40" r="4"/><path d="M10 76 H90"/>',
}

# Premier mot qui correspond gagne : le type de plat (soupe, salade...) passe avant les
# feculents, et le titre avant les ingredients.
ICON_BY_WORD = [
    ("pizza", "pizza"), ("burger", "sandwich"), ("sandwich", "sandwich"), ("wrap", "sandwich"),
    ("panini", "sandwich"), ("taco", "sandwich"), ("soup", "soup"), ("broth", "soup"),
    ("chowder", "soup"), ("stew", "pot"), ("curry", "pot"), ("chili", "pot"),
    ("casserole", "pot"), ("salad", "salad"), ("cookie", "cookie"), ("biscuit", "cookie"),
    ("pie", "pie"), ("tart", "pie"), ("cake", "cake"), ("cupcake", "cake"), ("muffin", "cake"),
    ("brownie", "cake"), ("dessert", "cake"), ("pudding", "cake"), ("mousse", "cake"),
    ("spaghetti", "noodles"), ("pasta", "noodles"), ("macaroni", "noodles"),
    ("lasagna", "noodles"), ("noodle", "noodles"), ("ramen", "noodles"),
    ("bread", "bread"), ("toast", "bread"), ("bun", "bread"), ("pancake", "bread"),
    ("waffle", "bread"), ("omelet", "egg"), ("omelette", "egg"), ("frittata", "egg"),
    ("quiche", "egg"), ("egg", "egg"), ("smoothie", "drink"), ("juice", "drink"),
    ("cocktail", "drink"), ("tea", "drink"), ("coffee", "drink"), ("salmon", "fish"),
    ("fish", "fish"), ("tuna", "fish"), ("shrimp", "fish"), ("prawn", "fish"), ("crab", "fish"),
    ("seafood", "fish"), ("chicken", "poultry"), ("turkey", "poultry"), ("duck", "poultry"),
    ("steak", "meat"), ("beef", "meat"), ("pork", "meat"), ("lamb", "meat"), ("meatball", "meat"),
    ("ribs", "meat"), ("sausage", "meat"), ("bacon", "meat"), ("ham", "meat"),
    ("rice", "rice"), ("risotto", "rice"), ("pilaf", "rice"), ("potato", "veggie"),
    ("broccoli", "veggie"), ("carrot", "veggie"), ("vegetable", "veggie"),
    ("zucchini", "veggie"), ("cabbage", "veggie"), ("spinach", "veggie"),
]
DEFAULT_ICON = "dish"
# (debut du degrade, fin du degrade, couleur du trait)
PALETTES = [
    ("#FFE8D6", "#FFD0A8", "#9A4E1C"), ("#FDECC8", "#F9D58A", "#8A5A12"),
    ("#FFE0E0", "#FFC2B8", "#A23B2C"), ("#E8F3D8", "#CDE5A8", "#4E7A2A"),
    ("#FFEFD5", "#FFD9A0", "#9A5B14"), ("#F9E1EC", "#F3C4D9", "#9C3F6A"),
]
_PATTERNS = [(re.compile(rf"\b{word}s?\b"), icon) for word, icon in ICON_BY_WORD]


def _first_icon(text: str) -> str | None:
    text = text.lower()
    return next((icon for pattern, icon in _PATTERNS if pattern.search(text)), None)


def pick_icon(recipe: dict) -> str:
    """Le titre prime sur les ingredients : 'Chicken Pie' est une tourte, pas un poulet."""
    return (
        _first_icon(recipe["title"])
        or _first_icon(" ".join(recipe["NER"]))
        or DEFAULT_ICON
    )


def pick_palette(title: str) -> tuple[str, str, str]:
    return PALETTES[zlib.crc32(title.encode("utf-8")) % len(PALETTES)]


def icon_svg(name: str, ink: str, size: int) -> str:
    body = ICONS[name].replace("INK", ink)
    return (
        f'<svg viewBox="8 8 84 84" width="{size}" height="{size}" fill="none" stroke="{ink}" '
        f'stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round">{body}</svg>'
    )


HARVEY = (
    '<svg viewBox="0 0 100 100" width="{size}" height="{size}" stroke-linecap="round" '
    'stroke-linejoin="round">'
    '<path d="M24 100 C26 86 38 82 50 90 C62 82 74 86 76 100 Z" fill="#fff" stroke="#8A4A1E" stroke-width="2.4"/>'
    '<ellipse cx="50" cy="62" rx="21" ry="23" fill="#F2C8A2" stroke="#8A4A1E" stroke-width="2.4"/>'
    '<g stroke="#8A4A1E" stroke-width="2.4" fill="#fff">'
    '<circle cx="32" cy="32" r="12"/><circle cx="50" cy="25" r="14"/><circle cx="68" cy="32" r="12"/></g>'
    '<g fill="#fff"><circle cx="32" cy="32" r="10.6"/><circle cx="50" cy="25" r="12.6"/>'
    '<circle cx="68" cy="32" r="10.6"/><rect x="31" y="32" width="38" height="12"/></g>'
    '<path d="M29 44 H71 V52 C71 54 29 54 29 52 Z" fill="#fff" stroke="#8A4A1E" stroke-width="2.4"/>'
    '<g fill="#3B2A20"><circle cx="41" cy="63" r="2.6"/><circle cx="59" cy="63" r="2.6"/></g>'
    '<path d="M36 70 C42 64 48 68 50 71 C52 68 58 64 64 70 C60 77 54 73 50 73 C46 73 40 77 36 70 Z" '
    'fill="#5A3A28"/>'
    '<path d="M43 80 C47 84 53 84 57 80" fill="none" stroke="#8A4A1E" stroke-width="2.4"/>'
    '<g fill="#F08A7A" fill-opacity=".45"><circle cx="35" cy="73" r="4"/><circle cx="65" cy="73" r="4"/></g>'
    '</svg>'
)


def harvey_svg(size: int = 64) -> str:
    return HARVEY.format(size=size)


def _safe_css_url(url: str) -> str:
    """Encode guillemets, parentheses et espaces : l'URL ne peut pas sortir de url('...')."""
    return html.escape(quote(url, safe=":/?&=#%+,;@~-_.!*$"), quote=True)


def cover_html(recipe: dict, height: int = 170) -> str:
    """Photo en image de fond par-dessus l'illustration : si elle ne charge pas, l'illustration
    reste visible, sans icone d'image cassee (ce que ferait une balise <img>)."""
    start, end, ink = pick_palette(recipe["title"])
    url = recipe.get("image", "")
    photo = ""
    if url.startswith(("http://", "https://")):
        photo = (
            f'<div style="position:absolute;inset:0;background:url(\'{_safe_css_url(url)}\') '
            'center/cover no-repeat"></div>'
        )
    return (
        f'<div style="position:relative;height:{height}px;border-radius:12px;overflow:hidden;'
        f"background:linear-gradient(135deg,{start},{end});display:flex;align-items:center;"
        f'justify-content:center">{icon_svg(pick_icon(recipe), ink, int(height * 0.62))}{photo}</div>'
    )
