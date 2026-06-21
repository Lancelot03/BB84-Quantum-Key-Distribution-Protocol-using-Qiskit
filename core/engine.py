from qiskit_aer import AerSimulator
from core.stats import calculate_qber, analyze_security, generate_error_report

class SimulationEngine:
    def __init__(self, backend=None):
        self.backend = backend if backend else AerSimulator()

    def run(self, protocol, n, eve_present=False, attack=None, callback=None):
        def log(msg):
            if callback:
                try:
                    callback(msg)
                except Exception:
                    pass

        log(f"Starting {protocol.name} simulation with n={n}...")

        # 1. Alice generates bits
        alice_bits = protocol.generate_bits(n)
        log("Alice generated random bits.")

        # 2. Alice/Bob generate bases
        # BB84 needs bases for both, B92 only for Bob's measurement
        if protocol.name == "BB84":
            alice_bases = protocol.generate_bases(n)
            bob_bases = protocol.generate_bases(n)
        else:
            alice_bases = ["B92"] * n
            bob_bases = protocol.generate_bases(n)
        log("Bases generated.")

        # 3. Alice encodes
        circuits = protocol.encode(alice_bits, alice_bases)
        log("Alice encoded bits into qubits.")

        # 4. Eve Attacks
        if eve_present and attack:
            log(f"Eve is attacking using {attack.__class__.__name__}...")
            intercepted_circuits = attack.apply(circuits, self.backend)
        else:
            intercepted_circuits = circuits

        # 5. Bob Measures
        bob_results = protocol.measure(intercepted_circuits, bob_bases, self.backend)
        log("Bob measured the received qubits.")

        # 6. Sifting
        key_a, key_b, indices = protocol.sift(alice_bases, bob_bases, alice_bits, bob_results)
        log(f"Sifting complete. Sifted key length: {len(key_a)}")

        # 7. Analysis
        qber = calculate_qber(key_a, key_b)
        is_secure, status = analyze_security(qber)
        report = generate_error_report(alice_bits, bob_results, alice_bases, bob_bases, key_a, key_b)

        log("Simulation complete.")

        return {
            "protocol_name": protocol.name,
            "alice_bits": alice_bits,
            "alice_bases": alice_bases,
            "bob_bases": bob_bases,
            "bob_results": bob_results,
            "key_a": key_a,
            "key_b": key_b,
            "indices": indices,
            "qber": qber,
            "is_secure": is_secure,
            "security_status": status,
            "report": report,
            "circuits": circuits
        }
