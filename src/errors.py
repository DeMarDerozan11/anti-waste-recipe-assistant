"""Erreurs affichables : `key` designe un message traduit (voir i18n)."""


class AppError(Exception):
    def __init__(self, key: str, **params) -> None:
        super().__init__(key)
        self.key = key
        self.params = params


class ValidationError(AppError, ValueError):
    """Saisie refusee."""
