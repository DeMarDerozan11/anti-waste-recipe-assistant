import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Pictogrammes, symboles divers, dingbats, fleches colorees et selecteurs d'emoji.
EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿⬀-⯿⏩-⏺️‍]")


def test_the_interface_contains_no_emoji():
    files = [ROOT / "app.py", *sorted((ROOT / "src").rglob("*.py"))]
    found = {f.name: sorted(set(EMOJI.findall(f.read_text(encoding="utf-8")))) for f in files}
    assert {name: chars for name, chars in found.items() if chars} == {}
