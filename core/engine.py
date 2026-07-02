from core.stats import calculate_qber, analyze_security, generate_error_report

class SimulationEngine:
    """
    Orchestrates the QKD simulation flow, decoupling the protocol logic from the UI.
    """
    def run(self, protocol, n, attack=None, backend=None, callback=None):
        def calculate_eve_info(attack_data, protocol, alice_bits, alice_bases, bob_bases, indices):
            """Estimate how much of the sifted key Eve knows."""
            if not attack_data or not indices:
                return 0.0

            sifted_set = set(indices)
            known_bits = 0

            # Case 1: Intercept-Resend
            if "eve_bits" in attack_data and "eve_bases" in attack_data:
                eve_bits = attack_data["eve_bits"]
                eve_bases = attack_data["eve_bases"]
                for idx in indices:
                    # Eve knows the bit if she guessed the correct basis
                    if eve_bases[idx] == alice_bases[idx]:
                        known_bits += 1
                    # Even if she guessed wrong, she might get it right by luck (50%)
                    # but typically we report information gain based on basis matching

            # Case 2: PNS
            elif "eve_captured_indices" in attack_data:
                captured = set(attack_data["eve_captured_indices"])
                # In PNS, Eve knows the bit if she captured it and it's part of the sifted key
                for idx in indices:
                    if idx in captured:
                        known_bits += 1

            return (known_bits / len(indices)) if indices else 0.0

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
        attack_data = {}
        if attack:
            log(f"Applying {type(attack).__name__} attack to the channel...")
            intercepted_circuits, attack_data = attack.apply(circuits, backend)
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

        # Calculate Eve's information gain
        eve_info = calculate_eve_info(attack_data, protocol, alice_bits, alice_bases, bob_bases, indices)

        report = generate_error_report(alice_bits, bob_results, alice_bases, bob_bases, key_a, key_b, protocol_name=protocol.name)
        if report:
            report["eve_info_gain"] = eve_info

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
            "eve_info_gain": eve_info,
            "is_secure": is_secure,
            "security_status": security_status,
            "report": report,
            "alice_circuits": circuits,
            "bob_circuits": meas_circuits
        }
