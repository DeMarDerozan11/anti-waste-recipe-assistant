# Demo dataset

Compact dataset published with the code so the app can run online without the full
`data/` folder. Generate it from your local data (recipes with a working photo only):

```bash
python -m src.check_images
python -m src.build_demo --size 12000
```

This writes `recipes.faiss` and `recipes.json.gz` here. Keep each file under 50 MB
(GitHub warns above 50 MB and rejects files above 100 MB); lower `--size` if needed.
