from core.bb84 import BB84Protocol

class SimulationEngine:
    def __init__(self, protocol, attack=None, backend=None):
        self.protocol = protocol
        self.attack = attack
        self.backend = backend

    def run(self, n, callback=None):
        def log(msg):
            if callback:
                try:
                    # Streamlit status update usually takes label=msg
                    callback(msg)
                except Exception:
                    pass

        log("Generating bits and bases...")
        alice_bits = self.protocol.generate_bits(n)

        # Determine Alice bases based on protocol
        if isinstance(self.protocol, BB84Protocol):
            alice_bases = self.protocol.generate_bases(n)
        else:
            # For B92 or other protocols where Alice uses a fixed/internal basis set
            alice_bases = ['B92'] * n

        log("Encoding qubits...")
        encoded_qubits = self.protocol.encode(alice_bits, alice_bases)

        log("Transmission through channel...")
        if self.attack:
            intercepted_qubits = self.attack.apply(encoded_qubits, self.backend)
        else:
            intercepted_qubits = encoded_qubits

        log("Bob measuring qubits...")
        bob_bases = self.protocol.generate_bases(n)
        bob_results = self.protocol.measure(intercepted_qubits, bob_bases, self.backend)

        log("Sifting keys...")
        # Note: we need the latest stats functions which will be updated in next steps
        from core.stats import calculate_qber, analyze_security, generate_error_report

        key_a, key_b, sifted_indices = self.protocol.sift(alice_bases, bob_bases, alice_bits, bob_results)

        log("Analyzing errors...")
        qber = calculate_qber(key_a, key_b)
        is_secure, security_status = analyze_security(qber)

        # We'll update generate_error_report to take qber explicitly in next steps
        try:
            report = generate_error_report(alice_bits, bob_results, alice_bases, bob_bases, key_a, key_b, qber=qber)
        except TypeError:
            # Fallback for old signature during transition
            report = generate_error_report(alice_bits, bob_results, alice_bases, bob_bases, key_a, key_b)

        log("Simulation complete.")

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
            "encoded_qubits": encoded_qubits
        }
