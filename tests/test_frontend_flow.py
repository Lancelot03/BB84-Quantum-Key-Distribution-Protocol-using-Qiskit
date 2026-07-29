import os
import pytest
from playwright.sync_api import sync_playwright

def test_frontend_flow():
    # Set up directories for screenshots and videos in the git-ignored verification/ folder
    os.makedirs("verification/videos", exist_ok=True)
    os.makedirs("verification/screenshots", exist_ok=True)

    with sync_playwright() as p:
        # Launch headless browser
        browser = p.chromium.launch(headless=True)
        # Create context to record video
        context = browser.new_context(
            record_video_dir="verification/videos"
        )
        page = context.new_page()

        try:
            # Go to Streamlit app
            page.goto("http://localhost:8501")
            page.wait_for_timeout(3000)

            # Click "Run Simulation" button
            run_btn = page.get_by_text("Run Simulation", exact=True)
            run_btn.scroll_into_view_if_needed()
            page.wait_for_timeout(500)
            run_btn.click()

            # Wait for simulation to complete
            page.wait_for_selector("text=Simulation Complete", timeout=60000)
            page.wait_for_timeout(2000)

            # Take a screenshot
            page.screenshot(path="verification/screenshots/verification.png")
            page.wait_for_timeout(1000)

        finally:
            context.close()
            browser.close()
