from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.configs.env import Settings


def test_settings_defaults_for_optional_values(monkeypatch):
    for name in (
        "PORT",
        "HOST",
        "LOG_LEVEL",
        "MODEL_CACHE_DIR",
        "MAX_INPUT_CHARS",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("MT_MODEL", "example/default-model")
    monkeypatch.setenv("SOURCE_LANGUAGE_DEFAULT", "Finnish")
    monkeypatch.setenv("TARGET_LANGUAGE_DEFAULT", "English")

    settings = Settings(_env_file=None)

    assert settings.port == 8000
    assert settings.host == "0.0.0.0"
    assert settings.log_level == "INFO"
    assert settings.mt_model == "example/default-model"
    assert settings.model_label == "default-model"
    assert settings.source_language_default == "Finnish"
    assert settings.target_language_default == "English"
    assert settings.model_cache_dir == "/model_cache"
    assert settings.max_input_chars == 1000


def test_settings_from_environment(monkeypatch):
    monkeypatch.setenv("PORT", "9000")
    monkeypatch.setenv("HOST", "127.0.0.1")
    monkeypatch.setenv("LOG_LEVEL", "debug")
    monkeypatch.setenv("MT_MODEL", "example/model")
    monkeypatch.setenv("MODEL_CACHE_DIR", "cache")
    monkeypatch.setenv("SOURCE_LANGUAGE_DEFAULT", "Dutch")
    monkeypatch.setenv("TARGET_LANGUAGE_DEFAULT", "Polish")
    monkeypatch.setenv("MAX_INPUT_CHARS", "42")

    settings = Settings(_env_file=None)

    assert settings.port == 9000
    assert settings.host == "127.0.0.1"
    assert settings.log_level == "debug"
    assert settings.mt_model == "example/model"
    assert settings.model_cache_dir == "cache"
    assert settings.source_language_default == "Dutch"
    assert settings.target_language_default == "Polish"
    assert settings.max_input_chars == 42


def test_extra_environment_values_are_ignored(monkeypatch):
    monkeypatch.setenv("MT_MODEL", "example/model")
    monkeypatch.setenv("SOURCE_LANGUAGE_DEFAULT", "Finnish")
    monkeypatch.setenv("TARGET_LANGUAGE_DEFAULT", "English")
    monkeypatch.setenv("UNRELATED_CACHE_DIR", "hf-cache")
    monkeypatch.setenv("MODEL_CACHE_DIR", "model-cache")

    settings = Settings(_env_file=None)

    assert settings.model_cache_dir == "model-cache"


def test_invalid_port_raises(monkeypatch):
    monkeypatch.setenv("MT_MODEL", "example/model")
    monkeypatch.setenv("SOURCE_LANGUAGE_DEFAULT", "Finnish")
    monkeypatch.setenv("TARGET_LANGUAGE_DEFAULT", "English")
    monkeypatch.setenv("PORT", "70000")

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_required_translation_settings_raise_when_missing(monkeypatch):
    monkeypatch.delenv("MT_MODEL", raising=False)
    monkeypatch.delenv("SOURCE_LANGUAGE_DEFAULT", raising=False)
    monkeypatch.delenv("TARGET_LANGUAGE_DEFAULT", raising=False)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_language_labels_require_content(monkeypatch):
    monkeypatch.setenv("MT_MODEL", "example/model")
    monkeypatch.setenv("SOURCE_LANGUAGE_DEFAULT", "")
    monkeypatch.setenv("TARGET_LANGUAGE_DEFAULT", "")

    with pytest.raises(ValidationError):
        Settings(_env_file=None)
