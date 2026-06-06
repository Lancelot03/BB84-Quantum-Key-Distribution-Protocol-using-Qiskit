import random
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from core.protocol import QKDProtocol
from core import stats

class B92Protocol(QKDProtocol):
    def generate_bits(self, n):
        """Alice's bits."""
        return [random.randint(0, 1) for _ in range(n)]

    def generate_bases(self, n):
        """
        For B92, Alice doesn't really 'choose' a basis in the BB84 sense for each qubit,
        but Bob chooses a measurement basis.
        Returning 'Z' or 'X' for Bob.
        """
        return [random.choice(['Z', 'X']) for _ in range(n)]

    def encode(self, bits, bases=None):
        """
        B92 Encoding: 0 -> |0> (Z-basis), 1 -> |+> (X-basis)
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
        Bob measures in X-basis if he wants to check for 0,
        and in Z-basis if he wants to check for 1.
        Wait, in B92 standard:
        Alice sends { |0>, |+> }.
        Bob measures in { |+>_perp, |0>_perp } which are { |1>, |-> }.
        Actually, simpler:
        Bob measures in X basis. If he gets 1 (i.e. |->), he knows Alice didn't send |+> (1), so she sent |0> (0).
        Bob measures in Z basis. If he gets 1 (i.e. |1>), he knows Alice didn't send |0> (0), so she sent |+> (1).
        """
        if backend is None:
            backend = Aer.get_backend('qasm_simulator')

        measurement_circuits = []
        for i, qc in enumerate(circuits):
            new_qc = qc.copy()
            if bases[i] == 'X':
                new_qc.h(0)
            new_qc.measure(0, 0)
            measurement_circuits.append(new_qc)

        t_circuits = transpile(measurement_circuits, backend)
        job = backend.run(t_circuits, shots=1, memory=True)
        results_obj = job.result()

        results = [int(results_obj.get_memory(i)[0]) for i in range(len(circuits))]
        return results

    def sift(self, alice_bases, bob_bases, alice_bits, bob_bits):
        """
        Sifting for B92: Bob only keeps bits where he got "1" (conclusive result).
        """
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
    Backward compatible function for initial UI integration.
    """
    protocol = B92Protocol()
    alice_bits = protocol.generate_bits(n)
    encoded_qubits = protocol.encode(alice_bits)

    if eve_present:
        # Simplified noise for backward compatibility
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

    key_a, key_b, indices = protocol.sift(None, bob_bases, alice_bits, bob_results)

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
