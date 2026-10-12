"""Affichage des noms d'aliments et de recettes dans la langue de l'utilisateur."""
from src.pantry import local_label


def localize(texts: list[str], language: str, translate_batch) -> dict[str, str]:
    """Associe chaque texte anglais a sa version traduite.

    Les aliments de la liste sont traduits localement ; le reste part en un seul lot vers
    `translate_batch(textes, langue)`. Si le lot echoue, l'exception remonte a l'appelant.
    """
    unique = list(dict.fromkeys(texts))
    if language == "en":
        return {text: text for text in unique}
    mapping, unknown = {}, []
    for text in unique:
        local = local_label(text, language)
        if local:
            mapping[text] = local
        else:
            unknown.append(text)
    if unknown:
        mapping.update(zip(unknown, translate_batch(unknown, language)))
    return mapping
