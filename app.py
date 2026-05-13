import streamlit as st
import random
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
try:
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
except ImportError:
    QiskitRuntimeService = None
import matplotlib.pyplot as plt
from visuals import bloch_sphere, photon_transmission, basis_matching_visual
from core import bb84, b92, attacks, metrics
import base64
from io import BytesIO

# Helper: Convert matplotlib plot to base64 string
def fig_to_base64(fig):
    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

# Plotting Functions
def plot_bit_differences(key_a, key_b):
    diffs = [int(a != b) for a, b in zip(key_a, key_b)]
    fig, ax = plt.subplots(figsize=(10, 2))
    ax.plot(diffs, marker='o', color='red', label='Mismatch')
    ax.set_title('Bit Differences (1 = Error)')
    ax.set_xlabel('Bit Index')
    ax.set_ylabel('Difference')
    ax.grid(True)
    return fig

def plot_qber_bar(qber):
    fig, ax = plt.subplots()
    correct = 100 * (1 - qber)
    incorrect = 100 * qber
    ax.bar(['Correct', 'Incorrect'], [correct, incorrect], color=['green', 'red'])
    ax.set_title(f'QBER: {qber * 100:.2f}%')
    ax.set_ylim(0, 100)
    return fig

# --- Protocols ---
def run_bb84(n, eve_present, attack_type, noise_level, use_real_hardware, ibm_api_key):
    alice_bits, alice_bases = bb84.generate_alice_bits_and_bases(n)
    bob_bases = bb84.generate_bob_bases(n)

    encoded_circuits = bb84.encode_qubits(alice_bits, alice_bases)

    if eve_present:
        if attack_type == "Intercept-Resend":
            intercepted_circuits, _ = attacks.intercept_resend(encoded_circuits)
        elif attack_type == "Noisy Channel":
            intercepted_circuits = attacks.noisy_channel(encoded_circuits, noise_level)
        elif attack_type == "Photon Number Splitting":
            intercepted_circuits = attacks.photon_number_splitting(encoded_circuits)
        else:
            intercepted_circuits = encoded_circuits
    else:
        intercepted_circuits = encoded_circuits

    # Backend selection logic simplified for simulation
    backend = Aer.get_backend('qasm_simulator')
    if use_real_hardware and ibm_api_key and QiskitRuntimeService:
        try:
            service = QiskitRuntimeService(channel="ibm_quantum", token=ibm_api_key)
            backend = service.least_busy(operational=True, simulator=False)
            st.sidebar.success(f"Connected to hardware: {backend.name}")
        except Exception as e:
            st.sidebar.error(f"Error connecting to IBM: {e}")

    bob_results = bb84.measure_qubits(intercepted_circuits, bob_bases, backend=backend)
    key_a, key_b, _ = bb84.sift_keys(alice_bases, bob_bases, alice_bits, bob_results)
    qber = metrics.calculate_qber(key_a, key_b)

    # Generate detailed report
    report = metrics.generate_error_report(alice_bits, bob_results, alice_bases, bob_bases, key_a, key_b)

    return {
        "alice_bits": alice_bits,
        "alice_bases": alice_bases,
        "bob_bases": bob_bases,
        "bob_results": bob_results,
        "key_a": key_a,
        "key_b": key_b,
        "qber": qber,
        "report": report,
        "circuits": encoded_circuits[:5] # Return a few circuits for visualization
    }

def run_b92_simulation(n, eve_present, noise_level):
    return b92.run_b92(n, eve_present, noise_level)

# --- Streamlit App ---
st.set_page_config(page_title="Quantum Key Distribution Simulator", layout="wide")

# Sidebar for Hardware Settings
st.sidebar.title("🛠️ Settings")
protocol = st.sidebar.selectbox("Select Protocol", ["BB84", "B92"])
use_real_hardware = st.sidebar.checkbox("Use Real Quantum Hardware (IBM)?", value=False)
ibm_api_key = st.sidebar.text_input("IBM Quantum API Key", type="password", disabled=not use_real_hardware)

st.title("🔐 BB84 Quantum Key Distribution Simulator")

tab1, tab2 = st.tabs(["🚀 Simulation", "🎓 Visual Learning"])

with tab1:
    col_a, col_b = st.columns(2)
    with col_a:
        n = st.slider("Select number of qubits", min_value=10, max_value=200, value=100, step=10)
        eve_present = st.checkbox("Simulate Eavesdropper (Eve)?", value=True)

    with col_b:
        attack_type = st.selectbox("Attack Model", ["Intercept-Resend", "Noisy Channel", "Photon Number Splitting"], disabled=not eve_present)
        noise_level = st.slider("Channel Noise / Attack Strength", 0.0, 0.5, 0.1, disabled=(not eve_present or attack_type == "Photon Number Splitting"))

    if st.button("Run Simulation"):
        st.info(f"Running {protocol} simulation with {attack_type if eve_present else 'no'} intervention...")

        if protocol == "BB84":
            results = run_bb84(n, eve_present, attack_type, noise_level, use_real_hardware, ibm_api_key)
        else:
            results = run_b92_simulation(n, eve_present, noise_level)

        key_a, key_b = results["key_a"], results["key_b"]
        qber = results["qber"]
        alice_bases, bob_bases = results["alice_bases"], results["bob_bases"]
        report = results.get("report")

        st.subheader("📬 Sifted Key Result")
        st.text(f"Alice's Key: {key_a}")
        st.text(f"Bob's Key:   {key_b}")
        st.markdown(f"### ❗ QBER: `{qber * 100:.2f}%`")

        if qber > 0.15:
            st.error("⚠️ High QBER! Potential eavesdropping detected.")
        else:
            st.success("✅ Low QBER. Communication likely secure.")

        if "circuits" in results:
            with st.expander("🛠️ Quantum Circuit Preview (First 5 Qubits)"):
                for i, qc in enumerate(results["circuits"]):
                    st.write(f"Qubit {i} (Basis: {alice_bases[i]}, Bit: {results['alice_bits'][i]})")
                    st.pyplot(qc.draw('mpl'))

        if report:
            st.subheader("📊 Detailed Error Analysis")
            col1, col2, col3 = st.columns(3)
            col1.metric("Basis Matching Efficiency", f"{report['basis_match_efficiency']:.1f}%")
            col2.metric("Z-Basis Error Rate", f"{report['z_error_rate']*100:.1f}%")
            col3.metric("X-Basis Error Rate", f"{report['x_error_rate']*100:.1f}%")

        st.subheader("🔍 Basis Matching")
        basis_matching_visual(alice_bases[:20], bob_bases[:20])

        st.subheader("🔍 Bit Differences")
        st.pyplot(plot_bit_differences(key_a, key_b))

        st.subheader("📊 QBER Distribution")
        st.pyplot(plot_qber_bar(qber))

with tab2:
    st.header("Visual Quantum Learning & Theory")

    theory_tab, visual_tab = st.tabs(["📖 Mathematical Core", "🎨 Animations"])

    with theory_tab:
        st.subheader("Quantum States & Bases")
        st.write("In BB84, we use two mutually unbiased bases:")
        st.latex(r"Z\text{-basis: } \{|0\rangle, |1\rangle\} \quad X\text{-basis: } \{|+\rangle, |-\rangle\}")
        st.write("Where:")
        st.latex(r"|+\rangle = \frac{|0\rangle + |1\rangle}{\sqrt{2}}, \quad |-\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}}")

        st.subheader("Quantum Bit Error Rate (QBER)")
        st.write("The security of BB84 relies on detecting errors introduced by an eavesdropper. QBER is defined as:")
        st.latex(r"QBER = \frac{\text{Number of mismatched bits}}{\text{Total compared bits}}")
        st.write(r"Typically, if $QBER > 11\%$, the key is considered compromised.")

    with visual_tab:
        st.subheader("1. Qubit States & Bloch Sphere")
        st.write("In the BB84 protocol, Alice encodes bits into qubits using two different bases: Z-basis (|0>, |1>) and X-basis (|+>, |->).")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("**State |0>** (Z-basis)")
            bloch_sphere(state_vector=[0, 0, 1], height=300)
        with col2:
            st.markdown("**State |1>** (Z-basis)")
            bloch_sphere(state_vector=[0, 0, -1], height=300)
        with col3:
            st.markdown("**State |+>** (X-basis)")
            bloch_sphere(state_vector=[1, 0, 0], height=300)
        with col4:
            st.markdown("**State |->** (X-basis)")
            bloch_sphere(state_vector=[-1, 0, 0], height=300)

        st.subheader("2. Photon Transmission")
        st.write("Alice sends qubits (photons) to Bob. If Eve is present, she might intercept and measure them, which introduces errors.")
        photon_transmission(n_photons=8)

        st.subheader("3. Live Basis Matching")
        st.write("After transmission, Alice and Bob announce their bases. They keep bits only where their bases matched.")
        basis_matching_visual(['Z', 'X', 'Z', 'Z', 'X', 'Z', 'X', 'X', 'Z', 'X'],
                              ['Z', 'Z', 'Z', 'X', 'X', 'Z', 'X', 'Z', 'Z', 'Z'])
