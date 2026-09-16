# Phase 1 — Clean Core BB84 Simulator

Simulate the BB84 (and B92) Quantum Key Distribution protocols to demonstrate how two parties (Alice and Bob) can generate a shared secret key securely, even when an eavesdropper (Eve) attempts to intercept communication.

## Features & Modular Architecture

### Core Engine & Protocols (`core/`)
- **Basis Generation & Encoding**: Random bit and basis selection (Z / X) with Qiskit quantum circuit encoding (`bb84.py`, `b92.py`).
- **Eavesdropper Simulation**: Attack models including Intercept-Resend, Noisy Channel, and Photon Number Splitting (`attacks.py`).
- **Key Sifting & Error Analysis**: Basis matching and Quantum Bit Error Rate (QBER) calculation with security threshold checks (`stats.py`).
- **Post-Processing**: Information reconciliation via Cascade protocol (`reconciliation.py`) and Privacy Amplification (`privacy.py`).
- **Simulation Engine**: Central orchestrator unifying simulation runs with progress callbacks (`engine.py`).

### User Interfaces & Visualizations
- **Streamlit Web Application (`app.py`)**: Real-time quantum circuit display, interactive 3D Bloch sphere rendering, photon transmission animations, and key sifting visualizations.
- **CLI Runner (`qkd_cli_runner.py`)**: Command-line interface with interactive mode and configurable simulation arguments.

![Simulation](assets/simulation.png)
![Visual Learning](assets/visual_learning.png)

## Tech Stack
- **Python 3.12**
- **Qiskit / Qiskit Aer** (Quantum circuit generation and simulation)
- **NumPy & Matplotlib** (Data processing and visualization)
- **Streamlit** (Interactive web UI)

## Installation & Usage

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Streamlit Web Application
```bash
streamlit run app.py
```

### 3. Run Command-Line Interface (CLI)
```bash
# Run standard BB84 simulation with 100 qubits and Intercept-Resend attack
python qkd_cli_runner.py -p BB84 -n 100 -e -a "Intercept-Resend" -s 0.2

# Run interactive CLI mode
python qkd_cli_runner.py -i
```

### 4. Run Test Suite
```bash
PYTHONPATH=. pytest
```
