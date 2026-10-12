"""Index en memoire : retrouve les recettes realisables avec ce que l'on a."""
from collections import Counter, defaultdict
from dataclasses import dataclass

from src.diets import violates
from src.matching import analyze, tokens

CANDIDATE_LIMIT = 20000
EXAMPLES = 3


@dataclass(frozen=True)
class Filters:
    diets: tuple[str, ...] = ()
    max_minutes: int | None = None
    max_calories: float | None = None
    with_photo: bool = False

    def accepts(self, recipe: dict) -> bool:
        minutes, calories = recipe.get("minutes"), recipe.get("calories")
        if self.with_photo and not recipe.get("image"):
            return False
        if self.max_minutes is not None and (minutes is None or minutes > self.max_minutes):
            return False
        if self.max_calories is not None and (calories is None or calories > self.max_calories):
            return False
        return not any(violates(diet, recipe) for diet in self.diets)


class Catalog:
    def __init__(self, recipes: list[dict]) -> None:
        self.recipes = recipes
        with_photo = sum(1 for r in recipes if r.get("image"))
        self.photo_share = with_photo / len(recipes) if recipes else 0.0
        self._postings: dict[str, set[int]] = defaultdict(set)
        for index, recipe in enumerate(recipes):
            for name in recipe["NER"]:
                for token in tokens(name):
                    self._postings[token].add(index)

    def _candidates(self, wanted: list[str], min_have: int) -> list[int]:
        """Surensemble des recettes utilisant un ingredient voulu (verifie ensuite)."""
        counts: Counter = Counter()
        for term in wanted:
            found: set[int] = set()
            for token in tokens(term):
                found |= self._postings.get(token, set())
            counts.update(found)
        return [i for i, c in counts.most_common(CANDIDATE_LIMIT) if c >= min_have]

    def _scored(self, wanted: list[str], staples: frozenset, min_have: int) -> list[tuple]:
        """Trie par (ingredients utilises - ingredients a acheter), puis moins de courses."""
        rows = []
        for index in self._candidates(wanted, min_have):
            recipe = self.recipes[index]
            result = analyze(wanted, recipe, staples)
            have, missing = result["have"], result["missing"]
            if len(have) >= min_have:
                no_photo = 0 if recipe.get("image") else 1
                rating = recipe.get("rating") or 0
                rows.append(
                    (len(missing) - len(have), len(missing), no_photo, -rating, index, have, missing)
                )
        rows.sort(key=lambda row: row[:5])
        return rows

    @staticmethod
    def default_min_have(wanted: list[str]) -> int:
        return 1 if len(wanted) < 2 else 2

    def search(
        self,
        wanted: list[str],
        *,
        staples: frozenset = frozenset(),
        filters: Filters = Filters(),
        max_missing: int | None = None,
        limit: int = 12,
        min_have: int | None = None,
    ) -> list[dict]:
        wanted = [w for w in wanted if tokens(w)]
        if not wanted:
            return []
        if min_have is None:
            min_have = self.default_min_have(wanted)
        results = []
        for _, n_missing, _, _, index, have, missing in self._scored(wanted, staples, min_have):
            recipe = self.recipes[index]
            if max_missing is not None and n_missing > max_missing:
                continue
            if filters.accepts(recipe):
                results.append({**recipe, "id": index, "have": have, "missing": missing})
                if len(results) >= limit:
                    break
        return results

    def opportunities(
        self,
        wanted: list[str],
        *,
        staples: frozenset = frozenset(),
        filters: Filters = Filters(),
        top: int = 3,
    ) -> dict:
        """Recettes faisables maintenant, et achats qui en debloquent le plus."""
        wanted = [w for w in wanted if tokens(w)]
        if not wanted:
            return {"cookable": 0, "purchases": []}
        min_have = self.default_min_have(wanted)
        cookable = 0
        unlocked: Counter = Counter()
        examples: dict[str, list[str]] = defaultdict(list)
        for _, n_missing, _, _, index, _, missing in self._scored(wanted, staples, min_have):
            if n_missing > 1:
                continue
            recipe = self.recipes[index]
            if not filters.accepts(recipe):
                continue
            if n_missing == 0:
                cookable += 1
                continue
            unlocked[missing[0]] += 1
            if len(examples[missing[0]]) < EXAMPLES:
                examples[missing[0]].append(recipe["title"])
        purchases = [
            {"item": item, "count": count, "examples": examples[item]}
            for item, count in unlocked.most_common(top)
        ]
        return {"cookable": cookable, "purchases": purchases}
