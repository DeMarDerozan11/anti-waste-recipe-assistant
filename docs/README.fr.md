# Assistant Recettes anti-gaspi

*English version: [README.md](../README.md)*

Application qui répond à une question concrète : **que cuisiner avec ce que j'ai, en
achetant le moins possible ?** On coche les aliments que l'on a ; elle cherche par
faisabilité (pas seulement par ressemblance), propose le « meilleur achat », planifie un menu
qui minimise les courses et répond aux questions sur une recette.

> Capture / GIF de démo : à ajouter ici après le déploiement.

## Fonctionnalités

- **Liste d'aliments à cocher** (142 aliments, 9 catégories, noms dans 4 langues), avec une
  section « Autre » en texte libre et un remplissage par **photo du frigo**.
- **Recherche par faisabilité** : classe les recettes selon (ingrédients que vous avez) −
  (ingrédients à acheter). Une liste de « basiques » (sel, huile, beurre...) est supposée
  disponible, désactivable.
- **Meilleur achat** : indique quel ingrédient débloque le plus de recettes réalisables, et
  permet de simuler cet achat.
- **Filtres** : régime (végétarien, végan, sans gluten, sans lactose, sans porc, sans fruits à
  coque), temps total, « léger », nombre de courses.
- **Planificateur** : choisit plusieurs repas en réutilisant les mêmes achats, et affiche le
  résultat chiffré (articles à acheter, part du frigo utilisée, comparaison avec un choix recette
  par recette).
- **Harvey, le chef virtuel** : questions sur une recette (sans four, pour 2 personnes,
  substitutions), dans la langue choisie.
- **4 langues** (français, anglais, espagnol, japonais) : interface, aliments, titres de
  recettes et fiches. Les aliments de la liste sont traduits localement, le reste par le LLM.

## Architecture

```
Dataset (Food.com) --ingest--> recipes.json + index FAISS (embeddings MiniLM)

Aliments coches / « Autre » --> Catalog (index inverse par ingredient, en memoire)
   --> filtres (regime, temps, calories, photo) --> cartes
   [envie particuliere] --> reclassement semantique FAISS
Planificateur : Catalog --> optimiseur glouton (src/optimizer.py)
Chef, photo, traduction : LLM via Groq (ancre sur la recette affichee)
```

| Brique | Choix | Raison |
|---|---|---|
| Faisabilité | index inversé + comparaison de mots | exact et instantané ; les embeddings trouvent des recettes proches, pas réalisables |
| Embeddings | `all-MiniLM-L6-v2` + FAISS `IndexFlatL2` | léger, CPU ; sert au reclassement par « envie » |
| LLM | `openai/gpt-oss-120b` via Groq (`GROQ_MODEL`) | seul modèle de chat accessible sur l'offre développeur utilisée |
| Vision | `qwen/qwen3.8-27b` via Groq (`GROQ_VISION_MODEL`) | modèle d'image listé par la documentation Groq |
| Interface | Streamlit | déploiement gratuit sur Community Cloud |

L'optimiseur est volontairement simple et testable : à chaque jour, il retient la recette qui
utilise le plus d'ingrédients encore inemployés pour le moins d'achats nouveaux ; un article
déjà prévu ne coûte rien, et un article partagé par d'autres recettes coûte un peu moins.

## Installation

```bash
conda create -n recettes python=3.11 -y && conda activate recettes
pip install -r requirements.txt
# si faiss-cpu ne s'installe pas via pip : conda install -c conda-forge faiss-cpu
cp .env.example .env                        # y mettre la clé Groq
```

## Utilisation

```bash
python -m src.ingest --input data/recipes.csv --format foodcom --sample 30000
python -m src.check_images --dry-run   # mesure les liens d'images morts
python -m src.check_images             # retire les liens morts de data/recipes.json
python -m streamlit run app.py   # « python -m » : utilise le Streamlit de l'environnement actif
python -m pytest
python -m src.evaluate --write         # mesure la recherche, écrit docs/evaluation.md
```

Lancer les commandes depuis la racine du projet. L'ingestion enregistre le temps, les
calories, les portions, la note et l'image : la relancer après une mise à jour du code.

## Qualité

`python -m src.evaluate` rejoue 30 listes d'aliments réalistes (`eval/queries.json`) et mesure,
sur les 12 premières recettes : part de requêtes sans résultat, recettes prêtes, recettes à
2 achats près, nombre moyen d'achats, couverture des ingrédients, temps de réponse. Il compare
trois variantes (basiques ou non, avec ou sans le filtre photo). Le rapport est dans
[`docs/evaluation.md`](evaluation.md) une fois la commande lancée.

## Limites connues

- Les recettes sont en anglais : leur traduction (titres, fiches) est faite par le LLM, sans
  mesure de qualité, et les japonais/espagnols n'ont pas été relus par un locuteur natif.
- La correspondance compare des mots : « butter » peut être confondu avec « peanut butter ».
  Le décompte « à acheter » est approximatif.
- Les régimes sont détectés par mots-clés : indicatif, pas une garantie d'allergènes.
- Les calories sont celles du jeu de données (probablement par portion, non vérifié). Le
  filtre sur le temps ou les calories exclut les recettes sans cette information.
- Les recettes sans photo sont masquées pour l'instant ; une illustration par type de plat
  (`src/visuals.py`) s'affiche quand le lien d'une photo ne charge plus. Les images sont celles
  de Food.com (liens externes qui peuvent disparaître : relancer `src.check_images`).
- La photo du frigo dépend du modèle de vision que le compte Groq autorise ; elle n'a pas été
  testée avec le vrai service.
- Chaque recherche en langue non anglaise consomme des requêtes Groq (traduction des titres) :
  les limites de l'offre gratuite peuvent être atteintes.

## Déploiement

Voir la section « Deploy » du [README anglais](../README.md#deploy) : jeu de données compact
`demo/` (`python -m src.build_demo`), clé Groq dans les secrets, limite d'appels au LLM par
session (`MAX_LLM_CALLS_PER_SESSION`, 60 par défaut).
