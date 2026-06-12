from __future__ import annotations

from src.libs.utility.render_html import _templates


def test_html_template_escapes_translation_values():
    html = _templates.get_template("response_template.html").render(
        title="<Title>",
        model_label='model-"x"',
        source_text="<script>alert(1)</script>",
        source_language="A&B",
        target_language="C>D",
        translation='"quoted"',
    )

    assert "&lt;Title&gt;" in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "A&amp;B" in html
    assert "C&gt;D" in html
    assert "model-&#34;x&#34;" in html
    assert "&#34;quoted&#34;" in html


def test_render_error_page_escapes_error():
    html = _templates.get_template("response_template.html").render(
        title="Error",
        model_label="model",
        source_language="Finnish",
        target_language="English",
        error="Bad <payload>",
    )

    assert 'class="error"' in html
    assert "Bad &lt;payload&gt;" in html
