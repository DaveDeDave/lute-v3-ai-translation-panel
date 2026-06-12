from __future__ import annotations

from dataclasses import dataclass

from fastapi.testclient import TestClient

from src.configs.env import Settings
from src.libs.translator import TranslationError
from src.main import create_app


@dataclass
class FakeResult:
    text: str
    elapsed_seconds: float = 0.01


class FakeTranslator:
    def __init__(self, *, fail: bool = False):
        self.fail = fail
        self.loaded = False
        self.translated_payloads: list[str] = []

    def load(self) -> None:
        self.loaded = True

    def translate(self, text: str) -> FakeResult:
        self.translated_payloads.append(text)
        if self.fail:
            raise TranslationError("fake failure")
        return FakeResult(text=f"translated: {text}")


def _settings(**overrides) -> Settings:
    values = {
        "max_input_chars": 20,
        "mt_model": "example/model",
        "source_language_default": "Finnish",
        "target_language_default": "English",
    }
    values.update(overrides)
    return Settings(**values)


def test_translate_success_returns_html():
    translator = FakeTranslator()
    app = create_app(_settings(), translator=translator)

    with TestClient(app) as client:
        response = client.get("/translate", params={"payload": "Hei"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "Hei" in response.text
    assert "translated: Hei" in response.text
    assert translator.translated_payloads == ["Hei"]


def test_translate_missing_payload_returns_400():
    app = create_app(_settings(), translator=FakeTranslator())

    with TestClient(app) as client:
        response = client.get("/translate")

    assert response.status_code == 400
    assert "Missing required query parameter" in response.text


def test_translate_empty_payload_returns_400():
    app = create_app(_settings(), translator=FakeTranslator())

    with TestClient(app) as client:
        response = client.get("/translate", params={"payload": "   "})

    assert response.status_code == 400


def test_translate_oversized_payload_returns_413():
    app = create_app(_settings(max_input_chars=3), translator=FakeTranslator())

    with TestClient(app) as client:
        response = client.get("/translate", params={"payload": "abcd"})

    assert response.status_code == 413
    assert "Maximum length is 3" in response.text


def test_translate_failure_returns_500_html():
    app = create_app(_settings(), translator=FakeTranslator(fail=True))

    with TestClient(app) as client:
        response = client.get("/translate", params={"payload": "Hei"})

    assert response.status_code == 500
    assert response.headers["content-type"].startswith("text/html")
    assert "Internal Server Error" in response.text
    assert "fake failure" not in response.text


def test_unknown_route_returns_html_404():
    app = create_app(_settings(), translator=FakeTranslator())

    with TestClient(app) as client:
        response = client.get("/missing")

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("text/html")
    assert "The requested page was not found" in response.text
