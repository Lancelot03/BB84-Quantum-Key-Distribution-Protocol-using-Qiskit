import os
import time
import socket
import subprocess
import pytest
from playwright.sync_api import Page, expect

def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

@pytest.fixture(scope="module", autouse=True)
def streamlit_server():
    # If already running on 8501, use it. Otherwise, start it.
    proc = None
    if not is_port_open(8501):
        proc = subprocess.Popen(
            ["streamlit", "run", "app.py", "--server.port", "8501", "--server.headless", "true"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        # Wait for server to start
        for _ in range(30):
            if is_port_open(8501):
                break
            time.sleep(0.5)

    yield

    if proc:
        proc.terminate()
        proc.wait()

def test_streamlit_frontend_flow(page: Page):
    # Navigate to the Streamlit app
    page.goto("http://localhost:8501")

    # 1. Assert title is present
    expect(page.get_by_text("🔐 Quantum Key Distribution Simulator")).to_be_visible()

    # Let's ensure page loads properly
    page.wait_for_timeout(2000)

    # 2. Trigger a simulation run
    run_btn = page.get_by_role("button", name="Run Simulation")
    expect(run_btn).to_be_visible()
    run_btn.click()

    # Wait for the status of simulation to complete
    page.wait_for_selector("text=Simulation Complete", timeout=15000)

    # Assert QBER is visible
    expect(page.get_by_text("QBER:")).to_be_visible()

    # 3. Go to "Visual Learning" Tab
    page.get_by_text("Visual Learning").click()
    page.wait_for_timeout(1000)

    # Navigate to "Animations" sub-tab within Visual Learning
    page.get_by_text("Animations").click()
    page.wait_for_timeout(1000)

    # Verify elements inside Animations are rendered, like the canvas or photon indicators
    expect(page.get_by_text("Photon Transmission")).to_be_visible()

    # Capture screenshot/video to verification/ directory
    os.makedirs("verification", exist_ok=True)
    page.screenshot(path="verification/frontend_test_screenshot.png")
