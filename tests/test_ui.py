import pytest
from playwright.sync_api import Page, expect
import subprocess
import time
import os
import signal

@pytest.fixture(scope="module", autouse=True)
def run_streamlit():
    # Start Streamlit in the background
    proc = subprocess.Popen(
        ["streamlit", "run", "app.py", "--server.port", "8501", "--server.headless", "true"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        preexec_fn=os.setsid
    )
    # Wait for Streamlit to start
    time.sleep(5)
    yield
    # Kill the Streamlit process group
    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)

def test_streamlit_app_runs(page: Page):
    # Go to the local Streamlit app
    page.goto("http://localhost:8501")

    # Wait for the app to load
    expect(page).to_have_title("Quantum Key Distribution Simulator")

    # Run the simulation
    run_button = page.get_by_role("button", name="Run Simulation")
    expect(run_button).to_be_visible()
    run_button.click()

    # Wait for simulation to complete (increased timeout for simulation)
    # We look for "Simulation Complete!" text in the status area
    # Note: Streamlit status updates can be found in the UI.
    expect(page.get_by_text("Simulation Complete!")).to_be_visible(timeout=60000)

    # Check if results are displayed
    expect(page.get_by_text("Sifted Key Result")).to_be_visible()
    expect(page.get_by_text("QBER:")).to_be_visible()

    # Check if visualizations are present (Bloch spheres, circuits)
    # They are rendered in the UI
    expect(page.get_by_text("Real-time Quantum Circuit & State Visualization")).to_be_visible()
