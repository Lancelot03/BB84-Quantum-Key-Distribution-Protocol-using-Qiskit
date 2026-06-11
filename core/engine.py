from core.stats import calculate_qber, analyze_security, generate_error_report

class SimulationEngine:
    def __init__(self, protocol, attack=None, backend=None):
        self.protocol = protocol
        self.attack = attack
        self.backend = backend

    def run(self, n, callback=None):
        """Runs the full QKD simulation."""
        def update(msg):
            if callback:
                # callback is a function that takes the message
                try:
                    callback(msg)
                except:
                    pass

        update("Generating bits and bases...")
        alice_bits = self.protocol.generate_bits(n)

        # Protocol-agnostic basis generation
        # We try to generate bases, and use a default label if it's not applicable
        try:
             alice_bases = self.protocol.generate_alice_bases(n)
        except AttributeError:
             # Fallback to current behavior
             try:
                 alice_bases = self.protocol.generate_bases(n)
             except TypeError:
                 # Protocols that don't need bases for Alice (like B92)
                 alice_bases = ["B92"] * n

        update("Encoding qubits...")
        encoded_qubits = self.protocol.encode(alice_bits, alice_bases)

        intercepted_qubits = encoded_qubits
        if self.attack:
            update(f"Applying {self.attack.__class__.__name__} attack...")
            intercepted_qubits = self.attack.apply(encoded_qubits, self.backend)

        update("Bob measuring qubits...")
        bob_bases = self.protocol.generate_bases(n)
        bob_results = self.protocol.measure(intercepted_qubits, bob_bases, self.backend)

        update("Sifting keys...")
        key_a, key_b, sifted_indices = self.protocol.sift(alice_bases, bob_bases, alice_bits, bob_results)

        update("Analyzing results...")
        qber = calculate_qber(key_a, key_b)
        is_secure, security_status = analyze_security(qber)
        report = generate_error_report(alice_bits, bob_results, alice_bases, bob_bases, key_a, key_b, qber)

        return {
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
            "encoded_qubits": encoded_qubits,
            "intercepted_qubits": intercepted_qubits
        }
