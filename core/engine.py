from core.stats import calculate_qber, analyze_security, generate_error_report

class SimulationEngine:
    """
    Orchestrates the QKD simulation flow, decoupling the protocol logic from the UI.
    """
    def run(self, protocol, n, attack=None, backend=None, callback=None):
        def log(msg):
            if callback:
                try:
                    # Streamlit status.update only accepts keyword arguments for label
                    # But we try to handle general callbacks here
                    callback(msg)
                except Exception:
                    pass

        log(f"Initializing {protocol.name} simulation with {n} qubits...")

        # Alice's side: bit and basis generation
        alice_bits = protocol.generate_bits(n)
        alice_bases = protocol.generate_alice_bases(n)

        # Encoding into quantum circuits
        circuits = protocol.encode(alice_bits, alice_bases)
        log("Quantum states encoded.")

        # Optional Eavesdropper/Channel Attack
        eve_info_gain = 0
        if attack:
            log(f"Applying {type(attack).__name__} attack to the channel...")
            intercepted_circuits, intercepted_info = attack.apply(circuits, backend)
            eve_info_gain = intercepted_info.get('info_gain', 0)
        else:
            intercepted_circuits = circuits

        # Bob's side: basis generation and measurement
        bob_bases = protocol.generate_bases(n)
        log("Bob is measuring the received qubits...")
        bob_results, meas_circuits = protocol.measure(intercepted_circuits, bob_bases, backend)

        # Sifting process (reconciling keys over classical channel)
        log("Performing key sifting...")
        key_a, key_b, indices = protocol.sift(alice_bases, bob_bases, alice_bits, bob_results)

        # Error analysis and security verification
        log("Analyzing Quantum Bit Error Rate (QBER)...")
        qber = calculate_qber(key_a, key_b)
        is_secure, security_status = analyze_security(qber)
        report = generate_error_report(
            alice_bits,
            bob_results,
            alice_bases,
            bob_bases,
            key_a,
            key_b,
            qber,
            protocol.name
        )

        log("Simulation complete.")
        return {
            "protocol_name": protocol.name,
            "alice_bits": alice_bits,
            "alice_bases": alice_bases,
            "bob_bases": bob_bases,
            "bob_results": bob_results,
            "key_a": key_a,
            "key_b": key_b,
            "indices": indices,
            "qber": qber,
            "is_secure": is_secure,
            "security_status": security_status,
            "report": report,
            "alice_circuits": circuits,
            "bob_circuits": meas_circuits,
            "eve_info_gain": eve_info_gain
        }
