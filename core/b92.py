import random
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from core.protocol import QKDProtocol
from core import stats

class B92Protocol(QKDProtocol):
    def generate_bits(self, n):
        return [random.randint(0, 1) for _ in range(n)]

    def generate_bases(self, n):
        """For B92, this returns Bob's measurement bases."""
        return [random.choice(['Z', 'X']) for _ in range(n)]

    def encode(self, bits, bases=None):
        """
        Alice encodes bits: 0 -> |0>, 1 -> |+>
        'bases' is ignored for Alice in B92.
        """
        circuits = []
        for bit in bits:
            qc = QuantumCircuit(1, 1)
            if bit == 1:
                qc.h(0)
            circuits.append(qc)
        return circuits

    def measure(self, circuits, bob_bases, backend=None):
        if backend is None:
            backend = AerSimulator()

        bob_results = []
        for i, qc in enumerate(circuits):
            nqc = qc.copy()
            if bob_bases[i] == 'X':  # Measure in X
                nqc.h(0)
            nqc.measure(0, 0)
            t_qc = transpile(nqc, backend)
            job = backend.run(t_qc, shots=1)
            result = int(list(job.result().get_counts().keys())[0])
            bob_results.append(result)
        return bob_results

    def sift(self, alice_bases, bob_bases, alice_bits, bob_results):
        """
        Sifting for B92: Bob only keeps bits where he got '1' (conclusive result).
        'alice_bases' is ignored.
        """
        key_a, key_b = [], []
        indices = []
        for i in range(len(bob_results)):
            if bob_results[i] == 1:
                # If Bob measured 1 in Z, Alice must have sent |+> (1)
                # If Bob measured 1 in X, Alice must have sent |0> (0)
                key_b_bit = 1 if bob_bases[i] == 'Z' else 0
                key_a.append(alice_bits[i])
                key_b.append(key_b_bit)
                indices.append(i)
        return key_a, key_b, indices

def run_b92(n, eve_present, noise_level):
    """
    Legacy function maintained for compatibility until app.py is updated.
    """
    protocol = B92Protocol()
    alice_bits = protocol.generate_bits(n)
    circuits = protocol.encode(alice_bits)
    bob_bases = protocol.generate_bases(n)

    # Intercept-resend for B92 (Simplified)
    if eve_present:
        # Just add noise for now
        intercepted = []
        for qc in circuits:
            nqc = qc.copy()
            if random.random() < noise_level:
                nqc.x(0)
            intercepted.append(nqc)
    else:
        intercepted = circuits

    bob_results = protocol.measure(intercepted, bob_bases)
    key_a, key_b, _ = protocol.sift(None, bob_bases, alice_bits, bob_results)

    qber = stats.calculate_qber(key_a, key_b)
    return {
        "alice_bits": alice_bits,
        "alice_bases": ["B92"] * n,
        "bob_bases": bob_bases,
        "bob_results": bob_results,
        "key_a": key_a,
        "key_b": key_b,
        "qber": qber,
        "report": None
    }
