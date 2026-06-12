from __future__ import annotations

import logging

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from src.configs.env import Settings
from src.libs.translator import (
    HuggingFaceTranslator,
    ModelUnavailableError,
    TranslationError,
)
from src.libs.utility.render_html import html_response

logger = logging.getLogger(__name__)


def create_translate_router(
    settings: Settings, translator: HuggingFaceTranslator
) -> APIRouter:
    router = APIRouter()

    @router.get("/translate", response_class=HTMLResponse)
    def translate(request: Request, payload: str | None = None) -> HTMLResponse:
        if payload is None or payload.strip() == "":
            return html_response(
                settings,
                status_code=400,
                title="Translation Error",
                error="Missing required query parameter: payload.",
            )

        if len(payload) > settings.max_input_chars:
            return html_response(
                settings,
                status_code=413,
                title="Translation Error",
                error=f"Payload is too large. Maximum length is {settings.max_input_chars} characters.",
            )

        logger.info("Translation request received with payload length %s", len(payload))
        load_error = getattr(request.app.state, "model_load_error", None)
        if load_error is not None:
            logger.error(
                "Translation unavailable because model failed to load",
                exc_info=(type(load_error), load_error, load_error.__traceback__),
            )
            return html_response(
                settings,
                status_code=500,
                title="Translation Error",
                source_text=payload,
                error="Internal Server Error",
            )

        try:
            result = translator.translate(payload)
        except (ModelUnavailableError, TranslationError) as exc:
            logger.exception("Translation request failed", exc)
            return html_response(
                settings,
                status_code=500,
                title="Translation Error",
                source_text=payload,
                error="Internal Server Error",
            )

        logger.info("Translation success in %.3fs", result.elapsed_seconds)
        return html_response(
            settings,
            status_code=200,
            title="Translation",
            source_text=payload,
            translation=result.text,
        )

    return router
