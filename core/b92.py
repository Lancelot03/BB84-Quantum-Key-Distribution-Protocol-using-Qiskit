import random
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from core.protocol import QKDProtocol
from core import stats

class B92Protocol(QKDProtocol):
    def generate_bits(self, n):
        return [random.randint(0, 1) for _ in range(n)]

    def generate_bases(self, n):
        # In B92, Bob selects bases to measure Alice's non-orthogonal states.
        # Alice uses a fixed encoding (0 -> |0>, 1 -> |+>).
        return [random.choice(['Z', 'X']) for _ in range(n)]

    def encode(self, bits, bases=None):
        # Bases is not strictly used by Alice in B92 as her encoding is fixed.
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
            job = backend.run(t_qc, shots=1, memory=True)
            result = int(job.result().get_memory()[0])
            results.append(result)
        return results

    def sift(self, alice_bases, bob_bases, alice_bits, bob_bits):
        # alice_bases is just a placeholder for B92 to match the interface.
        key_a, key_b = [], []
        indices = []
        for i in range(len(bob_bits)):
            if bob_bits[i] == 1:
                # If Bob measured 1 in Z, Alice must have sent |+> (1)
                # If Bob measured 1 in X, Alice must have sent |0> (0)
                key_b_bit = 1 if bob_bases[i] == 'Z' else 0
                key_a.append(alice_bits[i])
                key_b.append(key_b_bit)
                indices.append(i)
        return key_a, key_b, indices

def run_b92(n, eve_present, noise_level):
    """
    Legacy wrapper for B92 simulation.
    """
    protocol = B92Protocol()
    alice_bits = protocol.generate_bits(n)
    alice_bases = ["B92"] * n
    encoded_qubits = protocol.encode(alice_bits)

    if eve_present:
        intercepted = []
        for qc in encoded_qubits:
            nqc = qc.copy()
            if random.random() < noise_level:
                nqc.x(0)
            intercepted.append(nqc)
    else:
        intercepted = encoded_qubits

    bob_bases = protocol.generate_bases(n)
    bob_results = protocol.measure(intercepted, bob_bases)

    key_a, key_b, _ = protocol.sift(alice_bases, bob_bases, alice_bits, bob_results)

    qber = stats.calculate_qber(key_a, key_b)
    return {
        "alice_bits": alice_bits,
        "alice_bases": alice_bases,
        "bob_bases": bob_bases,
        "bob_results": bob_results,
        "key_a": key_a,
        "key_b": key_b,
        "qber": qber,
        "report": None
    }
