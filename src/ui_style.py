"""Feuille de style de Cook Factory, injectee une fois par page."""
import streamlit as st

_BASE = """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
:root {
  --ink: #221A15; --ink-2: #4A3B32; --muted: #7A6A5F; --cream: #FFF8F0; --card: #FFFFFF;
  --line: #EFE2D3; --line-2: #E4D2BF; --brand: #E8590C; --brand-2: #FF8A3D;
  --brand-deep: #B9420A; --brand-soft: #FFE8D8; --green: #2B8A3E; --green-soft: #E3F4E6;
  --amber: #A86200; --amber-soft: #FFF1D6;
  --display: 'Fraunces', 'Hiragino Mincho ProN', 'Yu Mincho', 'Noto Serif JP', Georgia, serif;
  --shadow-sm: 0 1px 2px rgba(70, 35, 10, .06), 0 2px 10px rgba(70, 35, 10, .05);
  --shadow-md: 0 2px 4px rgba(70, 35, 10, .05), 0 14px 34px rgba(70, 35, 10, .10);
  --shadow-lg: 0 6px 14px rgba(70, 35, 10, .08), 0 28px 60px rgba(70, 35, 10, .20);
}
.stApp {
  background: radial-gradient(1100px 600px at 92% -8%, #FFE2CB 0%, rgba(255, 226, 203, 0) 60%),
    radial-gradient(900px 520px at -12% 18%, #FFF0E1 0%, rgba(255, 240, 225, 0) 60%), var(--cream);
}
.stApp, .stApp p, .stApp li, .stApp label, .stApp input, .stApp textarea, .stApp button,
.stApp [data-testid="stMarkdownContainer"], .stApp [data-testid="stCaptionContainer"] {
  font-family: 'Plus Jakarta Sans', 'Hiragino Sans', 'Noto Sans JP', sans-serif; }
header[data-testid="stHeader"] { display: none; }
.block-container { padding: .8rem 2rem 2rem; max-width: 1280px; }
.glyph { flex: none; vertical-align: -0.14em; }
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition: none !important; }
  .mini { opacity: 1; }
}
"""

_TOPBAR = """
/* Le conteneur de la barre a sa propre enveloppe, aussi haute que lui : c'est elle qui colle. */
[data-testid="stLayoutWrapper"]:has(> .st-key-topbar) { position: sticky; top: .6rem; z-index: 99; }
.st-key-topbar { padding: .5rem .6rem .5rem .9rem;
  background: rgba(255, 253, 249, .82); backdrop-filter: saturate(1.5) blur(14px);
  -webkit-backdrop-filter: saturate(1.5) blur(14px); border: 1px solid var(--line);
  border-radius: 20px; box-shadow: var(--shadow-sm); }
.brand { display: flex; align-items: center; gap: .75rem; }
.brand svg { filter: drop-shadow(0 6px 10px rgba(232, 89, 12, .3)); }
.brand-name { font-family: var(--display); font-weight: 800; font-size: 1.5rem; line-height: 1;
  letter-spacing: -.02em; color: var(--ink); font-variation-settings: "SOFT" 100, "opsz" 72; }
.brand-name span { color: var(--brand); }
.brand-tag { font-size: .78rem; color: var(--muted); margin-top: .22rem; font-weight: 500; }
.st-key-language_widget [role="radiogroup"] { justify-content: flex-end; gap: .25rem; flex-wrap: wrap; }
.st-key-language_widget label { margin: 0 !important; padding: .3rem .75rem; border-radius: 999px;
  cursor: pointer; transition: background .2s, color .2s; }
.st-key-language_widget label:hover { background: var(--brand-soft); }
.st-key-language_widget [data-testid="stRadioOption"] > div > div:not([data-testid]) { display: none; }
.st-key-language_widget label p { font-weight: 600; font-size: .85rem; color: var(--ink-2); }
.st-key-language_widget label:has(input:checked) { background: var(--ink); }
.st-key-language_widget label:has(input:checked) p { color: #fff; }
"""

_HERO = """
.hero { position: relative; display: grid; grid-template-columns: minmax(0, 1fr) 600px;
  align-items: center; gap: 1rem; margin: 1.4rem 0 1rem; padding: 3rem 2rem 3rem 3.2rem;
  border-radius: 32px; overflow: hidden; isolation: isolate; border: 1px solid var(--line);
  background: radial-gradient(640px 420px at 80% 62%, #FFD6B6 0%, rgba(255, 214, 182, 0) 70%),
    linear-gradient(135deg, #FFFDF9 0%, #FFF1E4 100%); box-shadow: var(--shadow-md); }
.hero::before { content: ""; position: absolute; inset: 0; z-index: -1;
  background-image: radial-gradient(rgba(154, 52, 18, .13) 1px, transparent 1.3px);
  background-size: 22px 22px; -webkit-mask-image: linear-gradient(90deg, transparent 10%, #000 70%);
  mask-image: linear-gradient(90deg, transparent 10%, #000 70%); }
.eyebrow { display: inline-flex; align-items: center; gap: .45rem; padding: .38rem .85rem;
  border-radius: 999px; background: #fff; border: 1px solid var(--line); color: var(--green);
  font-weight: 700; font-size: .82rem; box-shadow: var(--shadow-sm); animation: rise .6s both; }
.hero .hero-title { font-family: var(--display) !important; font-weight: 750 !important;
  font-size: clamp(2.4rem, 4.2vw, 4rem) !important; line-height: 1.03 !important;
  letter-spacing: -.025em; color: var(--ink) !important; margin: 1.1rem 0 1.1rem !important;
  padding: 0 !important; font-variation-settings: "SOFT" 100, "opsz" 144; animation: rise .7s .08s both; }
.accent { color: var(--brand); -webkit-box-decoration-break: clone; box-decoration-break: clone;
  background: linear-gradient(transparent 64%, #FFD3B5 64%, #FFD3B5 92%, transparent 92%) no-repeat;
  animation: marker 1.2s .5s cubic-bezier(.2, .8, .2, 1) both; }
.hero-sub { font-size: 1.1rem; line-height: 1.65; color: var(--ink-2); max-width: 35rem;
  margin: 0 0 1.7rem; animation: rise .7s .16s both; }
.hero-actions { animation: rise .7s .24s both; }
.cta { display: inline-flex; align-items: center; gap: .6rem; padding: .9rem 1.6rem;
  border-radius: 999px; color: #fff !important; text-decoration: none !important; font-weight: 700;
  background: linear-gradient(135deg, var(--brand-2), var(--brand));
  box-shadow: 0 12px 26px rgba(232, 89, 12, .35); transition: transform .2s, box-shadow .2s; }
.cta:hover { transform: translateY(-2px); box-shadow: 0 16px 32px rgba(232, 89, 12, .45); }
.cta .glyph { transition: transform .2s; }
.cta:hover .glyph { transform: translateX(4px); }
.stats { display: flex; align-items: center; gap: 2.2rem; margin-top: 2.2rem; flex-wrap: wrap;
  animation: rise .7s .32s both; }
.stat b { display: block; font-family: var(--display); font-size: 1.9rem; font-weight: 750;
  line-height: 1; color: var(--ink); }
.stat span { font-size: .85rem; color: var(--muted); font-weight: 500; }
.stat.chef { display: flex; align-items: center; gap: .55rem; padding: .3rem 1rem .3rem .35rem;
  background: #fff; border: 1px solid var(--line); border-radius: 999px; box-shadow: var(--shadow-sm); }
.stat.chef span { font-weight: 650; color: var(--ink-2); }
@keyframes rise { from { opacity: 0; transform: translateY(14px); } }
@keyframes marker { from { background-size: 0% 100%; } to { background-size: 100% 100%; } }
@media (max-width: 1180px) { .hero { grid-template-columns: minmax(0, 1fr) 450px; } .scene { zoom: .75; } }
.hero.lang-ja .hero-title { font-size: clamp(2.1rem, 3.5vw, 3.3rem) !important; line-height: 1.2 !important; }
.hero-title, .hero-sub, .section-title, .banner-title { word-break: auto-phrase; }
@media (max-width: 960px) {
  .hero { grid-template-columns: minmax(0, 1fr); padding: 2rem 1.4rem; }
  .scene { justify-self: center; zoom: .8; }
}
@media (max-width: 640px) {
  .block-container { padding: .6rem 1rem 2rem; }
  .hero { padding: 1.6rem 1.1rem; border-radius: 24px; }
  .hero .hero-title { font-size: 2.1rem !important; }
  .scene { zoom: .47; }
  .section-title { font-size: 1.45rem; }
  [class*="st-key-panel_"] { padding: 1rem; }
}
"""

_SCENE = """
.scene { position: relative; width: 600px; height: 380px; justify-self: end; }
.scene-glow { position: absolute; left: 150px; top: 80px; width: 380px; height: 310px;
  border-radius: 50%; background: radial-gradient(circle, rgba(255, 160, 100, .45), rgba(255, 160, 100, 0) 70%); }
.belt { position: absolute; left: 0; bottom: 50px; width: 262px; height: 18px; border-radius: 9px;
  background: #3A2A22; overflow: hidden; box-shadow: inset 0 -3px 0 rgba(0, 0, 0, .25),
  0 8px 16px rgba(58, 42, 34, .25); }
.belt span { position: absolute; inset: 4px 9px; border-radius: 6px;
  background: repeating-linear-gradient(90deg, #5E4A3E 0 10px, #46352C 10px 20px);
  animation: belt .45s linear infinite; }
.token { position: absolute; left: 0; bottom: 68px; width: 40px; height: 40px; border-radius: 50%;
  background: #fff; display: grid; place-items: center; z-index: 2;
  box-shadow: 0 6px 14px rgba(70, 35, 10, .2); animation: ride 7.2s linear infinite; }
.token svg { animation: wobble 1.1s ease-in-out infinite alternate; }
.machine { position: absolute; left: 215px; bottom: 26px; z-index: 3;
  filter: drop-shadow(0 18px 22px rgba(154, 52, 18, .3)); animation: hum 2.4s ease-in-out infinite; }
.machine .needle { transform-origin: 124px 126px; animation: needle 2.8s ease-in-out infinite; }
.floor { position: absolute; left: 200px; bottom: 12px; width: 230px; height: 24px; border-radius: 50%;
  background: radial-gradient(closest-side, rgba(120, 50, 15, .28), rgba(120, 50, 15, 0)); }
.puff { position: absolute; left: 343px; top: 154px; width: 22px; height: 22px; border-radius: 50%;
  background: #fff; opacity: 0; z-index: 2; box-shadow: 0 0 0 1px rgba(228, 210, 191, .7);
  animation: puff 3.3s ease-out infinite; }
.puff.p2 { animation-delay: 1.1s; }
.puff.p3 { animation-delay: 2.2s; }
.stack { position: absolute; left: 410px; top: 46px; width: 180px; height: 196px; border-radius: 16px;
  background: #fff; border: 1px solid var(--line); box-shadow: var(--shadow-md); }
.stack.s1 { rotate: -7deg; }
.stack.s2 { rotate: 8deg; left: 416px; top: 40px; }
.mini { position: absolute; left: 406px; top: 40px; width: 180px; padding: 6px; background: #fff;
  border-radius: 16px; box-shadow: var(--shadow-lg); z-index: 4; rotate: 2deg; opacity: 0;
  animation: produce 9s cubic-bezier(.2, .8, .2, 1) infinite; }
.mini.o2 { animation-delay: 3s; }
.mini.o3 { animation-delay: 6s; }
.mini .cover { border-radius: 11px !important; }
.mini-body { padding: .45rem .35rem .2rem; }
.mini-title { font-family: var(--display); font-weight: 700; font-size: .86rem; line-height: 1.2;
  color: var(--ink); min-height: 2.4em; display: -webkit-box; -webkit-line-clamp: 2;
  -webkit-box-orient: vertical; overflow: hidden; }
.mini-meta { display: flex; gap: .6rem; margin-top: .3rem; font-size: .72rem; font-weight: 650;
  color: var(--muted); }
.mini-meta span { display: inline-flex; align-items: center; gap: .22rem; }
.mini-meta .glyph { color: var(--brand); }
.scene-label { position: absolute; z-index: 5; display: flex; align-items: center; gap: .35rem;
  font-family: var(--display); font-style: italic; font-weight: 600; font-size: 1rem;
  color: var(--brand-deep); }
.scene-label.in { left: 4px; bottom: 12px; }
.scene-label.out { left: 286px; top: 6px; }
@keyframes belt { to { background-position: 20px 0; } }
@keyframes ride {
  0% { transform: translateX(-20px) scale(.4); opacity: 0; }
  7% { transform: translateX(0) scale(1); opacity: 1; }
  82% { transform: translateX(205px) scale(1); opacity: 1; }
  92%, 100% { transform: translateX(232px) scale(.5); opacity: 0; }
}
@keyframes wobble { from { transform: rotate(-8deg); } to { transform: rotate(8deg); } }
@keyframes hum { 50% { transform: translateY(-3px); } }
@keyframes needle { 0%, 100% { transform: rotate(-55deg); } 45% { transform: rotate(48deg); }
  60% { transform: rotate(28deg); } }
@keyframes puff { 0% { transform: translate(0, 0) scale(.4); opacity: 0; } 15% { opacity: .95; }
  100% { transform: translate(26px, -112px) scale(2.1); opacity: 0; } }
@keyframes produce {
  0% { opacity: 0; translate: -110px 120px; scale: .35; }
  8% { opacity: 1; translate: 0 0; scale: 1; }
  31% { opacity: 1; translate: 0 -6px; scale: 1; }
  38%, 100% { opacity: 0; translate: 46px -26px; scale: .92; }
}
"""

_SECTIONS = """
.section-head { display: flex; align-items: center; gap: 1rem; margin: 2.2rem 0 .9rem;
  scroll-margin-top: 6rem; }
.step { flex: none; width: 2.5rem; height: 2.5rem; border-radius: 50%; display: grid;
  place-items: center; background: var(--ink); color: #fff; font-family: var(--display);
  font-weight: 800; font-size: 1.15rem; box-shadow: 0 6px 14px rgba(34, 26, 21, .25); }
.section-title { font-family: var(--display); font-size: 1.8rem; font-weight: 750; line-height: 1.1;
  letter-spacing: -.015em; color: var(--ink); }
.section-hint { color: var(--muted); font-size: .95rem; margin-top: .2rem; }
[class*="st-key-panel_"] { background: var(--card); border: 1px solid var(--line); border-radius: 24px;
  padding: 1.4rem 1.6rem; box-shadow: var(--shadow-sm); }
.panel-title { font-family: var(--display); font-size: 1.45rem; font-weight: 750; color: var(--ink);
  letter-spacing: -.01em; }
.stTabs [role="tablist"] { gap: .4rem; flex-wrap: wrap; border: none; box-shadow: none; }
.stTabs [data-testid="stTab"] { height: auto; padding: .42rem .95rem; border-radius: 999px;
  background: var(--cream); border: 1px solid var(--line); transition: background .2s, border-color .2s; }
.stTabs [data-testid="stTab"]:hover { border-color: var(--brand-2); }
.stTabs [data-testid="stTab"] p { font-size: .88rem; font-weight: 600; color: var(--ink-2); }
.stTabs [data-testid="stTab"][aria-selected="true"] { background: var(--ink); border-color: var(--ink); }
.stTabs [data-testid="stTab"][aria-selected="true"] p { color: #fff; }
.stTabs .react-aria-SelectionIndicator { display: none; }
[data-testid="stButtonGroup"] button { border-radius: 999px; border: 1px solid var(--line-2);
  background: #fff; font-weight: 600; transition: transform .15s, background .2s, border-color .2s; }
[data-testid="stButtonGroup"] button:hover { border-color: var(--brand); transform: translateY(-1px); }
[data-testid="stButtonGroup"] button[aria-pressed="true"] { background: var(--brand) !important;
  border-color: var(--brand) !important; box-shadow: 0 6px 14px rgba(232, 89, 12, .28); }
[data-testid="stButtonGroup"] button[aria-pressed="true"] * { background: transparent !important; }
[data-testid="stButtonGroup"] button[aria-pressed="true"] p { color: #fff !important; }
.chips { display: flex; flex-wrap: wrap; align-items: center; gap: .4rem; margin: .4rem 0 .2rem; }
.chips .count { font-weight: 800; color: var(--ink); margin-right: .35rem; }
.chip { padding: .28rem .75rem; border-radius: 999px; background: var(--brand-soft);
  color: var(--brand-deep); font-weight: 650; font-size: .82rem; animation: rise .3s both; }
.chips.empty { color: var(--muted); font-size: .9rem; }
button[data-testid="stBaseButton-primary"] { border: none; font-weight: 700; padding: .6rem 1.6rem;
  background: linear-gradient(135deg, var(--brand-2), var(--brand));
  box-shadow: 0 10px 22px rgba(232, 89, 12, .3); transition: transform .2s, box-shadow .2s; }
button[data-testid="stBaseButton-primary"]:hover { transform: translateY(-2px);
  box-shadow: 0 14px 28px rgba(232, 89, 12, .4); }
button[data-testid="stBaseButton-secondary"] { background: #fff; border: 1px solid var(--line-2);
  font-weight: 600; }
button[data-testid="stBaseButton-secondary"]:hover { border-color: var(--brand); color: var(--brand); }
[data-testid="stExpander"] details { border-radius: 16px; border: 1px solid var(--line); background: #fff; }
[data-testid="stExpander"] summary p { font-weight: 650; }
[class*="st-key-w_view_"] [role="radiogroup"] { display: inline-flex; gap: .3rem; padding: .3rem;
  background: #fff; border: 1px solid var(--line); border-radius: 999px; box-shadow: var(--shadow-sm); }
[class*="st-key-w_view_"] label { margin: 0 !important; padding: .55rem 1.3rem; border-radius: 999px;
  cursor: pointer; transition: background .2s; }
[class*="st-key-w_view_"] [data-testid="stRadioOption"] > div > div:not([data-testid]) { display: none; }
[class*="st-key-w_view_"] label p { font-weight: 700; color: var(--ink-2); }
[class*="st-key-w_view_"] label:has(input:checked) { background: var(--ink); }
[class*="st-key-w_view_"] label:has(input:checked) p { color: #fff; }
.footer { display: flex; align-items: center; justify-content: center; gap: .8rem; margin: 4rem 0 .5rem;
  color: var(--muted); font-size: .88rem; }
.footer b { color: var(--ink); }
.footer-data { font-size: .8rem; margin-top: .15rem; }
"""

_RESULTS = """
.results-head { scroll-margin-top: 6.5rem; display: flex; align-items: baseline; flex-wrap: wrap; gap: .4rem 1rem; margin: 1.8rem 0 .9rem; }
.results-head .title { font-family: var(--display); font-size: 1.6rem; font-weight: 750; color: var(--ink); }
.results-head .count { color: var(--muted); font-weight: 600; }
.insight { position: relative; overflow: hidden; min-height: 168px; border-radius: 22px; padding: 1.3rem 1.5rem; }
.insight .big { font-family: var(--display); font-size: 3.2rem; font-weight: 800; line-height: 1; }
.insight .label { margin-top: .4rem; font-weight: 650; }
.insight.ready { background: linear-gradient(135deg, #EAF8ED, #D2EFD9); border: 1px solid #C3E8CB; }
.insight.ready .big { color: var(--green); }
.insight.ready::after { content: ""; position: absolute; right: -40px; bottom: -60px; width: 190px; height: 190px;
  border-radius: 50%; background: radial-gradient(circle, rgba(105, 219, 124, .45), rgba(105, 219, 124, 0) 70%); }
.insight.ready .label { color: #24502E; }
.insight.zero { background: var(--amber-soft); border: 1px solid #F5DDAA; }
.insight.zero .label { color: #6B4A00; margin: 0; }
.insight.best { background: linear-gradient(135deg, #2B1D16, #4E2B17); color: #FFEBDD; }
.insight.best::after { content: ""; position: absolute; right: -50px; top: -60px; width: 200px; height: 200px;
  border-radius: 50%; background: radial-gradient(circle, rgba(255, 138, 61, .55), rgba(255, 138, 61, 0) 70%); }
.insight.best .kicker { display: flex; align-items: center; gap: .4rem; font-size: .74rem; font-weight: 800;
  letter-spacing: .12em; text-transform: uppercase; color: #FFB37A; }
.insight.best .item { font-family: var(--display); font-size: 2.2rem; font-weight: 750; line-height: 1.1;
  color: #fff; margin: .35rem 0 .15rem; }
.insight.best .unlocks { font-weight: 650; color: #FFD8BF; }
.insight.best .examples { margin-top: .5rem; font-size: .85rem; color: #E9CDBA; }
[class*="st-key-card_"] { position: relative; gap: 0; padding: 0; overflow: hidden; background: var(--card);
  border: 1px solid var(--line); border-radius: 22px; box-shadow: var(--shadow-sm); cursor: pointer;
  transition: transform .28s cubic-bezier(.2, .8, .2, 1), box-shadow .28s; }
[class*="st-key-card_"]:hover { transform: translateY(-6px) scale(1.02); box-shadow: var(--shadow-lg); z-index: 2; }
[class*="st-key-card_"] .stButton, [class*="st-key-card_"] [class*="st-key-open_"] { position: static; }
[class*="st-key-card_"] button { position: absolute; inset: 0; width: 100%; height: 100%; opacity: 0;
  cursor: pointer; z-index: 3; border-radius: 22px; }
[class*="st-key-card_"] .cover { border-radius: 0 !important; }
.cover-photo { transition: transform .7s cubic-bezier(.2, .8, .2, 1); }
[class*="st-key-card_"]:hover .cover-photo { transform: scale(1.08); }
.rc { animation: rise .55s cubic-bezier(.2, .8, .2, 1) both; }
.rc-media { position: relative; }
.rc-media::after { content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 45%;
  background: linear-gradient(to top, rgba(20, 12, 8, .5), rgba(20, 12, 8, 0)); pointer-events: none; }
.badge { display: inline-flex; align-items: center; gap: .3rem; padding: .3rem .7rem; border-radius: 999px;
  font-size: .75rem; font-weight: 750; box-shadow: 0 4px 12px rgba(0, 0, 0, .12); }
.badge.ok { background: rgba(227, 244, 230, .96); color: var(--green); }
.badge.buy { background: rgba(255, 241, 214, .96); color: var(--amber); }
.badge.day { background: var(--ink); color: #fff; }
.rc-media .badge { position: absolute; top: 12px; left: 12px; z-index: 2; }
.rc-media .badge.right { left: auto; right: 12px; }
.rc-time { position: absolute; left: 12px; bottom: 10px; z-index: 2; display: inline-flex; align-items: center;
  gap: .3rem; color: #fff; font-size: .8rem; font-weight: 700; text-shadow: 0 1px 4px rgba(0, 0, 0, .45); }
.rc-body { padding: .9rem 1rem 1.05rem; }
.rc-title { font-family: var(--display); font-size: 1.08rem; font-weight: 700; line-height: 1.25;
  color: var(--ink); min-height: 2.5em; display: -webkit-box; -webkit-line-clamp: 2;
  -webkit-box-orient: vertical; overflow: hidden; }
.rc-match { display: flex; align-items: center; gap: .6rem; margin: .7rem 0 .45rem; }
.rc-bar { flex: 1; height: 7px; border-radius: 99px; background: #F3E9DF; overflow: hidden; }
.rc-bar i { display: block; height: 100%; border-radius: inherit; transform-origin: left;
  background: linear-gradient(90deg, #FFB37A, var(--brand)); animation: grow 1s .25s cubic-bezier(.2, .8, .2, 1) both; }
.rc-bar i.full { background: linear-gradient(90deg, #69DB7C, var(--green)); }
.rc-match span { font-size: .78rem; font-weight: 700; color: var(--ink-2); white-space: nowrap; }
.rc-meta { display: flex; flex-wrap: wrap; gap: .25rem .75rem; font-size: .8rem; color: var(--muted); }
.rc-meta span { display: inline-flex; align-items: center; gap: .25rem; }
.rc-meta .glyph { color: var(--brand); }
@keyframes grow { from { transform: scaleX(0); } }
"""

_DETAIL = """
.banner { position: relative; overflow: hidden; height: 420px; border-radius: 28px; margin: .8rem 0 1.6rem;
  box-shadow: var(--shadow-lg); animation: rise .5s both; }
.banner-bg { position: absolute; inset: 0; }
.banner-bg .cover { border-radius: 0 !important; }
.banner-bg .cover-photo { filter: blur(26px) saturate(1.25); transform: scale(1.3); }
.banner::after { content: ""; position: absolute; inset: 0; z-index: 1; pointer-events: none;
  background: linear-gradient(90deg, rgba(18, 10, 6, .88) 0%, rgba(18, 10, 6, .62) 55%, rgba(18, 10, 6, .3) 100%); }
.banner-inner { position: relative; z-index: 2; display: grid; grid-template-columns: minmax(0, 1fr) 440px;
  align-items: center; gap: 2.4rem; height: 100%; padding: 2rem 2.6rem; color: #fff; }
.banner-photo .cover { border-radius: 20px !important; border: 5px solid rgba(255, 255, 255, .92);
  box-shadow: 0 30px 60px rgba(0, 0, 0, .45); rotate: 2deg; animation: pop-in .8s .15s cubic-bezier(.2, 1.3, .4, 1) both; }
.banner-title { font-family: var(--display); font-size: clamp(1.9rem, 3.4vw, 3.1rem); font-weight: 750;
  line-height: 1.05; letter-spacing: -.02em; margin: .8rem 0 1.1rem; text-shadow: 0 2px 22px rgba(0, 0, 0, .35); }
@keyframes pop-in { from { opacity: 0; scale: .85; rotate: -4deg; } }
@media (max-width: 900px) {
  .banner { height: auto; }
  .banner-inner { grid-template-columns: 1fr; padding: 1.6rem; }
  .banner-photo { display: none; }
}
.facts { display: flex; flex-wrap: wrap; gap: .5rem; }
.fact { display: inline-flex; align-items: center; gap: .4rem; padding: .42rem .85rem; border-radius: 999px;
  font-size: .85rem; font-weight: 650; background: rgba(255, 255, 255, .16);
  border: 1px solid rgba(255, 255, 255, .3); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); }
.panel-head { display: flex; align-items: center; justify-content: space-between; gap: .6rem;
  flex-wrap: wrap; margin-bottom: .7rem; }
.legend { display: flex; gap: .4rem; flex-wrap: wrap; }
.tag { display: inline-flex; align-items: center; gap: .25rem; padding: .25rem .65rem; border-radius: 999px;
  font-size: .75rem; font-weight: 750; }
.tag.have { background: var(--green-soft); color: var(--green); }
.tag.missing { background: var(--amber-soft); color: var(--amber); }
.ing-row { display: flex; align-items: flex-start; gap: .75rem; padding: .62rem 0;
  border-bottom: 1px dashed var(--line); color: var(--ink-2); line-height: 1.45; }
.ing-row:last-child { border-bottom: none; }
.ing-row .mark { flex: none; display: grid; place-items: center; width: 1.45rem; height: 1.45rem;
  margin-top: .05rem; border-radius: 50%; font-size: .8rem; background: #F4ECE4; color: #B5A69A; }
.ing-row.have .mark { background: var(--green); color: #fff; }
.ing-row.missing .mark { background: #FFB020; color: #fff; }
.ing-row .buy { margin-left: auto; padding: .15rem .55rem; border-radius: 99px; white-space: nowrap;
  font-size: .72rem; font-weight: 750; color: var(--amber); background: var(--amber-soft); }
.ready-note { margin-top: .9rem; padding: .7rem .9rem; border-radius: 14px; background: var(--green-soft);
  color: var(--green); font-weight: 650; font-size: .9rem; }
.diet-row { display: flex; flex-wrap: wrap; gap: .4rem; margin-top: 1rem; }
.diet { padding: .25rem .7rem; border-radius: 999px; background: #EEF6EA; color: #3B6B2A;
  font-size: .78rem; font-weight: 650; }
.diet-note { margin-top: .5rem; font-size: .75rem; color: var(--muted); }
.step-row { display: flex; gap: 1rem; padding: .95rem 0; border-bottom: 1px solid var(--line); }
.step-row:last-child { border-bottom: none; }
.step-num { flex: none; display: grid; place-items: center; width: 2.3rem; height: 2.3rem; border-radius: 12px;
  background: var(--brand-soft); color: var(--brand-deep); font-family: var(--display); font-weight: 800;
  font-size: 1.05rem; }
.step-text { padding-top: .25rem; line-height: 1.65; color: var(--ink-2); }
.chef-head { display: flex; align-items: center; gap: 1.1rem; }
.chef-avatar { flex: none; display: grid; place-items: center; width: 88px; height: 88px; border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, #FFF4EA, #FFD6B6); box-shadow: inset 0 0 0 3px #fff, var(--shadow-sm); }
.chef-title { font-family: var(--display); font-size: 1.6rem; font-weight: 750; color: var(--ink); }
.chef-sub { color: var(--muted); font-size: .95rem; margin-top: .15rem; }
.bubble { max-width: 42rem; margin: 1.1rem 0 .8rem; padding: .85rem 1.1rem; border-radius: 4px 18px 18px 18px;
  background: var(--cream); border: 1px solid var(--line); color: var(--ink-2); }
[class*="st-key-ask_"] button { border-radius: 999px; background: var(--cream); font-size: .85rem; }
"""

_PLAN = """
.kpis { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1rem; margin: 1.4rem 0 .4rem; }
.kpi { display: flex; align-items: center; gap: 1rem; padding: 1.2rem 1.3rem; background: var(--card);
  border: 1px solid var(--line); border-radius: 22px; box-shadow: var(--shadow-sm); animation: rise .5s both; }
.kpi b { font-family: var(--display); font-size: 2.7rem; font-weight: 800; line-height: 1; color: var(--ink); }
.kpi .lbl { font-weight: 650; color: var(--muted); font-size: .9rem; }
.kpi .delta { display: inline-block; margin-top: .4rem; padding: .2rem .6rem; border-radius: 99px;
  font-size: .75rem; font-weight: 750; color: var(--green); background: var(--green-soft); }
.ring { flex: none; display: grid; place-items: center; width: 66px; height: 66px; border-radius: 50%;
  background: conic-gradient(var(--brand) calc(var(--p) * 1%), #F3E9DF 0); }
.ring span { display: grid; place-items: center; width: 50px; height: 50px; border-radius: 50%;
  background: #fff; font-weight: 800; font-size: .85rem; color: var(--ink); }
.st-key-panel_shopping { position: relative; padding-left: 3.4rem !important; background-color: #FFFEFA;
  background-image: linear-gradient(90deg, transparent 2.4rem, rgba(232, 72, 59, .35) 2.4rem,
    rgba(232, 72, 59, .35) calc(2.4rem + 2px), transparent calc(2.4rem + 2px)); }
.st-key-panel_shopping::before { content: ""; position: absolute; top: -12px; left: 50%; width: 120px;
  height: 26px; transform: translateX(-50%) rotate(-3deg); border-radius: 3px; background: rgba(255, 179, 122, .6); }
.st-key-panel_shopping [data-testid="stCheckbox"] { padding: .3rem 0; border-bottom: 1px dashed var(--line); }
.st-key-panel_shopping [data-testid="stCheckbox"]:has(input:checked) p { text-decoration: line-through;
  color: var(--muted); }
@media (max-width: 760px) { .kpis { grid-template-columns: 1fr; } }
"""

CSS = _BASE + _TOPBAR + _HERO + _SCENE + _SECTIONS + _RESULTS + _DETAIL + _PLAN


def inject_style() -> None:
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
