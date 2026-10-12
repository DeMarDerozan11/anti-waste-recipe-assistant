"""Detection des ingredients sur une photo (modele de vision Groq)."""
import base64
import json
import os
import re

from src.errors import ValidationError
from src.generate import LLMError, chat

VISION_MODEL = os.getenv("GROQ_VISION_MODEL", "qwen/qwen3.8-27b")
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_BYTES = 4_000_000
MAX_INGREDIENTS = 30
MAX_NAME_CHARS = 60


_THINKING = re.compile(r"<think>.*?</think>", re.DOTALL)


def _json_part(raw: str) -> str:
    """Un modele a reflexion peut entourer le JSON de texte : on isole l'objet."""
    raw = _THINKING.sub("", raw)
    return raw[raw.find("{"): raw.rfind("}") + 1]


def parse_ingredients(raw: str) -> list[str]:
    try:
        items = json.loads(_json_part(raw)).get("ingredients", [])
    except (json.JSONDecodeError, AttributeError) as exc:
        raise LLMError("err_vision_unreadable") from exc
    names = [str(i).strip()[:MAX_NAME_CHARS] for i in items if str(i).strip()]
    return list(dict.fromkeys(names))[:MAX_INGREDIENTS]


def detect_ingredients(data: bytes, mime: str) -> list[str]:
    if mime not in ALLOWED_TYPES:
        raise ValidationError("err_image_format")
    if len(data) > MAX_BYTES:
        raise ValidationError("err_image_big")
    image = base64.b64encode(data).decode()
    prompt = (
        "List the distinct food ingredients visible in this photo. Reply only with JSON "
        '{"ingredients": ["..."]}, names in English, singular, no quantities.'
    )
    content = [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{image}"}},
    ]
    raw = chat(
        [{"role": "user", "content": content}],
        json_mode=True,
        temperature=0,
        model=VISION_MODEL,
    )
    return parse_ingredients(raw)
