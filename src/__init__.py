import os

# faiss (conda) et torch (pip) embarquent chacun libomp : sans ca, abort sur macOS.
# Doit etre defini avant le premier import de faiss ou torch.
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
