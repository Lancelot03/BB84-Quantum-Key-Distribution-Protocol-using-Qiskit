import random
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from core.protocol import QKDProtocol
from core import stats

class B92Protocol(QKDProtocol):
    def generate_bits(self, n):
        return [random.randint(0, 1) for _ in range(n)]

    def generate_bases(self, n):
        """In B92, Alice's basis is implicitly tied to her bits (0->|0>, 1->|+>)."""
        return ['B92'] * n

    def generate_bob_bases(self, n):
        return [random.choice(['Z', 'X']) for _ in range(n)]

    def encode(self, bits, bases=None):
        circuits = []
        for bit in bits:
            qc = QuantumCircuit(1, 1)
            if bit == 1:
                qc.h(0)
            circuits.append(qc)
        return circuits

    def measure(self, circuits, bob_bases, backend=None):
        if backend is None:
            backend = Aer.get_backend('qasm_simulator')

        measurement_circuits = []
        for i, qc in enumerate(circuits):
            new_qc = qc.copy()
            if bob_bases[i] == 'X':
                new_qc.h(0)
            new_qc.measure(0, 0)
            measurement_circuits.append(new_qc)

        t_circuits = transpile(measurement_circuits, backend)
        job = backend.run(t_circuits, shots=1, memory=True)
        result_data = job.result()

        results = []
        for i in range(len(circuits)):
            results.append(int(result_data.get_memory(i)[0]))
        return results

    def sift(self, alice_bases, bob_bases, alice_bits, bob_results):
        key_a, key_b = [], []
        indices = []
        for i in range(len(bob_results)):
            if bob_results[i] == 1:
                # Bob got a conclusive result
                # If Bob measured 1 in Z, Alice must have sent |+> (bit 1)
                # If Bob measured 1 in X, Alice must have sent |0> (bit 0)
                key_b_bit = 1 if bob_bases[i] == 'Z' else 0
                key_a.append(alice_bits[i])
                key_b.append(key_b_bit)
                indices.append(i)
        return key_a, key_b, indices

def run_b92(n, eve_present, noise_level):
    """
    Wrapper for backward compatibility with the UI.
    """
    from core.attacks import NoisyChannel

    protocol = B92Protocol()
    alice_bits = protocol.generate_bits(n)
    alice_bases = protocol.generate_bases(n)
    encoded_qubits = protocol.encode(alice_bits)

    backend = Aer.get_backend('qasm_simulator')

    if eve_present:
        # Use NoisyChannel as a simple way to represent Eavesdropper's impact for B92 in this wrapper
        attack = NoisyChannel(noise_level)
        intercepted_qubits = attack.apply(encoded_qubits, backend)
    else:
        intercepted_qubits = encoded_qubits

    bob_bases = protocol.generate_bob_bases(n)
    bob_results = protocol.measure(intercepted_qubits, bob_bases, backend)

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
        "report": None,
        "encoded_qubits": encoded_qubits # Return circuits for visualization
    }
