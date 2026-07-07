import streamlit as st
import random
from qiskit_aer import AerSimulator
try:
    from qiskit_ibm_runtime import QiskitRuntimeService
except ImportError:
    QiskitRuntimeService = None
import matplotlib.pyplot as plt
from visuals import (
    bloch_sphere,
    photon_transmission,
    basis_matching_visual,
    draw_circuit_visual,
    get_bloch_coordinates,
    plot_bit_differences,
    plot_qber_bar
)
from core import (
    BB84Protocol,
    B92Protocol,
    InterceptResend,
    NoisyChannel,
    PhotonNumberSplitting,
    SimulationEngine
)

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
        engine = SimulationEngine()

        # Initialize Protocol
        protocol = BB84Protocol() if protocol_choice == "BB84" else B92Protocol()

        # Initialize Attack
        attack = None
        if eve_present:
            if attack_choice == "Intercept-Resend":
                attack = InterceptResend()
            elif attack_choice == "Noisy Channel":
                attack = NoisyChannel(noise_level)
            else:
                attack = PhotonNumberSplitting()

        # Progress Bar and Status
        progress_bar = st.progress(0.0)

        # Run Simulation with UI status updates
        with st.status("🚀 Simulation in Progress...") as status:
            def simulation_callback(msg, progress=None):
                status.update(label=msg)
                if progress is not None:
                    progress_bar.progress(progress)

            viz_data = engine.run(
                protocol=protocol,
                n=n,
                attack=attack,
                backend=backend,
                callback=simulation_callback
            )
            status.update(label="✅ Simulation Complete!", state="complete", expanded=False)

        st.subheader("📬 Sifted Key Result")
        st.text(f"Alice's Key: {''.join(map(str, viz_data['key_a']))}")
        st.text(f"Bob's Key:   {''.join(map(str, viz_data['key_b']))}")
        st.markdown(f"### ❗ QBER: `{viz_data['qber'] * 100:.2f}%` - Status: **{viz_data['security_status']}**")

        if not viz_data['is_secure']:
            st.error("⚠️ High QBER! Potential eavesdropping detected.")
        else:
            st.success("✅ Low QBER. Communication likely secure.")

            with st.expander("🔐 Post-Processing Details (Error Correction & Privacy Amplification)"):
                st.subheader("🛠️ Information Reconciliation (Cascade)")
                st.write(f"Errors corrected by Bob: `{viz_data['report'].get('errors_fixed', 0)}` bits")
                st.text(f"Alice's Reconciled Key: {''.join(map(str, viz_data['key_a']))}")
                st.text(f"Bob's Reconciled Key:   {''.join(map(str, viz_data['reconciled_key_b']))}")

                st.subheader("🛡️ Privacy Amplification")
                st.write(f"Key compressed by factor of: `{viz_data['report'].get('final_key_length', 0) / len(viz_data['key_a']) if len(viz_data['key_a']) > 0 else 0:.2f}`")
                st.markdown(f"**Final Shared Secret Key (Alice):**")
                st.code(''.join(map(str, viz_data['final_key_a'])))
                st.markdown(f"**Final Shared Secret Key (Bob):**")
                st.code(''.join(map(str, viz_data['final_key_b'])))

                if viz_data['final_key_a'] == viz_data['final_key_b']:
                    st.success("✅ Perfect Key Match!")
                else:
                    st.error("❌ Key Mismatch! Reconciliation failed.")

        # Real-time Circuit Display
        st.subheader("🛠️ Real-time Quantum Circuit & State Visualization")

        for i in range(min(3, n)):
            st.markdown(f"#### Qubit {i}")
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                st.markdown(f"**Alice's Encoding** (Basis: {viz_data['alice_bases'][i]}, Bit: {viz_data['alice_bits'][i]})")
                st.pyplot(draw_circuit_visual(viz_data['alice_circuits'][i]))
                coords = get_bloch_coordinates(viz_data['alice_circuits'][i])
                bloch_sphere(coords, height=300)
            with col_c2:
                st.markdown(f"**Bob's Measurement** (Basis: {viz_data['bob_bases'][i]})")
                st.pyplot(draw_circuit_visual(viz_data['bob_circuits'][i]))
                coords = get_bloch_coordinates(viz_data['bob_circuits'][i])
                bloch_sphere(coords, height=300)

        with st.expander("🛠️ Quantum Circuit Preview (First 10 Qubits)"):
            for i in range(min(10, n)):
                st.write(f"### Qubit {i}")
                st.write(f"**Alice Basis:** {viz_data['alice_bases'][i]}, **Alice Bit:** {viz_data['alice_bits'][i]}")
                st.write(f"**Bob Basis:** {viz_data['bob_bases'][i]}")
                col_i1, col_i2 = st.columns(2)
                with col_i1:
                    st.markdown("*Encoding:*")
                    st.pyplot(viz_data['alice_circuits'][i].draw('mpl'))
                with col_i2:
                    st.markdown("*Measurement:*")
                    st.pyplot(viz_data['bob_circuits'][i].draw('mpl'))

        if viz_data['report']:
            st.subheader("📊 Detailed Error Analysis")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Sifting Efficiency", f"{viz_data['report']['basis_match_efficiency']:.1f}%")
            col2.metric("Z-Basis Error", f"{viz_data['report']['z_error_rate']*100:.1f}%")
            col3.metric("X-Basis Error", f"{viz_data['report']['x_error_rate']*100:.1f}%")
            col4.metric("Info Leakage", f"{viz_data['report']['info_leakage']*100:.1f}%")

            if viz_data['is_secure']:
                st.subheader("🛡️ Security Performance")
                m1, m2, m3 = st.columns(3)
                m1.metric("Final Key Length", f"{viz_data['report']['final_key_length']} bits")
                m2.metric("Secret Key Rate", f"{viz_data['report']['secret_key_rate']*100:.1f}%")
                m3.metric("Errors Fixed", f"{viz_data['report']['errors_fixed']}")

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
        st.subheader("BB84 Protocol: Mutually Unbiased Bases")
        st.write("In BB84, we use two mutually unbiased bases to encode bits into quantum states:")
        st.latex(r"Z\text{-basis: } \{|0\rangle, |1\rangle\} \quad X\text{-basis: } \{|+\rangle, |-\rangle\}")
        st.write("Alice randomly chooses a bit (0 or 1) and a basis (Z or X). Bob also chooses a basis at random to measure. If their bases match, Bob gets the correct bit.")

        st.subheader("B92 Protocol: Non-Orthogonal States")
        st.write("B92 uses only two non-orthogonal states for encoding:")
        st.latex(r"\text{Bit 0: } |0\rangle \quad \text{Bit 1: } |+\rangle = \frac{|0\rangle + |1\rangle}{\sqrt{2}}")
        st.write("Bob chooses to measure in either the X-basis or the Z-basis. A conclusive result (measuring '1') only happens if his basis is different from Alice's encoding.")

        st.subheader("Quantum Bit Error Rate (QBER)")
        st.write("The security of QKD relies on detecting errors introduced by an eavesdropper. QBER is defined as:")
        st.latex(r"QBER = \frac{\text{Number of mismatched bits}}{\text{Total compared bits}}")
        st.write(r"Typically, if $QBER > 11\%$ in BB84, the key is considered compromised. Eavesdropping necessarily introduces errors due to the No-Cloning Theorem.")

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
