from core.stats import calculate_qber, analyze_security, generate_error_report

class SimulationEngine:
    def __init__(self, protocol, attack=None, backend=None):
        self.protocol = protocol
        self.attack = attack
        self.backend = backend

    def run(self, n, callback=None):
        def log(msg):
            if callback:
                try:
                    callback(msg)
                except Exception:
                    pass

        log(f"Initializing {self.protocol.name} simulation...")

        # 1. Alice generates bits and bases
        alice_bits = self.protocol.generate_bits(n)
        # B92 might not need bases for encoding, but we'll follow the protocol interface
        # For B92, we'll pass a dummy if needed, but BB84 needs them.
        if self.protocol.name == "BB84":
            alice_bases = self.protocol.generate_bases(n)
        else:
            alice_bases = ["B92"] * n

        log("Encoding qubits...")
        encoded_qubits = self.protocol.encode(alice_bits, alice_bases)

        # 2. Eve Attacks
        if self.attack:
            log(f"Eve applying {self.attack.__class__.__name__}...")
            intercepted_qubits = self.attack.apply(encoded_qubits, self.backend)
        else:
            intercepted_qubits = encoded_qubits

        # 3. Bob chooses bases and measures
        log("Bob measuring qubits...")
        bob_bases = self.protocol.generate_bases(n)
        bob_results = self.protocol.measure(intercepted_qubits, bob_bases, self.backend)

        # 4. Sifting
        log("Sifting keys...")
        key_a, key_b, sifted_indices = self.protocol.sift(alice_bases, bob_bases, alice_bits, bob_results)

        # 5. Error Analysis
        log("Analyzing security...")
        qber = calculate_qber(key_a, key_b)
        is_secure, security_status = analyze_security(qber)

        report = generate_error_report(alice_bits, bob_results, alice_bases, bob_bases, key_a, key_b, qber)

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
