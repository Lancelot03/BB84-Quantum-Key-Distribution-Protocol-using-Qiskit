# BB84 Quantum Key Distribution Simulator

An interactive and modular Quantum Key Distribution (QKD) simulator built with Python, Qiskit, and Streamlit. The simulator models quantum communication protocols (BB84 and B92), eavesdropping attacks, error analysis (QBER), information reconciliation, and privacy amplification.

![Simulation](assets/simulation.png)
![Visual Learning](assets/visual_learning.png)

---

## 🌟 Key Features & Phase 1 Highlights

- **Modular Architecture (`core/`)**: Fully decoupled quantum engine logic from frontend UI.
- **Protocol Mechanics**:
  - **BB84 & B92 Protocols**: Support for 4-state (BB84) and 2-state non-orthogonal (B92) encodings.
  - **Quantum Circuit Generation & Simulation**: Powered by Qiskit and Qiskit Aer simulator.
  - **Key Sifting**: Classical basis reconciliation to sift matching bit sequences.
  - **Error Analysis & Security Verification**: Real-time Quantum Bit Error Rate (QBER) calculation and security threshold detection (11% threshold for BB84).
  - **Post-Processing Pipeline**: Cascade Information Reconciliation for error correction and SHA-256 Privacy Amplification.
- **Eavesdropper Simulation (`attacks.py`)**:
  - **Intercept-Resend**: Eve measures and re-encodes transmitted qubits, introducing detectable QBER.
  - **Noisy Channel**: Simulates environmental channel depolarizing noise.
  - **Photon Number Splitting (PNS)**: Simulates subtle multi-photon eavesdropping.
- **Interactive Visualizations (`visuals.py`)**:
  - **3D Bloch Sphere**: Real-time rendering of qubit quantum states using Three.js and Qiskit `Statevector`.
  - **Circuit Diagrams**: Individual quantum circuit rendering for Alice's encoding and Bob's measurements.
  - **Photon Transmission Animation**: Visual simulation of quantum channel transmission and eavesdropping intervention.
  - **Basis Matching & Error Charts**: Visual representation of basis sifting and bit error distribution.

---

## 📂 Architecture Overview

```text
├── core/                   # Core QKD simulation logic (Decoupled & Testable)
│   ├── __init__.py         # Package API exports
│   ├── protocol.py         # Abstract base class for QKD protocols
│   ├── bb84.py             # BB84 protocol implementation
│   ├── b92.py              # B92 protocol implementation
│   ├── engine.py           # Simulation Engine orchestrator
│   ├── attacks.py          # Eavesdropper attack implementations
│   ├── stats.py            # QBER, security, and error report analytics
│   ├── reconciliation.py   # Cascade error correction protocol
│   └── privacy.py          # SHA-256 Privacy Amplification
├── visuals.py              # Streamlit & Three.js visualization components
├── app.py                  # Interactive Streamlit Web Interface
├── qkd_cli_runner.py       # Command-Line Interface for automated simulations
└── tests/                  # Pytest suite covering all protocols, attacks, and engine flows
```

---

## 🚀 Getting Started

### Installation

1. Clone the repository and install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Streamlit web application:
```bash
streamlit run app.py
```

### Running CLI Simulations

You can also run QKD simulations directly from the command line:

```bash
# Run a standard BB84 simulation with 100 qubits
python3 qkd_cli_runner.py --protocol BB84 --qubits 100

# Run a simulation with an Intercept-Resend attack
python3 qkd_cli_runner.py --protocol BB84 --qubits 100 --attack Intercept-Resend --noise 0.5
```

---

## 🧪 Testing

Run the automated test suite with `pytest`:

```bash
python3 -m pytest
```
