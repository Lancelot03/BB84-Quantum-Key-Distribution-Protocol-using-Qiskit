from qiskit_aer import AerSimulator
from core.stats import calculate_qber, analyze_security, generate_error_report

class SimulationEngine:
    def run(self, protocol, n, attack=None, backend=None, callback=None):
        if backend is None:
            backend = AerSimulator()

        def log(msg):
            if callback:
                try:
                    callback(msg)
                except Exception:
                    pass

        log("Generating bits and bases...")
        alice_bits = protocol.generate_bits(n)
        alice_bases = protocol.generate_bases(n) if protocol.name == "BB84" else ["B92"] * n

        log("Encoding qubits...")
        encoded_qubits = protocol.encode(alice_bits, alice_bases)

        log("Channel transmission...")
        if attack:
            log(f"Applying {attack.__class__.__name__} attack...")
            intercepted_qubits = attack.apply(encoded_qubits, backend)
        else:
            intercepted_qubits = encoded_qubits

        log("Bob measuring...")
        bob_bases = protocol.generate_bases(n)
        bob_results = protocol.measure(intercepted_qubits, bob_bases, backend)

        log("Sifting keys...")
        key_a, key_b, sifted_indices = protocol.sift(alice_bases, bob_bases, alice_bits, bob_results)

        log("Analyzing security...")
        qber = calculate_qber(key_a, key_b)
        is_secure, security_status = analyze_security(qber)
        report = generate_error_report(alice_bits, bob_results, alice_bases, bob_bases, qber)

        log("Simulation complete.")

        return {
            "protocol_name": protocol.name,
            "alice_bits": alice_bits,
            "alice_bases": alice_bases,
            "bob_bases": bob_bases,
            "bob_results": bob_results,
            "key_a": key_a,
            "key_b": key_b,
            "indices": sifted_indices,
            "qber": qber,
            "is_secure": is_secure,
            "security_status": security_status,
            "report": report,
            "circuits": encoded_qubits # Return original circuits for visualization
        }
