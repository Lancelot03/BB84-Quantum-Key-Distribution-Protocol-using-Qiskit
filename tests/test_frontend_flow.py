import pytest
import subprocess
import socket
import time
import os
import signal
from playwright.sync_api import Page, expect

def is_port_open(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0)
        return s.connect_ex((host, port)) == 0

@pytest.fixture(scope="session", autouse=True)
def streamlit_server():
    host = "127.0.0.1"
    port = 8501

    # Check if server is already running
    if is_port_open(host, port):
        yield
        return

    # Start Streamlit server
    cmd = [
        "streamlit", "run", "app.py",
        "--server.port", str(port),
        "--server.address", host,
        "--server.headless", "true",
        "--global.developmentMode", "false",
        "--browser.gatherUsageStats", "false"
    ]

    # Run the server in a new process group to make it easy to kill all subprocesses
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid if hasattr(os, "setsid") else None
    )

    # Wait for the server to start
    start_time = time.time()
    started = False
    while time.time() - start_time < 20:
        if is_port_open(host, port):
            started = True
            break
        time.sleep(0.5)

    if not started:
        # Fetch output if any to help debugging
        try:
            outs, errs = process.communicate(timeout=1.0)
            print("Streamlit STDOUT:", outs.decode())
            print("Streamlit STDERR:", errs.decode())
        except Exception:
            pass
        process.terminate()
        raise RuntimeError("Streamlit server failed to start on port 8501")

    yield

    # Teardown: stop the server
    try:
        if hasattr(os, "killpg"):
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        else:
            process.terminate()
    except Exception:
        pass

def test_streamlit_e2e(page: Page):
    # Navigate to the local Streamlit application
    page.goto("http://127.0.0.1:8501")

    # Wait for page elements to load
    page.wait_for_selector("text=Quantum Key Distribution Simulator", timeout=15000)

    # Ensure Title is present in a heading role
    header = page.get_by_role("heading", name="🔐 Quantum Key Distribution Simulator")
    expect(header).to_be_visible()

    # Interact with "Run Simulation" button
    run_btn = page.get_by_role("button", name="Run Simulation")
    expect(run_btn).to_be_visible()
    run_btn.scroll_into_view_if_needed()
    run_btn.click()

    # Wait for the simulation results to render (e.g. "Sifted Key Result" section header)
    page.wait_for_selector("text=Sifted Key Result", timeout=30000)

    # Ensure QBER section is present
    page.wait_for_selector("text=QBER", timeout=5000)

    # Ensure we create verification/ directory
    os.makedirs("verification", exist_ok=True)

    # Capture screenshot of the first tab results
    page.screenshot(path="verification/test_flow_simulation_done.png", full_page=True)

    # Navigate to the "Visual Learning" tab
    visual_tab = page.get_by_role("tab", name="🎓 Visual Learning")
    expect(visual_tab).to_be_visible()
    visual_tab.click()

    # Wait for tab content to render
    page.wait_for_selector("text=Visual Quantum Learning & Theory", timeout=10000)

    # Switch to the nested "Animations" sub-tab
    animations_tab = page.get_by_role("tab", name="🎨 Animations")
    expect(animations_tab).to_be_visible()
    animations_tab.click()

    # Verify photon transmission canvas or container is present
    page.wait_for_selector("text=Photon Transmission", timeout=10000)

    # Capture screenshot of the animations sub-tab
    page.screenshot(path="verification/test_flow_visual_learning.png", full_page=True)
