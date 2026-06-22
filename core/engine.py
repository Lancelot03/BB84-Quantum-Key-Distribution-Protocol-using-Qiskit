from core.stats import calculate_qber, analyze_security, generate_error_report

class SimulationEngine:
    def __init__(self, protocol, attack=None):
        self.protocol = protocol
        self.attack = attack

    def run(self, n, backend=None, callback=None):
        def log(msg):
            if callback:
                try:
                    callback(msg)
                except:
                    pass

        # 1. Generation
        log(f"Generating {n} random bits and bases...")
        alice_bits = self.protocol.generate_bits(n)
        if self.protocol.name == "BB84":
            alice_bases = self.protocol.generate_bases(n)
        else:
            alice_bases = ["B92"] * n

        # 2. Encoding
        log("Encoding bits into quantum circuits...")
        encoded_qubits = self.protocol.encode(alice_bits, alice_bases)

        # 3. Attack (Optional)
        if self.attack:
            log(f"Applying {type(self.attack).__name__} attack...")
            intercepted_qubits = self.attack.apply(encoded_qubits, backend)
        else:
            intercepted_qubits = encoded_qubits

        # 4. Bob's Measurement
        log("Bob is generating bases and measuring...")
        bob_bases = self.protocol.generate_bases(n)
        bob_results = self.protocol.measure(intercepted_qubits, bob_bases, backend)

        # 5. Sifting
        log("Sifting keys and performing error analysis...")
        key_a, key_b, sifted_indices = self.protocol.sift(alice_bases, bob_bases, alice_bits, bob_results)

        # 6. Analysis
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
            "indices": sifted_indices,
            "qber": qber,
            "is_secure": is_secure,
            "security_status": security_status,
            "report": report,
            "circuits": encoded_qubits # For visualization
        }
