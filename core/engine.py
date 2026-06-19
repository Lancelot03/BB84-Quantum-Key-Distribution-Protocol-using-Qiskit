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

        log(f"Initializing {self.protocol.name} protocol...")

        # 1. Alice generates bits
        alice_bits = self.protocol.generate_bits(n)

        # 2. Alice generates bases (if applicable)
        if self.protocol.name == "BB84":
            alice_bases = self.protocol.generate_bases(n)
        else:
            alice_bases = ["B92"] * n

        # 3. Alice encodes bits into qubits
        log("Encoding qubits...")
        encoded_qubits = self.protocol.encode(alice_bits, alice_bases)

        # 4. Optional Attack
        if self.attack:
            log(f"Applying {type(self.attack).__name__} attack...")
            intercepted_qubits = self.attack.apply(encoded_qubits, self.backend)
        else:
            intercepted_qubits = encoded_qubits

        # 5. Bob generates bases and measures
        log("Bob is measuring...")
        bob_bases = self.protocol.generate_bases(n)
        bob_results = self.protocol.measure(intercepted_qubits, bob_bases, self.backend)

        # 6. Sifting
        log("Sifting keys...")
        key_a, key_b, indices = self.protocol.sift(alice_bases, bob_bases, alice_bits, bob_results)

        # 7. Analysis
        log("Calculating QBER and security...")
        qber = stats.calculate_qber(key_a, key_b)
        is_secure, security_status = stats.analyze_security(qber)

        report = stats.generate_error_report(
            alice_bits, bob_results, alice_bases, bob_bases, key_a, key_b, qber
        )

        return {
            "protocol_name": self.protocol.name,
            "alice_bits": alice_bits,
            "alice_bases": alice_bases,
            "bob_bases": bob_bases,
            "bob_results": bob_results,
            "key_a": key_a,
            "key_b": key_b,
            "indices": indices,
            "qber": qber,
            "is_secure": is_secure,
            "security_status": security_status,
            "report": report,
            "circuits": encoded_qubits # For visualization
        }
