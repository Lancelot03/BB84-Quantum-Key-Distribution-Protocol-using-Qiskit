import random
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from core.protocol import QKDProtocol
from core import stats

class B92Protocol(QKDProtocol):
    def generate_bits(self, n):
        return [random.randint(0, 1) for _ in range(n)]

    def generate_bases(self, n):
        # B92 doesn't use random bases like BB84 in the same way,
        # but we use it to represent Bob's measurement basis choice.
        return [random.choice(['Z', 'X']) for _ in range(n)]

    def encode(self, bits, bases=None):
        """Alice sends 0 as |0> and 1 as |+>"""
        circuits = []
        for bit in bits:
            qc = QuantumCircuit(1, 1)
            if bit == 1:
                qc.h(0)
            circuits.append(qc)
        return circuits

    def measure(self, circuits, bases, backend=None):
        """Bob measures in X-basis for 0 and Z-basis for 1 (or vice versa)"""
        if backend is None:
            backend = Aer.get_backend('qasm_simulator')

        measured_circuits = []
        for i, qc in enumerate(circuits):
            nqc = qc.copy()
            if bases[i] == 'X':
                nqc.h(0)
            nqc.measure(0, 0)
            measured_circuits.append(nqc)

        t_circs = transpile(measured_circuits, backend)
        job = backend.run(t_circs, shots=1, memory=True)
        result = job.result()

        results = []
        for i in range(len(circuits)):
            results.append(int(result.get_memory(i)[0]))
        return results

    def sift(self, alice_bases, bob_bases, alice_bits, bob_bits):
        """Sifting for B92: Bob only keeps bits where he got '1' (conclusive result)"""
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

def run_b92(n, eve_present, noise_level):
    """
    Backward compatibility wrapper for run_b92.
    """
    protocol = B92Protocol()
    alice_bits = protocol.generate_bits(n)
    alice_bases = ["B92"] * n
    encoded_qubits = protocol.encode(alice_bits)

    if eve_present:
        from core.attacks import NoisyChannel
        attack = NoisyChannel(noise_level)
        intercepted = attack.apply(encoded_qubits)
    else:
        intercepted = encoded_qubits

    bob_bases = protocol.generate_bases(n)
    bob_results = protocol.measure(intercepted, bob_bases)

    key_a, key_b, sifted_indices = protocol.sift(alice_bases, bob_bases, alice_bits, bob_results)
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
