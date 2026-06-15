from core.stats import calculate_qber, analyze_security, generate_error_report

class SimulationEngine:
    def __init__(self, protocol, backend=None):
        self.protocol = protocol
        self.backend = backend

    def run(self, n_qubits, attack=None, callback=None):
        def log(msg):
            if callback:
                try:
                    callback(msg)
                except Exception:
                    pass

        log(f"Initializing {self.protocol.name} simulation...")

        # 1. Generate bits
        log("Generating random bits...")
        alice_bits = self.protocol.generate_bits(n_qubits)

        # 2. Generate bases (Alice)
        log("Generating Alice's bases...")
        if self.protocol.name == "BB84":
            alice_bases = self.protocol.generate_bases(n_qubits)
        else:
            # B92 uses a fixed label or logic in stats
            alice_bases = ["B92"] * n_qubits

        # 3. Encode
        log("Encoding bits into quantum states...")
        encoded_qubits = self.protocol.encode(alice_bits, alice_bases)

        # 4. Attack
        if attack:
            log(f"Applying {attack.__class__.__name__} attack...")
            intercepted_qubits = attack.apply(encoded_qubits, self.backend)
        else:
            intercepted_qubits = encoded_qubits

        # 5. Bob's bases
        log("Generating Bob's measurement bases...")
        bob_bases = self.protocol.generate_bases(n_qubits)

        # 6. Measure
        log("Measuring qubits...")
        bob_results = self.protocol.measure(intercepted_qubits, bob_bases, self.backend)

        # 7. Sifting
        log("Sifting keys...")
        key_a, key_b, sifted_indices = self.protocol.sift(alice_bases, bob_bases, alice_bits, bob_results)

        # 8. Analysis
        log("Performing error analysis...")
        qber = calculate_qber(key_a, key_b)
        is_secure, security_status = analyze_security(qber)
        report = generate_error_report(alice_bits, bob_results, alice_bases, bob_bases, key_a, key_b, qber)

        log("Simulation complete.")

        return {
            "protocol_name": self.protocol.name,
            "alice_bits": alice_bits,
            "alice_bases": alice_bases,
            "bob_bases": bob_bases,
            "bob_results": bob_results,
            "key_a": key_a,
            "key_b": key_b,
            "sifted_indices": sifted_indices,
            "qber": qber,
            "report": report,
            "is_secure": is_secure,
            "security_status": security_status,
            "encoded_qubits": encoded_qubits
        }
