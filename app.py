import streamlit as st
import random
from qiskit_aer import AerSimulator
try:
    from qiskit_ibm_runtime import QiskitRuntimeService
except ImportError:
    QiskitRuntimeService = None
import matplotlib.pyplot as plt
from visuals import bloch_sphere, photon_transmission, basis_matching_visual, draw_circuit_visual
from core import BB84Protocol, B92Protocol, InterceptResend, NoisyChannel, PhotonNumberSplitting, SimulationEngine

# --- Quantum Logic Functions ---

def get_backend(use_hardware=False, api_key=""):
    if use_hardware and api_key:
        try:
            service = QiskitRuntimeService(channel="ibm_quantum", token=api_key)
            backend = service.least_busy(operational=True, simulator=False)
            st.sidebar.success(f"Connected to hardware: {backend.name}")
            return backend
        except Exception as e:
            st.sidebar.error(f"Error connecting to IBM: {e}")
            return AerSimulator()
    else:
        return AerSimulator()

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

# Sidebar for Hardware Settings
st.sidebar.title("🛠️ Settings")
protocol_choice = st.sidebar.selectbox("Select Protocol", ["BB84", "B92"])
use_real_hardware = st.sidebar.checkbox("Use Real Quantum Hardware (IBM)?", value=False)
ibm_api_key = st.sidebar.text_input("IBM Quantum API Key", type="password", disabled=not use_real_hardware)

st.title("🔐 Quantum Key Distribution Simulator")

tab1, tab2 = st.tabs(["🚀 Simulation", "🎓 Visual Learning"])

with tab1:
    col_a, col_b = st.columns(2)
    with col_a:
        n = st.slider("Select number of qubits", min_value=10, max_value=200, value=100, step=10)
        eve_present = st.checkbox("Simulate Eavesdropper (Eve)?", value=True)

    with col_b:
        attack_choice = st.selectbox("Attack Model", ["Intercept-Resend", "Noisy Channel", "Photon Number Splitting"], disabled=not eve_present)
        noise_level = st.slider("Channel Noise / Attack Strength", 0.0, 0.5, 0.1, disabled=(not eve_present or attack_choice == "Photon Number Splitting"))

    if st.button("Run Simulation"):
        backend = get_backend(use_real_hardware, ibm_api_key)

        # Initialize Protocol
        protocol = BB84Protocol() if protocol_choice == "BB84" else B92Protocol()

        # Eve Attacks
        attack = None
        if eve_present:
            if attack_choice == "Intercept-Resend":
                attack = InterceptResend()
            elif attack_choice == "Noisy Channel":
                attack = NoisyChannel(noise_level)
            else:
                attack = PhotonNumberSplitting()

        # Run Engine with st.status
        with st.status("Simulating QKD...", expanded=True) as status:
            engine = SimulationEngine()
            viz_data = engine.run(
                protocol=protocol,
                n=n,
                attack=attack,
                backend=backend,
                callback=lambda msg: status.update(label=msg)
            )
            status.update(label="Simulation Complete!", state="complete", expanded=False)

        st.subheader("📬 Sifted Key Result")
        st.text(f"Alice's Key: {''.join(map(str, viz_data['key_a']))}")
        st.text(f"Bob's Key:   {''.join(map(str, viz_data['key_b']))}")
        st.markdown(f"### ❗ QBER: `{viz_data['qber'] * 100:.2f}%` - Status: **{viz_data['security_status']}**")

        if not viz_data['is_secure']:
            st.error("⚠️ High QBER! Potential eavesdropping detected.")
        else:
            st.success("✅ Low QBER. Communication likely secure.")

        # Real-time Circuit Display
        st.subheader("🛠️ Quantum Circuit (First Qubit)")
        st.pyplot(draw_circuit_visual(viz_data['circuits'][0]))

        with st.expander("🛠️ Quantum Circuit Preview (First 5 Qubits)"):
            for i in range(min(5, n)):
                st.write(f"Qubit {i} (Basis: {viz_data['alice_bases'][i]}, Bit: {viz_data['alice_bits'][i]})")
                st.pyplot(viz_data['circuits'][i].draw('mpl'))

        if viz_data['report']:
            st.subheader("📊 Detailed Error Analysis")
            col1, col2, col3 = st.columns(3)
            col1.metric("Sifting Efficiency", f"{viz_data['report']['basis_match_efficiency']:.1f}%")
            col2.metric("Z-Basis Error Rate", f"{viz_data['report']['z_error_rate']*100:.1f}%")
            col3.metric("X-Basis Error Rate", f"{viz_data['report']['x_error_rate']*100:.1f}%")

        st.subheader("🔍 Basis Matching")
        basis_matching_visual(viz_data['alice_bases'][:20], viz_data['bob_bases'][:20])

        st.subheader("🔍 Bit Differences")
        st.pyplot(plot_bit_differences(viz_data['key_a'], viz_data['key_b']))

        st.subheader("📊 QBER Distribution")
        st.pyplot(plot_qber_bar(viz_data['qber']))

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
