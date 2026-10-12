"""Verifie que les images des recettes chargent encore et retire les liens morts.

Ne touche pas a l'index : seuls les champs `image` de recipes.json changent.
"""
import argparse
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.client import HTTPException
from urllib.error import URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from src.ingest import RECIPES_PATH

TIMEOUT = 8
WORKERS = 16
USER_AGENT = "Mozilla/5.0 (compatible; recipe-rag-assistant image check)"


def encode_url(url: str) -> str:
    """Certains liens du jeu de donnees contiennent des espaces : on les encode comme le
    navigateur (%20), sans toucher aux caracteres deja encodes."""
    return quote(url, safe=":/?&=#%+,;@~-_.!*$'()")


def is_alive(url: str) -> bool:
    """Demande 1 octet seulement : on veut savoir si l'image existe, pas la telecharger."""
    try:
        request = Request(encode_url(url), headers={"User-Agent": USER_AGENT, "Range": "bytes=0-0"})
        with urlopen(request, timeout=TIMEOUT) as response:
            return response.headers.get_content_type().startswith("image/")
    except (URLError, HTTPException, OSError, ValueError):
        return False


def check_urls(urls: list[str], workers: int = WORKERS, on_progress=None) -> dict[str, bool]:
    results: dict[str, bool] = {}
    with ThreadPoolExecutor(workers) as pool:
        futures = {pool.submit(is_alive, url): url for url in urls}
        for done, future in enumerate(as_completed(futures), 1):
            results[futures[future]] = future.result()
            if on_progress and done % 500 == 0:
                on_progress(done, len(futures))
    return results


def remove_dead_images(recipes: list[dict], alive: dict[str, bool]) -> int:
    removed = 0
    for recipe in recipes:
        url = recipe.get("image")
        if url and not alive.get(url, False):
            recipe["image"] = ""
            removed += 1
    return removed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="mesurer sans modifier le fichier")
    args = parser.parse_args()

    recipes = json.loads(RECIPES_PATH.read_text(encoding="utf-8"))
    urls = sorted({r["image"] for r in recipes if r.get("image")})
    print(f"{len(urls)} images à vérifier sur {len(recipes)} recettes")
    alive = check_urls(urls, on_progress=lambda d, t: print(f"  {d}/{t}"))
    ok = sum(alive.values())
    print(f"{ok} images valides, {len(urls) - ok} liens morts ou bloqués")
    if args.dry_run:
        return
    removed = remove_dead_images(recipes, alive)
    temporary = RECIPES_PATH.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(recipes), encoding="utf-8")
    os.replace(temporary, RECIPES_PATH)
    print(f"{removed} recettes sans image fonctionnelle : lien retiré")


if __name__ == "__main__":
    main()
