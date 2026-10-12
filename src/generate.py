"""Appels au LLM (Groq) : traduction et utilitaires communs."""
import json
import os

import groq
from dotenv import load_dotenv

from src.errors import AppError
from src.i18n import LLM_NAMES

load_dotenv()

# Modifiable via .env : les fournisseurs retirent regulierement d'anciens modeles.
LLM_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")


class LLMError(AppError):
    """Erreur du fournisseur LLM : le message affiche est traduit (cle + parametres)."""


_call_guard = None


def set_call_guard(guard) -> None:
    """Fonction appelee avant chaque requete (ex. quota par visiteur) ; elle peut lever LLMError."""
    global _call_guard
    _call_guard = guard


def get_client() -> groq.Groq:
    key = os.getenv("GROQ_API_KEY")
    if not key or key == "your_key_here":
        raise LLMError("err_llm_key")
    return groq.Groq(api_key=key)


def format_recipe(recipe: dict) -> str:
    steps = "\n".join(f"{n}. {s}" for n, s in enumerate(recipe["directions"], 1))
    return (
        f"### {recipe['title']}\n"
        f"Ingredients: {'; '.join(recipe['ingredients'])}\n"
        f"Steps:\n{steps}"
    )


def chat(
    messages: list[dict],
    json_mode: bool = False,
    temperature: float = 0.4,
    model: str | None = None,
) -> str:
    if _call_guard is not None:
        _call_guard()
    kwargs = {"response_format": {"type": "json_object"}} if json_mode else {}
    try:
        response = get_client().chat.completions.create(
            model=model or LLM_MODEL, messages=messages, temperature=temperature, **kwargs
        )
    except groq.RateLimitError as exc:
        raise LLMError("err_llm_rate") from exc
    except groq.AuthenticationError as exc:
        raise LLMError("err_llm_auth") from exc
    except (groq.APIConnectionError, groq.APITimeoutError) as exc:
        raise LLMError("err_llm_network") from exc
    except groq.NotFoundError as exc:
        raise LLMError("err_llm_model", model=model or LLM_MODEL) from exc
    except groq.APIStatusError as exc:
        raise LLMError("err_llm_status", status=exc.status_code, message=exc.message) from exc
    except groq.APIError as exc:
        raise LLMError("err_llm_other", message=exc.message) from exc
    return response.choices[0].message.content or ""


def translate_to_english(text: str) -> str:
    """Les recettes et les embeddings sont en anglais : on traduit la requete avant la recherche."""
    system = (
        "Translate the user's list of ingredients or food request into English. "
        "Output only the translation, nothing else. If it is already English, repeat it."
    )
    result = chat(
        [{"role": "system", "content": system}, {"role": "user", "content": text}],
        temperature=0,
    ).strip()
    return result or text


def translate_batch(texts: list[str], language: str) -> list[str]:
    """Traduit des titres ou des noms d'aliments en un seul appel ; renvoie l'original en cas
    de reponse inexploitable plutot que de decaler les traductions."""
    system = (
        f"Translate each English text into {LLM_NAMES[language]}. These are recipe titles or "
        'food names. Reply only with JSON {"translations": [...]} holding exactly '
        f"{len(texts)} strings, in the same order."
    )
    raw = chat(
        [{"role": "system", "content": system},
         {"role": "user", "content": json.dumps(texts, ensure_ascii=False)}],
        json_mode=True,
        temperature=0,
    )
    try:
        translated = json.loads(raw[raw.find("{"): raw.rfind("}") + 1])["translations"]
    except (json.JSONDecodeError, KeyError, TypeError):
        return list(texts)
    if not isinstance(translated, list) or len(translated) != len(texts):
        return list(texts)
    return [str(t) for t in translated]


def translate_recipe(recipe: dict, language: str) -> str:
    system = (
        f"Translate the recipe into {LLM_NAMES[language]}. Keep every quantity. Output "
        "markdown: a '### ' heading with the title, then the translated words for "
        "'Ingredients' and 'Steps' as bold labels, ingredients as a bullet list, steps as a "
        "numbered list. Output only the translation."
    )
    return chat(
        [{"role": "system", "content": system}, {"role": "user", "content": format_recipe(recipe)}],
        temperature=0,
    )
