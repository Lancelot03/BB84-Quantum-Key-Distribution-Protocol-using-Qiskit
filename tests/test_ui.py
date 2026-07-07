import re
import pytest
from playwright.sync_api import Page, expect

def test_streamlit_ui(page: Page):
    # Streamlit runs on port 8501 by default
    page.goto("http://localhost:8501")

    # Wait for the app to load
    page.wait_for_selector("h1", timeout=60000)
    expect(page.get_by_text("Quantum Key Distribution Simulator")).to_be_visible()

    # Click "Run Simulation"
    page.get_by_role("button", name="Run Simulation").click()

    # Wait for simulation to finish
    page.wait_for_selector("text=Simulation Complete!", timeout=60000)

    # Check for results
    expect(page.get_by_text("Sifted Key Result")).to_be_visible()
    expect(page.get_by_text("QBER:")).to_be_visible()

    # Verify Visualizations
    expect(page.get_by_text("Real-time Quantum Circuit & State Visualization")).to_be_visible()

    # Capture screenshot for manual inspection if needed
    page.screenshot(path="verification/ui_verification.png", full_page=True)
