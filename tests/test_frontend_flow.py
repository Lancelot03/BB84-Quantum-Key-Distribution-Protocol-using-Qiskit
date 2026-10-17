import os
import socket
import subprocess
import time
import pytest
from playwright.sync_api import sync_playwright

def is_port_open(host="127.0.0.1", port=8501):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            return True
        except ConnectionRefusedError:
            return False

@pytest.fixture(scope="session", autouse=True)
def streamlit_server():
    """Start the Streamlit server if it is not already running."""
    server_process = None
    if not is_port_open():
        print("Streamlit server not running on port 8501. Starting it...")
        # Start server with CORS and XSRF disabled as per Streamlit config practices
        server_process = subprocess.Popen(
            [
                "streamlit",
                "run",
                "app.py",
                "--server.port",
                "8501",
                "--server.address",
                "127.0.0.1",
                "--server.enableCORS",
                "false",
                "--server.enableXsrfProtection",
                "false"
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        # Wait for the server to spin up
        for _ in range(30):
            if is_port_open():
                print("Streamlit server is ready.")
                break
            time.sleep(0.5)
        else:
            raise RuntimeError("Streamlit server failed to start on port 8501.")
    else:
        print("Streamlit server is already running on port 8501.")

    yield

    if server_process:
        print("Stopping Streamlit server...")
        server_process.terminate()
        server_process.wait()

def test_frontend_flow():
    """End-to-end integration and frontend flow test using Playwright."""
    os.makedirs("verification/videos", exist_ok=True)
    os.makedirs("verification/screenshots", exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Video is recorded at the context level
        context = browser.new_context(
            record_video_dir="verification/videos"
        )
        page = context.new_page()

        try:
            # 1. Navigate to the app
            page.goto("http://127.0.0.1:8501")
            page.wait_for_timeout(2000)

            # Ensure page has loaded by waiting for the main heading to be visible
            heading = page.get_by_role("heading", name="🔐 Quantum Key Distribution")
            heading.wait_for(state="visible", timeout=10000)

            # 2. Select qubits and options, then Run Simulation
            run_btn = page.get_by_role("button", name="Run Simulation")
            run_btn.scroll_into_view_if_needed()
            page.wait_for_timeout(500)
            run_btn.click()
            page.wait_for_timeout(4000) # Wait for simulation to complete

            # Verify that we got a sifting report or key display
            sifted_result_header = page.get_by_text("Sifted Key Result")
            sifted_result_header.wait_for(state="visible", timeout=10000)

            # Expand the Post-Processing Details
            expander_title = "Post-Processing Details (Error Correction & Privacy Amplification)"
            expander = page.get_by_text(expander_title)
            if expander.is_visible():
                expander.scroll_into_view_if_needed()
                page.wait_for_timeout(500)
                expander.click()
                page.wait_for_timeout(1000)

            # Take a screenshot of the main tab showing sifting and results
            page.screenshot(path="verification/screenshots/simulation_tab.png")
            page.wait_for_timeout(500)

            # 3. Switch to 'Visual Learning' tab
            visual_learning_tab = page.get_by_role("tab", name="🎓 Visual Learning")
            visual_learning_tab.scroll_into_view_if_needed()
            page.wait_for_timeout(500)
            visual_learning_tab.click()
            page.wait_for_timeout(1000)

            # Click the Animations sub-tab
            animations_sub_tab = page.get_by_role("tab", name="🎨 Animations")
            animations_sub_tab.scroll_into_view_if_needed()
            page.wait_for_timeout(500)
            animations_sub_tab.click()
            page.wait_for_timeout(1000)

            # Take a screenshot of the visual learning animations
            page.screenshot(path="verification/screenshots/visual_learning_tab.png")
            page.wait_for_timeout(1000)

        finally:
            context.close()
            browser.close()
