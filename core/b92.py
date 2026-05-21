import random
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from core.protocol import QKDProtocol
from core import stats

class B92Protocol(QKDProtocol):
    def generate_bits(self, n):
        """Generate random bits for Alice."""
        return [random.randint(0, 1) for _ in range(n)]

    def generate_bases(self, n):
        """Generate random bases for Bob's measurement."""
        return [random.choice(['Z', 'X']) for _ in range(n)]

    def encode(self, bits, bases=None):
        """
        Encode bits into quantum circuits.
        Alice sends 0 as |0> and 1 as |+>.
        """
        circuits = []
        for bit in bits:
            qc = QuantumCircuit(1, 1)
            if bit == 1:
                qc.h(0)
            circuits.append(qc)
        return circuits

    def measure(self, circuits, bob_bases, backend=None):
        """Bob measures the qubits using his chosen bases."""
        if backend is None:
            backend = AerSimulator()

        results = []
        for i, qc in enumerate(circuits):
            new_qc = qc.copy()
            if bob_bases[i] == 'X':
                new_qc.h(0)
            new_qc.measure(0, 0)
            t_qc = transpile(new_qc, backend)
            job = backend.run(t_qc, shots=1)
            result = int(list(job.result().get_counts().keys())[0])
            results.append(result)
        return results

    def sift(self, alice_bases, bob_bases, alice_bits, bob_bits):
        """
        Perform key sifting for B92.
        Bob only keeps bits where he got a conclusive '1' result.
        """
        key_a, key_b = [], []
        indices = []
        for i in range(len(bob_bits)):
            if bob_bits[i] == 1:
                # Conclusive result
                # If Bob measured 1 in Z (basis 'Z'), Alice must have sent |+> (bit 1)
                # If Bob measured 1 in X (basis 'X'), Alice must have sent |0> (bit 0)
                key_b_bit = 1 if bob_bases[i] == 'Z' else 0
                key_a.append(alice_bits[i])
                key_b.append(key_b_bit)
                indices.append(i)
        return key_a, key_b, indices

def run_b92(n, eve_present, noise_level):
    """
    Legacy compatibility function for B92 simulation.
    """
    protocol = B92Protocol()
    alice_bits = protocol.generate_bits(n)
    # In B92 Alice doesn't use bases, but we can represent it for the report
    alice_bases = ["B92"] * n

    encoded_qubits = protocol.encode(alice_bits)

    # Intercept-resend for B92 (Simplified/Noise-based as before)
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
