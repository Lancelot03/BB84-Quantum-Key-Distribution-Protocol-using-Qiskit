from core import stats

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
                except:
                    pass

        log("Generating Alice's bits and bases...")
        alice_bits = self.protocol.generate_bits(n)
        alice_bases = self.protocol.generate_alice_bases(n)

        log("Encoding bits into quantum circuits...")
        encoded_qubits = self.protocol.encode(alice_bits, alice_bases)

        if self.attack:
            log(f"Applying {self.attack.__class__.__name__} attack...")
            intercepted_qubits = self.attack.apply(encoded_qubits, self.backend)
        else:
            intercepted_qubits = encoded_qubits

        log("Bob is measuring the qubits...")
        bob_bases = self.protocol.generate_bob_bases(n)
        bob_results = self.protocol.measure(intercepted_qubits, bob_bases, self.backend)

        log("Sifting keys and analyzing errors...")
        key_a, key_b, sifted_indices = self.protocol.sift(alice_bases, bob_bases, alice_bits, bob_results)

        qber = stats.calculate_qber(key_a, key_b)
        is_secure, security_status = stats.analyze_security(qber)
        report = stats.generate_error_report(alice_bits, bob_results, alice_bases, bob_bases, key_a, key_b, qber)

        log("Simulation complete!")
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
