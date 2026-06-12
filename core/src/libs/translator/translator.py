from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from threading import Lock

from src.configs.env import Settings

logger = logging.getLogger(__name__)


class ModelUnavailableError(RuntimeError):
    """Raised when the configured model cannot be loaded locally."""


class TranslationError(RuntimeError):
    """Raised when model inference fails."""


@dataclass
class TranslationResult:
    text: str
    elapsed_seconds: float


class HuggingFaceTranslator:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._tokenizer = None
        self._model = None
        self._lock = Lock()

    def load(self) -> None:
        if self._tokenizer is not None and self._model is not None:
            return

        with self._lock:
            if self._tokenizer is not None and self._model is not None:
                return

            logger.info(
                "Loading model '%s' from cache directory '%s'",
                self._settings.mt_model,
                self._settings.model_cache_dir,
            )
            try:
                from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

                self._tokenizer = AutoTokenizer.from_pretrained(
                    self._settings.mt_model,
                    cache_dir=self._settings.model_cache_dir,
                    local_files_only=True,
                )
                self._model = AutoModelForSeq2SeqLM.from_pretrained(
                    self._settings.mt_model,
                    cache_dir=self._settings.model_cache_dir,
                    local_files_only=True,
                )
                self._model.to("cpu")
                self._model.eval()
            except Exception as exc:
                logger.exception("Failed to load model '%s'", self._settings.mt_model)
                raise ModelUnavailableError(
                    "The configured translation model is not available locally. "
                    "Run python scripts/prefetch_model.py before starting the app."
                ) from exc

            logger.info("Model '%s' loaded successfully", self._settings.mt_model)

    def translate(self, text: str) -> TranslationResult:
        self.load()
        assert self._tokenizer is not None
        assert self._model is not None

        start = time.perf_counter()
        try:
            inputs = self._tokenizer(text, return_tensors="pt", truncation=True)
            output_tokens = self._model.generate(**inputs)
            translated = self._tokenizer.decode(output_tokens[0], skip_special_tokens=True)
        except Exception as exc:
            logger.exception("Translation inference failed")
            raise TranslationError("Translation failed while running model inference.") from exc

        return TranslationResult(
            text=translated,
            elapsed_seconds=time.perf_counter() - start,
        )
