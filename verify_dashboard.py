
from playwright.sync_api import sync_playwright
import time

def verify_dashboard():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            # Wait for server to start
            time.sleep(3)

            page.goto("http://127.0.0.1:5000/")

            # Check title
            print("Title:", page.title())

            # Take screenshot
            page.screenshot(path="dashboard_verification.png")
            print("Screenshot saved to dashboard_verification.png")

            # Check if we can see the "Scan Results" tab active
            assert page.is_visible("#scan-results"), "Scan results tab not visible"

        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="error.png")
        finally:
            browser.close()

if __name__ == "__main__":
    verify_dashboard()
