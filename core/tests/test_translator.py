from __future__ import annotations

import sys
import types

from src.configs.env import Settings
from src.libs.translator import HuggingFaceTranslator


class FakeTokenizer:
    from_kwargs = None

    @classmethod
    def from_pretrained(cls, *args, **kwargs):
        cls.from_kwargs = kwargs
        return cls()

    def __call__(self, text, **kwargs):
        return {"input_ids": [text], **kwargs}

    def decode(self, _tokens, skip_special_tokens):
        assert skip_special_tokens is True
        return "translated text"


class FakeModel:
    from_kwargs = None

    @classmethod
    def from_pretrained(cls, *args, **kwargs):
        cls.from_kwargs = kwargs
        return cls()

    def to(self, device):
        self.device = device

    def eval(self):
        self.evaluated = True

    def generate(self, **_inputs):
        return [["tokens"]]


def test_translator_loads_local_only_and_translates(monkeypatch, tmp_path):
    fake_transformers = types.SimpleNamespace(
        AutoTokenizer=FakeTokenizer,
        AutoModelForSeq2SeqLM=FakeModel,
    )
    monkeypatch.setitem(sys.modules, "transformers", fake_transformers)

    settings = Settings(
        mt_model="example/model",
        source_language_default="Finnish",
        target_language_default="English",
        model_cache_dir=str(tmp_path),
    )
    translator = HuggingFaceTranslator(settings)

    result = translator.translate("source text")

    assert result.text == "translated text"
    assert result.elapsed_seconds >= 0
    assert FakeTokenizer.from_kwargs["cache_dir"] == str(tmp_path)
    assert FakeTokenizer.from_kwargs["local_files_only"] is True
    assert FakeModel.from_kwargs["cache_dir"] == str(tmp_path)
    assert FakeModel.from_kwargs["local_files_only"] is True
