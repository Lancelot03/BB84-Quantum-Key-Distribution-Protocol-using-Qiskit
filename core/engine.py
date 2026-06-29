from qiskit_aer import AerSimulator
from core.stats import calculate_qber, analyze_security, generate_error_report

class SimulationEngine:
    def __init__(self, protocol, attack=None, backend=None):
        self.protocol = protocol
        self.attack = attack
        self.backend = backend or AerSimulator()

    def run(self, n, callback=None):
        def log(msg):
            if callback:
                try:
                    callback(msg)
                except Exception:
                    pass

        log(f"Starting {self.protocol.name} simulation with {n} qubits...")

        # 1. Alice generates random bits
        alice_bits = self.protocol.generate_bits(n)
        log("Alice generated random bits.")

        # 2. Alice generates random bases (if applicable)
        if self.protocol.name == "BB84":
            alice_bases = self.protocol.generate_bases(n)
        else:
            alice_bases = ["B92"] * n
        log("Alice prepared bases.")

        # 3. Alice encodes bits into quantum circuits
        circuits = self.protocol.encode(alice_bits, alice_bases)
        log("Alice encoded bits into quantum circuits.")

        # 4. Optional Attack
        if self.attack:
            log(f"Applying attack: {type(self.attack).__name__}...")
            intercepted_circuits = self.attack.apply(circuits, self.backend)
        else:
            intercepted_circuits = circuits

        # 5. Bob generates random bases and measures
        bob_bases = self.protocol.generate_bases(n)
        bob_results = self.protocol.measure(intercepted_circuits, bob_bases, self.backend)
        log("Bob measured the received qubits.")

        # 6. Sifting
        key_a, key_b, indices = self.protocol.sift(alice_bases, bob_bases, alice_bits, bob_results)
        log("Alice and Bob performed key sifting.")

        # 7. Error Analysis
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
            "indices": indices,
            "qber": qber,
            "is_secure": is_secure,
            "security_status": security_status,
            "report": report,
            "circuits": circuits # Alice's original circuits for visualization
        }
