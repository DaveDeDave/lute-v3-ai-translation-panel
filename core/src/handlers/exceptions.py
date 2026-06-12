from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.configs.env import Settings
from src.libs.utility.render_html import html_response

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI, settings: Settings) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        _request: Request,
        exc: StarletteHTTPException,
    ) -> HTMLResponse:
        if exc.status_code == 404:
            message = "The requested page was not found."
            title = "Not Found"
        else:
            message = str(exc.detail)
            title = "Translation Error"
        return html_response(
            settings,
            status_code=exc.status_code,
            title=title,
            error=message,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_request: Request, exc: Exception) -> HTMLResponse:
        logger.exception("Unhandled application error")
        return html_response(
            settings,
            status_code=500,
            title="Translation Error",
            error="An unexpected server error occurred.",
        )
