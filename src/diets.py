"""Regimes alimentaires : detection par mots-cles sur les ingredients.

Indicatif seulement : une liste de mots ne remplace pas une etiquette d'allergenes.
"""
import re
from dataclasses import dataclass

DIETS = ("vegetarian", "vegan", "gluten_free", "dairy_free", "pork_free", "nut_free")


def _words(*items: str) -> re.Pattern:
    alternatives = "|".join(re.escape(i) for i in items)
    return re.compile(rf"\b(?:{alternatives})(?:e?s)?\b")


@dataclass(frozen=True)
class _Rule:
    forbidden: re.Pattern
    allowed: re.Pattern | None = None

    def violated_by(self, text: str) -> bool:
        if self.allowed:
            text = self.allowed.sub(" ", text)
        return bool(self.forbidden.search(text))


_MEAT = ("beef", "pork", "bacon", "ham", "hamburger", "sausage", "chicken", "turkey", "lamb",
         "veal", "duck", "steak", "prosciutto", "pancetta", "chorizo", "salami", "pepperoni",
         "bologna", "rib", "brisket", "venison", "bison", "hot dog", "gelatin", "lard")
_FISH = ("fish", "tuna", "salmon", "cod", "tilapia", "halibut", "trout", "anchovy",
         "anchovie", "sardine", "shrimp", "prawn", "crab", "lobster", "clam", "oyster",
         "mussel", "scallop", "squid", "calamari", "worcestershire")
_DAIRY = ("milk", "cheese", "butter", "cream", "yogurt", "yoghurt", "whey", "ghee",
          "buttermilk", "cheddar", "mozzarella", "parmesan", "ricotta", "feta", "mascarpone",
          "custard", "half-and-half")
_DAIRY_OK = ("coconut milk", "almond milk", "soy milk", "oat milk", "rice milk", "cashew milk",
             "coconut cream", "peanut butter", "almond butter", "cocoa butter", "nut butter",
             "cream of tartar", "apple butter", "non-dairy", "dairy-free", "vegan butter",
             "vegan cheese", "sunflower seed butter")
_GLUTEN = ("wheat", "flour", "bread", "breadcrumb", "panko", "pasta", "spaghetti", "macaroni",
           "noodle", "couscous", "barley", "rye", "semolina", "bulgur", "seitan", "soy sauce",
           "beer", "tortilla", "cracker", "pita", "bagel", "biscuit", "orzo", "lasagna",
           "udon", "ramen", "puff pastry", "phyllo", "wonton", "malt", "oat", "cake mix")
_GLUTEN_OK = ("gluten-free", "gluten free", "rice flour", "corn flour", "almond flour",
              "coconut flour", "chickpea flour", "tapioca flour", "potato flour",
              "buckwheat flour", "rice noodle", "corn tortilla", "rice paper")
_PORK = ("pork", "bacon", "ham", "sausage", "prosciutto", "pancetta", "chorizo", "lard",
         "pepperoni", "salami", "hot dog", "bologna", "rib")
_PORK_OK = ("turkey bacon", "turkey sausage", "chicken sausage", "turkey ham",
            "turkey pepperoni", "beef bacon", "beef sausage")
_NUTS = ("almond", "walnut", "pecan", "cashew", "pistachio", "hazelnut", "peanut",
         "macadamia", "nut", "pine nut")

_VEGETARIAN = _Rule(_words(*_MEAT, *_FISH))
_DAIRY_RULE = _Rule(_words(*_DAIRY), _words(*_DAIRY_OK))
_RULES = {
    "vegetarian": _VEGETARIAN,
    "vegan": _Rule(
        _words(*_MEAT, *_FISH, *_DAIRY, "egg", "honey"), _words(*_DAIRY_OK)
    ),
    "gluten_free": _Rule(_words(*_GLUTEN), _words(*_GLUTEN_OK)),
    "dairy_free": _DAIRY_RULE,
    "pork_free": _Rule(_words(*_PORK), _words(*_PORK_OK)),
    "nut_free": _Rule(_words(*_NUTS), _words("nutmeg", "coconut", "butternut")),
}


def _text(recipe: dict) -> str:
    return " ".join(recipe["NER"]).lower()


def violates(diet: str, recipe: dict) -> bool:
    return _RULES[diet].violated_by(_text(recipe))


def satisfied_diets(recipe: dict) -> list[str]:
    return [diet for diet in _RULES if not violates(diet, recipe)]
