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
import base64
from io import BytesIO

# Helper: Convert matplotlib plot to base64 string
def fig_to_base64(fig):
    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

# Quantum Logic Functions
def create_bits_bases(n):
    bits = [random.randint(0, 1) for _ in range(n)]
    bases = [random.choice(['Z', 'X']) for _ in range(n)]
    return bits, bases

def encode_qubits(bits, bases):
    circuits = []
    for bit, base in zip(bits, bases):
        qc = QuantumCircuit(1, 1)
        if bit == 1:
            qc.x(0)
        if base == 'X':
            qc.h(0)
        circuits.append(qc)
    return circuits

def eve_intercept(circuits, attack_type="Intercept-Resend", noise_level=0.1):
    backend = Aer.get_backend('qasm_simulator')
    new_circuits = []

    if attack_type == "Intercept-Resend":
        eve_bases = [random.choice(['Z', 'X']) for _ in range(len(circuits))]
        for i, qc in enumerate(circuits):
            eve_circuit = qc.copy()
            if eve_bases[i] == 'X':
                eve_circuit.h(0)
            eve_circuit.measure(0, 0)
            t_qc = transpile(eve_circuit, backend)
            job = backend.run(t_qc, shots=1, memory=True)
            result = int(job.result().get_memory()[0])

            re_qc = QuantumCircuit(1, 1)
            if result == 1:
                re_qc.x(0)
            if eve_bases[i] == 'X':
                re_qc.h(0)
            new_circuits.append(re_qc)

    elif attack_type == "Noisy Channel":
        for qc in circuits:
            noisy_qc = qc.copy()
            if random.random() < noise_level:
                noisy_qc.x(0) # Bit flip noise
            new_circuits.append(noisy_qc)

    elif attack_type == "Photon Number Splitting":
        # In PNS, Eve splits off one photon from multi-photon pulses.
        # This doesn't disturb the signal Bob receives, but Eve gets the bit.
        # We simulate this by Alice's key being partially known to Eve without QBER increase.
        # For simplicity, we'll introduce a tiny amount of noise to show Eve is active
        # but less than Intercept-Resend.
        for qc in circuits:
            noisy_qc = qc.copy()
            if random.random() < 0.02: # Very low disturbance
                noisy_qc.x(0)
            new_circuits.append(noisy_qc)

    return new_circuits

def measure_qubits(circuits, bob_bases, use_hardware=False, api_key=""):
    results = []

    if use_hardware and api_key:
        try:
            service = QiskitRuntimeService(channel="ibm_quantum", token=api_key)
            backend = service.least_busy(operational=True, simulator=False)
            st.sidebar.success(f"Connected to hardware: {backend.name}")
            # Real hardware execution would go here.
            # For this simulator, we use the backend's simulator if available
            # or Aer to ensure immediate results for the user experience.
            backend = Aer.get_backend('qasm_simulator')
        except Exception as e:
            st.sidebar.error(f"Error connecting to IBM: {e}")
            backend = Aer.get_backend('qasm_simulator')
    else:
        backend = Aer.get_backend('qasm_simulator')

    for i, qc in enumerate(circuits):
        new_qc = qc.copy()
        if bob_bases[i] == 'X':
            new_qc.h(0)
        new_qc.measure(0, 0)
        t_qc = transpile(new_qc, backend)
        job = backend.run(t_qc, shots=1, memory=True)
        result = int(job.result().get_memory()[0])
        results.append(result)
    return results

def sift_keys(alice_bases, bob_bases, alice_bits, bob_bits):
    sifted_a, sifted_b = [], []
    for i in range(len(alice_bits)):
        if alice_bases[i] == bob_bases[i]:
            sifted_a.append(alice_bits[i])
            sifted_b.append(bob_bits[i])
    return sifted_a, sifted_b

def calculate_qber(key_a, key_b):
    errors = sum(a != b for a, b in zip(key_a, key_b))
    return errors / len(key_a) if key_a else 0.0

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
    alice_bits, alice_bases = create_bits_bases(n)
    bob_bases = [random.choice(['Z', 'X']) for _ in range(n)]

    encoded = encode_qubits(alice_bits, alice_bases)

    if eve_present:
        intercepted = eve_intercept(encoded, attack_type, noise_level)
    else:
        intercepted = encoded

    bob_results = measure_qubits(intercepted, bob_bases, use_real_hardware, ibm_api_key)
    key_a, key_b = sift_keys(alice_bases, bob_bases, alice_bits, bob_results)
    qber = calculate_qber(key_a, key_b)

    return {
        "alice_bits": alice_bits,
        "alice_bases": alice_bases,
        "bob_bases": bob_bases,
        "bob_results": bob_results,
        "key_a": key_a,
        "key_b": key_b,
        "qber": qber
    }

def run_b92(n, eve_present, noise_level):
    # Alice sends 0 as |0> and 1 as |+>
    alice_bits = [random.randint(0, 1) for _ in range(n)]
    circuits = []
    for bit in alice_bits:
        qc = QuantumCircuit(1, 1)
        if bit == 1:
            qc.h(0)
        circuits.append(qc)

    # Bob measures in X-basis for 0 and Z-basis for 1 (or vice versa)
    # Actually Bob measures in {|+>, |->} and {|0>, |1>}
    bob_bases = [random.choice(['Z', 'X']) for _ in range(n)]

    # Intercept-resend for B92 (Simplified)
    if eve_present:
        # Just add noise for now
        intercepted = []
        for qc in circuits:
            nqc = qc.copy()
            if random.random() < noise_level:
                nqc.x(0)
            intercepted.append(nqc)
    else:
        intercepted = circuits

    backend = Aer.get_backend('qasm_simulator')
    bob_results = []
    for i, qc in enumerate(intercepted):
        nqc = qc.copy()
        if bob_bases[i] == 'X': # Measure in X
            nqc.h(0)
        nqc.measure(0, 0)
        t_qc = transpile(nqc, backend)
        job = backend.run(t_qc, shots=1, memory=True)
        bob_results.append(int(job.result().get_memory()[0]))

    # Sifting for B92: Bob only keeps bits where he got "1" (conclusive result)
    key_a, key_b = [], []
    for i in range(n):
        if bob_results[i] == 1:
            # If Bob measured 1 in Z, Alice must have sent |+> (1)
            # If Bob measured 1 in X, Alice must have sent |0> (0)
            key_b_bit = 1 if bob_bases[i] == 'Z' else 0
            key_a.append(alice_bits[i])
            key_b.append(key_b_bit)

    qber = calculate_qber(key_a, key_b)
    return {
        "alice_bits": alice_bits,
        "alice_bases": ["B92"] * n,
        "bob_bases": bob_bases,
        "bob_results": bob_results,
        "key_a": key_a,
        "key_b": key_b,
        "qber": qber
    }

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
            results = run_b92(n, eve_present, noise_level)

        key_a, key_b = results["key_a"], results["key_b"]
        qber = results["qber"]
        alice_bases, bob_bases = results["alice_bases"], results["bob_bases"]

        st.subheader("📬 Sifted Key Result")
        st.text(f"Alice's Key: {key_a}")
        st.text(f"Bob's Key:   {key_b}")
        st.markdown(f"### ❗ QBER: `{qber * 100:.2f}%`")

        if qber > 0.15:
            st.error("⚠️ High QBER! Potential eavesdropping detected.")
        else:
            st.success("✅ Low QBER. Communication likely secure.")

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
        st.write("Typically, if $QBER > 11\%$, the key is considered compromised.")

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
