import random
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from core.protocol import QKDProtocol

class B92Protocol(QKDProtocol):
    def generate_bits(self, n):
        return [random.randint(0, 1) for _ in range(n)]

    def generate_bases(self, n):
        # B92 uses bases for measurement choices
        return [random.choice(['Z', 'X']) for _ in range(n)]

    def encode(self, bits, bases=None):
        """
        Alice encodes 0 as |0> and 1 as |+>.
        bases is not strictly needed for Alice in B92 but kept for interface consistency.
        """
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
            # Result is '0' or '1'
            result = int(list(counts.keys())[0])
            results.append(result)
        return results

    def sift(self, alice_bits, bob_bases, bob_results):
        """
        In B92, Bob only keeps bits where he got a conclusive result (1).
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
