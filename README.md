# BB84 Quantum Key Distribution (QKD) Simulator - Phase 1: Clean Core

An interactive, high-fidelity educational simulator demonstrating the core principles of Quantum Key Distribution (QKD). The simulator supports end-to-end simulation of both the **BB84** and **B92** protocols, modeling eavesdropping attacks, real-time circuit generation using Qiskit, and post-processing steps (information reconciliation and privacy amplification).

---

## 🚀 Key Features

- **Modular "Clean Core" Architecture**: Strictly separates the protocol quantum logic from UI orchestrations.
- **Protocol Support**:
  - **BB84**: Standard 4-state protocol using mutually unbiased Z and X bases.
  - **B92**: 2-state protocol utilizing non-orthogonal states.
- **Eavesdropping Attack Models**:
  - **Intercept-Resend**: Eve measures intercepted qubits on a chosen basis with a tunable interception probability and resends them.
  - **Noisy Channel**: Introduces basis-independent quantum channel noise.
  - **Photon Number Splitting (PNS)**: Subtly splits multi-photon pulses to gain information without raising QBER.
- **Post-Processing (Phase 2 integration)**:
  - **Information Reconciliation (Cascade)**: Divides sifted keys into blocks and resolves discrepancies via parity-based binary search.
  - **Privacy Amplification**: Uses SHA-256 hash compression to eliminate Eve's partial information gain.
- **Pedagogical Visualizations**:
  - **3D Bloch Sphere**: Renders live qubit states on a Three.js-based 3D sphere.
  - **Real-Time Quantum Circuit Generation**: Draws exact Alice and Bob Qiskit quantum circuits side-by-side.
  - **Photon Transmission Simulation**: Animates key transit over the quantum channel.
  - **Analytical Charts**: Includes QBER distribution, bit mismatch indices, and live basis matching matrices.

---

## 📂 Project Structure

```text
├── core/                       # Clean Core Module
│   ├── __init__.py             # Exposes public API classes and methods
│   ├── protocol.py             # Abstract Base Class QKDProtocol
│   ├── bb84.py                 # BB84 encoding, measurement, and sifting
│   ├── b92.py                  # B92 encoding, measurement, and sifting
│   ├── attacks.py              # Eavesdropper attack simulation models
│   ├── engine.py               # Protocol-agnostic SimulationEngine
│   ├── stats.py                # QBER, security, and information leakage analysis
│   ├── reconciliation.py       # Cascade information reconciliation
│   └── privacy.py              # SHA-256 privacy amplification
├── tests/                      # Unit and integration test suites
│   ├── test_attacks.py
│   ├── test_b92.py
│   ├── test_bb84.py
│   ├── test_engine.py
│   └── test_post_processing.py
├── assets/                     # Diagnostic images and UI assets
├── app.py                      # Interactive Streamlit Frontend
├── visuals.py                  # Streamlit visualizations (Three.js and Matplotlib)
└── requirements.txt            # Project dependencies
```

---

## ⚙️ Installation & Usage

### 📦 Prerequisites

Ensure you have Python 3.10+ installed. Install the package dependencies using:

```bash
pip install -r requirements.txt pytest
```

### 🖥️ Run the Streamlit UI

Start the local web application on your local machine:

```bash
streamlit run app.py
```

### 🧪 Run the Test Suite

Execute the robust unit and integration tests using:

```bash
PYTHONPATH=. python3 -m pytest
```
