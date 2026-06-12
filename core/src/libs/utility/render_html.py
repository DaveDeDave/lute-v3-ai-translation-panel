from __future__ import annotations

from pathlib import Path

from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.configs.env import Settings

_templates = Environment(
    loader=FileSystemLoader(Path(__file__).parents[2] / "views"),
    autoescape=select_autoescape(("html", "xml")),
)


def html_response(
    settings: Settings,
    *,
    status_code: int,
    title: str,
    source_text: str = "",
    translation: str = "",
    error: str = "",
) -> HTMLResponse:
    html = _templates.get_template("response_template.html").render(
        title=title,
        model_label=settings.model_label,
        source_text=source_text,
        source_language=settings.source_language_default,
        target_language=settings.target_language_default,
        translation=translation,
        error=error,
    )
    return HTMLResponse(
        html,
        status_code=status_code,
        media_type="text/html; charset=utf-8",
    )
