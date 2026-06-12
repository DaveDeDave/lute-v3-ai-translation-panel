from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.configs.logging import configure_logging
from src.configs.env import Settings, settings
from src.handlers.exceptions import register_exception_handlers
from src.libs.translator import HuggingFaceTranslator, ModelUnavailableError
from src.controllers.translate import create_translate_router

logger = logging.getLogger(__name__)


def create_app(
    app_settings: Settings | None = None,
    translator: HuggingFaceTranslator | None = None,
) -> FastAPI:
    resolved_settings = app_settings or settings
    active_translator = translator or HuggingFaceTranslator(resolved_settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        configure_logging(resolved_settings.log_level)
        logger.info(
            "Starting local translation server with config: %s",
            resolved_settings.public_dict(),
        )
        app.state.model_load_error = None

        try:
            active_translator.load()
        except ModelUnavailableError as exc:
            app.state.model_load_error = exc

        yield

    app = FastAPI(lifespan=lifespan)
    app.include_router(create_translate_router(resolved_settings, active_translator))
    register_exception_handlers(app, resolved_settings)
    return app


app = create_app()
