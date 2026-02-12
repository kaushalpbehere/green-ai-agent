import threading
import time
import pytest
from unittest.mock import patch, MagicMock
from playwright.sync_api import sync_playwright
import sys
import os

# Add src to path just in case
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ui.dashboard_app import app
from src.core.domain import Project

# Mock project with XSS payload
xss_payload = "<img src=x onerror=window.xss_triggered=true>"
malicious_project_name = f"Project {xss_payload}"
malicious_project = Project(
    name=malicious_project_name,
    repo_url="http://example.com",
    language="Python",
    id="proj-xss"
)

@pytest.fixture(scope="module")
def server():
    # Patch get_project_manager to return our malicious project
    with patch('src.ui.dashboard_app.get_project_manager') as mock_pm:
        mock_pm.return_value.list_projects.return_value = [malicious_project]

        # Start server in thread
        port = 5002
        server_thread = threading.Thread(target=app.run, kwargs={'port': port, 'use_reloader': False})
        server_thread.daemon = True
        server_thread.start()

        # Wait for server to be responsive
        base_url = f"http://127.0.0.1:{port}"
        time.sleep(3)

        yield base_url

def test_dashboard_xss(server):
    with sync_playwright() as p:
        # Launch browser (headless by default)
        try:
            browser = p.chromium.launch()
        except Exception as e:
            pytest.skip(f"Could not launch browser: {e}")
            return

        page = browser.new_page()

        try:
            # Navigate to dashboard
            page.goto(server)

            # Wait for the project card to appear (it's loaded via JS)
            try:
                page.wait_for_selector(".project-card", timeout=10000)
            except Exception:
                # If it times out, print content for debugging
                print("Timeout waiting for .project-card. Page content:")
                print(page.content())
                raise

            # Check if XSS triggered
            is_xss_triggered = page.evaluate("() => window.xss_triggered === true")
            assert not is_xss_triggered, "XSS vulnerability detected! window.xss_triggered was true."

            # Check if the project card is rendered correctly
            project_name_el = page.locator(".project-name").first
            project_name_text = project_name_el.inner_text()

            print(f"Project Name Text: {project_name_text}")
            assert xss_payload in project_name_text, f"Payload not found in text content. Found: {project_name_text}"

            # Verify it is escaped in HTML source
            html_content = project_name_el.inner_html()
            assert "&lt;img" in html_content, "Payload does not appear to be escaped in HTML source"
            assert "<img" not in html_content, "Payload appears unescaped in HTML source"

        finally:
            browser.close()
