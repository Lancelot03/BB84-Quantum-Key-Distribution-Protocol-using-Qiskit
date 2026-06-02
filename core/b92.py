import random
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from core.protocol import QKDProtocol
from core import stats

class B92Protocol(QKDProtocol):
    def generate_bits(self, n):
        """Alice's secret bits."""
        return [random.randint(0, 1) for _ in range(n)]

    def generate_bases(self, n):
        """Bob's measurement bases."""
        return [random.choice(['Z', 'X']) for _ in range(n)]

    def encode(self, bits, bases=None):
        """
        Alice encodes 0 as |0> and 1 as |+>.
        Bases is ignored for Alice in B92 but kept for interface consistency.
        """
        circuits = []
        for bit in bits:
            qc = QuantumCircuit(1, 1)
            if bit == 1:
                qc.h(0)
            circuits.append(qc)
        return circuits

    def measure(self, circuits, bases, backend=None):
        """
        Bob measures in X-basis for 0 and Z-basis for 1.
        """
        if backend is None:
            backend = AerSimulator()

        measurement_circuits = []
        for i, qc in enumerate(circuits):
            new_qc = qc.copy()
            if bases[i] == 'X':
                new_qc.h(0)
            new_qc.measure(0, 0)
            measurement_circuits.append(new_qc)

        t_circuits = transpile(measurement_circuits, backend)
        job = backend.run(t_circuits, shots=1, memory=True)
        result_data = job.result()

        results = []
        for i in range(len(circuits)):
            memory = result_data.get_memory(i)
            results.append(int(memory[0]))
        return results

    def sift(self, alice_bases, bob_bases, alice_bits, bob_bits):
        """
        Sifting for B92: Bob only keeps bits where he got '1' (conclusive result).
        alice_bases is ignored (Alice only has one basis in B92).
        """
        key_a, key_b = [], []
        indices = []
        for i in range(len(bob_bits)):
            if bob_bits[i] == 1:
                # If Bob measured 1 in Z (base='Z'), Alice must have sent |+> (bit=1)
                # If Bob measured 1 in X (base='X'), Alice must have sent |0> (bit=0)
                key_b_bit = 1 if bob_bases[i] == 'Z' else 0
                key_a.append(alice_bits[i])
                key_b.append(key_b_bit)
                indices.append(i)
        return key_a, key_b, indices

def run_b92(n, eve_present, noise_level):
    """
    Legacy wrapper for run_b92.
    """
    protocol = B92Protocol()
    alice_bits = protocol.generate_bits(n)
    alice_bases = ['B92'] * n
    encoded_qubits = protocol.encode(alice_bits)

    if eve_present:
        # Simplified noise for now as in original
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
