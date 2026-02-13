
import pytest
from unittest.mock import patch
from flask import render_template_string
import src.ui.dashboard_app as dashboard_app

def test_load_template_simulating_crash():
    # If the error message contains something that looks like Jinja syntax (e.g. {{ 1/0 }}),
    # and render_template_string renders it, it will execute it and crash with ZeroDivisionError.

    with patch('builtins.open', side_effect=FileNotFoundError("File {{ 1/0 }} not found")):
        template_content = dashboard_app.load_template('crash.html')

        # Verify the template content contains the jinja syntax from the error message
        # But wrapped in raw blocks
        assert "{{ 1/0 }}" in template_content

        with dashboard_app.app.app_context():
            # This should NOT crash now, because we are using {% raw %} blocks
            try:
                rendered = render_template_string(template_content)
                # Verify it rendered literally
                assert "{{ 1/0 }}" in rendered
            except ZeroDivisionError:
                pytest.fail("render_template_string executed the error message as a template!")
            except Exception as e:
                 pytest.fail(f"render_template_string failed: {e}")

def test_load_template_simulating_syntax_error():
     with patch('builtins.open', side_effect=FileNotFoundError("File {% if %} not found")):
        template_content = dashboard_app.load_template('syntax.html')

        with dashboard_app.app.app_context():
             # This should also succeed now
             try:
                 rendered = render_template_string(template_content)
                 # Replaced content should be present as HTML entity
                 assert "&#123;% if %}" in rendered
             except Exception as e:
                 pytest.fail(f"render_template_string failed on syntax error message: {e}")

def test_load_template_simulating_xss():
    with patch('builtins.open', side_effect=FileNotFoundError("File <script>alert(1)</script> not found")):
        template_content = dashboard_app.load_template('xss.html')

        with dashboard_app.app.app_context():
            rendered = render_template_string(template_content)
            # Verify it contains escaped HTML entities (so browser displays tags as text)
            assert "&lt;script&gt;alert(1)&lt;/script&gt;" in rendered
            # Verify it does NOT contain raw script tag (which would be executed)
            assert "<script>" not in rendered
