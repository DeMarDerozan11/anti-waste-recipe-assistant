import groq
import httpx
import pytest

from src import chef, generate, vision
from src.i18n import describe


def _status_error(cls, status):
    request = httpx.Request("POST", "https://api.groq.com")
    return cls("boom", response=httpx.Response(status, request=request), body=None)


class FailingClient:
    def __init__(self, error):
        self.chat = self
        self.completions = self
        self._error = error

    def create(self, **_):
        raise self._error


@pytest.mark.parametrize("error, key", [
    (_status_error(groq.RateLimitError, 429), "err_llm_rate"),
    (_status_error(groq.AuthenticationError, 401), "err_llm_auth"),
    (_status_error(groq.NotFoundError, 404), "err_llm_model"),
    (_status_error(groq.InternalServerError, 500), "err_llm_status"),
])
def test_provider_errors_become_translatable_llm_errors(monkeypatch, error, key):
    monkeypatch.setattr(generate, "get_client", lambda: FailingClient(error))
    with pytest.raises(generate.LLMError) as caught:
        generate.chat([{"role": "user", "content": "hi"}])
    assert caught.value.key == key
    assert describe(caught.value, "en")


def test_missing_api_key_is_reported(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(generate.LLMError) as caught:
        generate.get_client()
    assert caught.value.key == "err_llm_key"


def test_chef_sends_recipe_history_and_question(monkeypatch):
    sent = {}
    monkeypatch.setattr(chef, "chat", lambda messages: sent.update(m=messages) or "ok")
    recipe = {"title": "Soup", "ingredients": ["water"], "directions": ["Boil."]}
    history = [{"role": "user", "content": f"q{i}"} for i in range(20)]

    assert chef.ask_chef(recipe, history, "no oven?", "ja") == "ok"

    messages = sent["m"]
    assert "Soup" in messages[0]["content"] and "Japanese" in messages[0]["content"]
    assert len(messages) == 1 + chef.MAX_TURNS + 1
    assert messages[-1] == {"role": "user", "content": "no oven?"}


def test_vision_parses_and_cleans_ingredients():
    assert vision.parse_ingredients('{"ingredients": ["tomate", " ", "tomate", "oeuf"]}') == ["tomate", "oeuf"]
    with pytest.raises(generate.LLMError):
        vision.parse_ingredients("not json")


def test_vision_tolerates_thinking_text_around_the_json():
    raw = '<think>hmm, a fridge</think>Voici : {"ingredients": ["oeuf", "lait"]} voila'
    assert vision.parse_ingredients(raw) == ["oeuf", "lait"]


def test_vision_rejects_bad_files_before_any_api_call(monkeypatch):
    monkeypatch.setattr(vision, "chat", lambda *a, **k: pytest.fail("no API call expected"))
    with pytest.raises(ValueError):
        vision.detect_ingredients(b"x", "application/pdf")
    with pytest.raises(ValueError):
        vision.detect_ingredients(b"x" * (vision.MAX_BYTES + 1), "image/png")


def test_vision_sends_the_image_to_the_vision_model(monkeypatch):
    seen = {}

    def fake_chat(messages, json_mode, temperature, model):
        seen.update(model=model, content=messages[0]["content"])
        return '{"ingredients": ["carotte"]}'

    monkeypatch.setattr(vision, "chat", fake_chat)
    assert vision.detect_ingredients(b"abc", "image/png") == ["carotte"]
    assert seen["model"] == vision.VISION_MODEL
    assert seen["content"][1]["image_url"]["url"].startswith("data:image/png;base64,")


def test_unknown_model_error_names_the_model(monkeypatch):
    monkeypatch.setattr(generate, "get_client", lambda: FailingClient(_status_error(groq.NotFoundError, 404)))
    with pytest.raises(generate.LLMError) as caught:
        generate.chat([{"role": "user", "content": "hi"}], model="my-vision-model")
    assert "my-vision-model" in describe(caught.value, "fr")


def test_translate_batch_keeps_the_order_and_falls_back_on_a_bad_answer(monkeypatch):
    monkeypatch.setattr(generate, "chat", lambda *a, **k: '{"translations": ["Soupe", "Tarte"]}')
    assert generate.translate_batch(["Soup", "Pie"], "fr") == ["Soupe", "Tarte"]
    monkeypatch.setattr(generate, "chat", lambda *a, **k: '{"translations": ["Soupe"]}')
    assert generate.translate_batch(["Soup", "Pie"], "fr") == ["Soup", "Pie"]
    monkeypatch.setattr(generate, "chat", lambda *a, **k: "not json")
    assert generate.translate_batch(["Soup", "Pie"], "fr") == ["Soup", "Pie"]


def test_the_call_guard_runs_before_any_request(monkeypatch):
    def refuse():
        raise generate.LLMError("err_llm_quota", max=3)

    monkeypatch.setattr(generate, "get_client", lambda: pytest.fail("no request expected"))
    generate.set_call_guard(refuse)
    try:
        with pytest.raises(generate.LLMError) as caught:
            generate.chat([{"role": "user", "content": "hi"}])
    finally:
        generate.set_call_guard(None)
    assert describe(caught.value, "en") == "AI call limit reached for this session (3): please try again later."
