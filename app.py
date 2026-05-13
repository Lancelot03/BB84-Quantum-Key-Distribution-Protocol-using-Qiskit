import streamlit as st
import random
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
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

def eve_intercept(circuits):
    backend = Aer.get_backend('qasm_simulator')
    eve_bases = [random.choice(['Z', 'X']) for _ in range(len(circuits))]
    new_circuits = []

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
    return new_circuits

def measure_qubits(circuits, bob_bases):
    backend = Aer.get_backend('qasm_simulator')
    results = []
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

# --- Streamlit App ---
st.set_page_config(page_title="Quantum Key Distribution Simulator", layout="wide")
st.title("🔐 BB84 Quantum Key Distribution Simulator")

tab1, tab2 = st.tabs(["🚀 Simulation", "🎓 Visual Learning"])

with tab1:
    n = st.slider("Select number of qubits", min_value=10, max_value=200, value=100, step=10)
    eve_present = st.checkbox("Simulate Eavesdropper (Eve)?", value=True)

    if st.button("Run Simulation"):
        st.info("Running QKD simulation...")
        alice_bits, alice_bases = create_bits_bases(n)
        bob_bases = [random.choice(['Z', 'X']) for _ in range(n)]

        encoded = encode_qubits(alice_bits, alice_bases)

        if eve_present:
            intercepted = eve_intercept(encoded)
        else:
            intercepted = encoded

        bob_results = measure_qubits(intercepted, bob_bases)
        key_a, key_b = sift_keys(alice_bases, bob_bases, alice_bits, bob_results)
        qber = calculate_qber(key_a, key_b)

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
    st.header("Visual Quantum Learning")

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
