import random
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from core.protocol import QKDProtocol

class B92Protocol(QKDProtocol):
    def generate_bits(self, n):
        return [random.randint(0, 1) for _ in range(n)]

    def generate_bases(self, n):
        # Bob chooses bases to measure in: Z or X
        return [random.choice(['Z', 'X']) for _ in range(n)]

    def encode(self, bits, bases=None):
        # In B92, Alice encodes 0 as |0> (Z-basis) and 1 as |+> (X-basis)
        # bases parameter is ignored for Alice in B92 but kept for interface compatibility
        circuits = []
        for bit in bits:
            qc = QuantumCircuit(1, 1)
            if bit == 1:
                qc.h(0)
            circuits.append(qc)
        return circuits

    def measure(self, circuits, bases, backend=None):
        if backend is None:
            backend = AerSimulator()

        results = []
        for i, qc in enumerate(circuits):
            new_qc = qc.copy()
            if bases[i] == 'X':
                new_qc.h(0)
            new_qc.measure(0, 0)
            t_qc = transpile(new_qc, backend)
            job = backend.run(t_qc, shots=1)
            counts = job.result().get_counts()
            result = int(max(counts, key=counts.get))
            results.append(result)
        return results

    def sift(self, alice_bits, bob_bases, bob_results):
        # In B92, Alice and Bob keep bits where Bob got a conclusive result (1)
        # If Bob measured 1 in Z (bases[i] == 'Z'), Alice must have sent |+> (1)
        # If Bob measured 1 in X (bases[i] == 'X'), Alice must have sent |0> (0)
        sifted_a, sifted_b = [], []
        indices = []
        for i in range(len(bob_results)):
            if bob_results[i] == 1:
                key_b_bit = 1 if bob_bases[i] == 'Z' else 0
                sifted_a.append(alice_bits[i])
                sifted_b.append(key_b_bit)
                indices.append(i)
        return sifted_a, sifted_b, indices

def run_b92(n, eve_present, noise_level):
    """
    Legacy function wrapper for B92 simulation.
    """
    from core.attacks import NoisyChannel
    from core import stats

    protocol = B92Protocol()
    alice_bits = protocol.generate_bits(n)
    circuits = protocol.encode(alice_bits)

    if eve_present:
        attack = NoisyChannel(noise_level)
        intercepted = attack.apply(circuits)
    else:
        intercepted = circuits

    bob_bases = protocol.generate_bases(n)
    bob_results = protocol.measure(intercepted, bob_bases)

    key_a, key_b, sifted_indices = protocol.sift(alice_bits, bob_bases, bob_results)

    qber = stats.calculate_qber(key_a, key_b)

    return {
        "alice_bits": alice_bits,
        "alice_bases": ["B92"] * n,
        "bob_bases": bob_bases,
        "bob_results": bob_results,
        "key_a": key_a,
        "key_b": key_b,
        "qber": qber,
        "report": None, # Will be filled by generate_error_report in app.py if needed
        "encoded_qubits": circuits
    }
