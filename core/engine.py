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

        log(f"Initializing {self.protocol.__class__.__name__} simulation...")

        # 1. Alice generates bits
        log("Alice: Generating random bits...")
        alice_bits = self.protocol.generate_bits(n)

        # 2. Alice generates bases
        log("Alice: Choosing random bases...")
        # B92 might not use Alice bases in the same way, but let's follow the protocol's lead
        if self.protocol.__class__.__name__ == "BB84Protocol":
            alice_bases = self.protocol.generate_bases(n)
        else:
            alice_bases = ["B92"] * n

        # 3. Alice encodes
        log("Alice: Encoding bits into qubits...")
        encoded_qubits = self.protocol.encode(alice_bits, alice_bases)

        # 4. Eve Attacks (optional)
        if self.attack:
            log(f"Channel: {self.attack.__class__.__name__} attack detected...")
            intercepted_qubits = self.attack.apply(encoded_qubits, self.backend)
        else:
            log("Channel: Transmission in progress...")
            intercepted_qubits = encoded_qubits

        # 5. Bob generates bases
        log("Bob: Choosing random bases...")
        bob_bases = self.protocol.generate_bases(n)

        # 6. Bob measures
        log("Bob: Measuring received qubits...")
        bob_results = self.protocol.measure(intercepted_qubits, bob_bases, self.backend)

        # 7. Sifting
        log("Alice & Bob: Performing key sifting...")
        key_a, key_b, sifted_indices = self.protocol.sift(alice_bases, bob_bases, alice_bits, bob_results)

        # 8. Analysis
        log("Analyzing communication security...")
        qber = calculate_qber(key_a, key_b)
        is_secure, security_status = analyze_security(qber)
        report = generate_error_report(alice_bits, bob_results, alice_bases, bob_bases, key_a, key_b)

        log("Simulation complete.")

        return {
            "protocol_name": self.protocol.__class__.__name__.replace("Protocol", ""),
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
            "circuits": encoded_qubits
        }
