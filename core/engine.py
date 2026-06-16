from core.stats import calculate_qber, analyze_security, generate_error_report

class SimulationEngine:
    def __init__(self, backend=None):
        self.backend = backend

    def run(self, n, protocol, attack=None, callback=None):
        """
        Run the full QKD simulation.

        Args:
            n (int): Number of qubits to simulate.
            protocol (QKDProtocol): The protocol instance (BB84, B92).
            attack (Attack, optional): The attack model to apply.
            callback (callable, optional): A function to receive status updates.
        """
        def log(msg):
            if callback:
                try:
                    callback(msg)
                except:
                    pass

        log("Alice generating bits...")
        alice_bits = protocol.generate_bits(n)

        log("Alice generating bases...")
        # Note: B92 doesn't use Alice bases in the same way, but we keep it compatible
        if protocol.name == "BB84":
            alice_bases = protocol.generate_bases(n)
        else:
            alice_bases = ["B92"] * n

        log("Encoding qubits...")
        encoded_qubits = protocol.encode(alice_bits, alice_bases)

        if attack:
            log(f"Eve applying {attack.__class__.__name__}...")
            intercepted_qubits = attack.apply(encoded_qubits, self.backend)
        else:
            intercepted_qubits = encoded_qubits

        log("Bob generating bases and measuring...")
        bob_bases = protocol.generate_bases(n)
        bob_results = protocol.measure(intercepted_qubits, bob_bases, self.backend)

        log("Performing key sifting...")
        key_a, key_b, sifted_indices = protocol.sift(alice_bases, bob_bases, alice_bits, bob_results)

        log("Analyzing errors...")
        qber = calculate_qber(key_a, key_b)
        is_secure, security_status = analyze_security(qber)
        report = generate_error_report(alice_bits, bob_results, alice_bases, bob_bases, key_a, key_b, qber=qber)

        log("Simulation complete.")
        return {
            "protocol_name": protocol.name,
            "alice_bits": alice_bits,
            "alice_bases": alice_bases,
            "bob_bases": bob_bases,
            "bob_results": bob_results,
            "key_a": key_a,
            "key_b": key_b,
            "qber": qber,
            "report": report,
            "is_secure": is_secure,
            "security_status": security_status,
            "encoded_qubits": encoded_qubits,
            "sifted_indices": sifted_indices
        }
