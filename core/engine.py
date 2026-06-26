from core.stats import calculate_qber, analyze_security, generate_error_report

class SimulationEngine:
    """
    Orchestrates the end-to-end QKD simulation flow.
    """
    def __init__(self, protocol, attack=None, backend=None):
        self.protocol = protocol
        self.attack = attack
        self.backend = backend

    def run(self, n, callback=None):
        """
        Runs the simulation for n qubits.

        Args:
            n (int): Number of qubits to simulate.
            callback (callable): Optional function for real-time status updates.

        Returns:
            dict: Simulation results and metadata.
        """
        def log(msg):
            if callback:
                try:
                    callback(msg)
                except Exception:
                    # Fail silently if callback fails (e.g. UI disconnected)
                    pass

        log(f"🚀 Initializing {self.protocol.name} protocol...")

        # 1. Alice generates bits and bases
        log("📡 Alice: Generating random bits and selecting bases...")
        alice_bits = self.protocol.generate_bits(n)
        # B92 doesn't use bases for Alice in the same way, but we track it for reporting
        alice_bases = self.protocol.generate_bases(n) if self.protocol.name == "BB84" else ["B92"] * n

        # 2. Alice encodes qubits
        log("💎 Alice: Encoding bits into quantum states...")
        encoded_qubits = self.protocol.encode(alice_bits, alice_bases)

        # 3. Eve attacks (optional)
        if self.attack:
            log(f"🕵️ Eve: Applying {self.attack.__class__.__name__} attack...")
            intercepted_qubits = self.attack.apply(encoded_qubits, self.backend)
        else:
            intercepted_qubits = encoded_qubits

        # 4. Bob measures
        log("📥 Bob: Randomly selecting measurement bases and observing qubits...")
        bob_bases = self.protocol.generate_bases(n)
        bob_results = self.protocol.measure(intercepted_qubits, bob_bases, self.backend)

        # 5. Sifting
        log("🤝 Alice & Bob: Comparing bases and sifting keys...")
        key_a, key_b, sifted_indices = self.protocol.sift(alice_bases, bob_bases, alice_bits, bob_results)

        # 6. Error analysis
        log("📊 System: Analyzing Quantum Bit Error Rate (QBER)...")
        qber = calculate_qber(key_a, key_b)
        is_secure, security_status = analyze_security(qber)
        report = generate_error_report(alice_bits, bob_results, alice_bases, bob_bases, key_a, key_b)

        log("✅ Simulation complete.")

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
            "circuits": encoded_qubits
        }
