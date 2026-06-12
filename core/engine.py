from core import stats

class SimulationEngine:
    def __init__(self, protocol, attack=None, backend=None):
        self.protocol = protocol
        self.attack = attack
        self.backend = backend

    def run(self, n, callback=None):
        """
        Orchestrate the QKD simulation.
        """
        def log(msg):
            if callback:
                try:
                    callback(msg)
                except Exception:
                    pass

        log("Generating Alice's bits and bases...")
        alice_bits = self.protocol.generate_bits(n)

        # Determine protocol type for basis generation
        # This is a bit hacky, but consistent with current app.py
        from core.bb84 import BB84Protocol
        if isinstance(self.protocol, BB84Protocol):
            alice_bases = self.protocol.generate_bases(n)
        else:
            alice_bases = ['B92'] * n

        log("Encoding bits into quantum states...")
        encoded_qubits = self.protocol.encode(alice_bits, alice_bases)

        log("Transmitting qubits through channel...")
        if self.attack:
            log(f"Eavesdropper applying {self.attack.__class__.__name__} attack...")
            intercepted_qubits = self.attack.apply(encoded_qubits, self.backend)
        else:
            intercepted_qubits = encoded_qubits

        log("Bob generating bases and measuring...")
        bob_bases = self.protocol.generate_bases(n)
        bob_results = self.protocol.measure(intercepted_qubits, bob_bases, self.backend)

        log("Sifting keys...")
        key_a, key_b, sifted_indices = self.protocol.sift(alice_bases, bob_bases, alice_bits, bob_results)

        log("Analyzing errors and security...")
        qber = stats.calculate_qber(key_a, key_b)
        is_secure, security_status = stats.analyze_security(qber)
        report = stats.generate_error_report(alice_bits, bob_results, alice_bases, bob_bases, key_a, key_b)

        # Add B92 specific logic for eve info gain if needed,
        # or just placeholder as per memory
        if self.attack and isinstance(self.attack, (InterceptResend, NoisyChannel)):
             report['eve_info_gain'] = qber * 2 # Simple simulation heuristic
        else:
             report['eve_info_gain'] = 0.0

        log("Simulation complete!")

        return {
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

# Import these at the bottom to avoid circular imports if any
from core.attacks import InterceptResend, NoisyChannel
