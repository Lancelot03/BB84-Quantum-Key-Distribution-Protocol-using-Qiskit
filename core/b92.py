import random
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from core.protocol import QKDProtocol
from core import stats

class B92Protocol(QKDProtocol):
    @property
    def name(self):
        return "B92"

    def generate_bits(self, n):
        return [random.randint(0, 1) for _ in range(n)]

    def generate_alice_bases(self, n):
        return ["B92"] * n

    def generate_bases(self, n):
        # In B92, Bob chooses between Z and X bases for measurement
        return [random.choice(['Z', 'X']) for _ in range(n)]

    def encode(self, bits, bases=None):
        # bases is ignored in B92 for Alice's encoding
        circuits = []
        for bit in bits:
            qc = QuantumCircuit(1, 1)
            if bit == 1:
                qc.h(0) # |+> state
            # bit 0 is |0> state (default)
            circuits.append(qc)
        return circuits

    def sift(self, alice_bases, bob_bases, alice_bits, bob_bits):
        # Sifting for B92: Bob only keeps bits where he got "1" (conclusive result)
        sifted_a, sifted_b = [], []
        indices = []
        for i in range(len(bob_bits)):
            if bob_bits[i] == 1:
                # If Bob measured 1 in Z, Alice must have sent |+> (1)
                # If Bob measured 1 in X, Alice must have sent |0> (0)
                key_b_bit = 1 if bob_bases[i] == 'Z' else 0
                sifted_a.append(alice_bits[i])
                sifted_b.append(key_b_bit)
                indices.append(i)
        return sifted_a, sifted_b, indices
