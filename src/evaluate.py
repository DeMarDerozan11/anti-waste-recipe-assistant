"""Mesure la recherche par faisabilite sur un jeu de requetes fixe (sans appel au LLM).

Pour chaque requete, on regarde les 12 premieres recettes proposees :
- pretes : recettes sans rien a acheter ;
- a_2_pres : recettes avec 2 achats au plus ;
- manque_moyen : nombre moyen d'ingredients a acheter ;
- couverture : part moyenne des ingredients de l'utilisateur utilises par la recette.
"""
import argparse
import json
import statistics
import time
from datetime import date
from pathlib import Path

from src.catalog import Catalog, Filters
from src.matching import STAPLES

ROOT = Path(__file__).resolve().parent.parent
QUERIES_PATH = ROOT / "eval" / "queries.json"
REPORT_PATH = ROOT / "docs" / "evaluation.md"
TOP = 12


def run_query(catalog: Catalog, wanted: list[str], staples: frozenset, filters: Filters) -> dict:
    started = time.perf_counter()
    results = catalog.search(wanted, staples=staples, filters=filters, limit=TOP)
    elapsed = time.perf_counter() - started
    n = len(results)
    return {
        "resultats": n,
        "pretes": sum(1 for r in results if not r["missing"]),
        "a_2_pres": sum(1 for r in results if len(r["missing"]) <= 2),
        "manque_moyen": statistics.mean(len(r["missing"]) for r in results) if n else None,
        "couverture": statistics.mean(len(r["have"]) / len(wanted) for r in results) if n else None,
        "secondes": elapsed,
    }


def _mean(rows: list[dict], key: str) -> float | None:
    values = [r[key] for r in rows if r[key] is not None]
    return statistics.mean(values) if values else None


def summarize(rows: list[dict]) -> dict:
    """Moyennes sur l'ensemble des requetes ; `sans_resultat` = requetes sans aucune recette."""
    times = sorted(r["secondes"] for r in rows)
    return {
        "requetes": len(rows),
        "sans_resultat": sum(1 for r in rows if r["resultats"] == 0),
        "avec_une_recette_prete": sum(1 for r in rows if r["pretes"] > 0),
        "pretes": _mean(rows, "pretes"),
        "a_2_pres": _mean(rows, "a_2_pres"),
        "manque_moyen": _mean(rows, "manque_moyen"),
        "couverture": _mean(rows, "couverture"),
        "p95_secondes": times[min(len(times) - 1, int(len(times) * 0.95))],
    }


def evaluate(catalog: Catalog, queries: list[dict], staples: frozenset, filters: Filters) -> dict:
    rows = [run_query(catalog, q["wanted"], staples, filters) for q in queries]
    return summarize(rows)


def _fmt(value, digits: int = 2) -> str:
    return "-" if value is None else f"{value:.{digits}f}"


def report(catalog: Catalog, queries: list[dict]) -> str:
    variants = [
        ("Avec les basiques, recettes avec photo", STAPLES, Filters(with_photo=True)),
        ("Avec les basiques, toutes les recettes", STAPLES, Filters()),
        ("Sans les basiques, recettes avec photo", frozenset(), Filters(with_photo=True)),
    ]
    lines = [
        "# Évaluation de la recherche par faisabilité",
        "",
        f"Mesure du {date.today().isoformat()} sur {len(catalog.recipes)} recettes "
        f"({catalog.photo_share:.0%} avec photo), {len(queries)} requêtes, top {TOP}.",
        "",
        "| Variante | Sans résultat | Au moins 1 recette prête | Prêtes (moy.) | À 2 achats près (moy.) "
        "| Manque (moy.) | Couverture (moy.) | p95 (s) |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for name, staples, filters in variants:
        s = evaluate(catalog, queries, staples, filters)
        lines.append(
            f"| {name} | {s['sans_resultat']}/{s['requetes']} | {s['avec_une_recette_prete']}/{s['requetes']} "
            f"| {_fmt(s['pretes'])} | {_fmt(s['a_2_pres'])} | {_fmt(s['manque_moyen'])} "
            f"| {_fmt(s['couverture'], 2)} | {_fmt(s['p95_secondes'], 3)} |"
        )
    lines += [
        "",
        "Limites : une recette « prête » contient les ingrédients, pas forcément une bonne recette ; "
        "la correspondance compare des mots (voir README) ; 30 requêtes donnent une tendance, "
        "pas une preuve.",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="enregistre docs/evaluation.md")
    args = parser.parse_args()
    from src.ingest import RECIPES_PATH

    catalog = Catalog(json.loads(RECIPES_PATH.read_text(encoding="utf-8")))
    queries = json.loads(QUERIES_PATH.read_text(encoding="utf-8"))
    text = report(catalog, queries)
    print(text)
    if args.write:
        REPORT_PATH.parent.mkdir(exist_ok=True)
        REPORT_PATH.write_text(text + "\n", encoding="utf-8")
        print(f"\nÉcrit dans {REPORT_PATH}")


if __name__ == "__main__":
    main()
