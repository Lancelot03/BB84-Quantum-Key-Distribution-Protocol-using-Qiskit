import random
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from core.protocol import QKDProtocol
from core import stats

class B92Protocol(QKDProtocol):
    def generate_bits(self, n):
        return [random.randint(0, 1) for _ in range(n)]

    def generate_bases(self, n):
        # In B92, Bob randomly chooses between Z and X bases for measurement
        return [random.choice(['Z', 'X']) for _ in range(n)]

    def encode(self, bits, bases=None):
        # Alice sends 0 as |0> (Z-basis) and 1 as |+> (X-basis)
        circuits = []
        for bit in bits:
            qc = QuantumCircuit(1, 1)
            if bit == 1:
                qc.h(0)
            circuits.append(qc)
        return circuits

    def measure(self, circuits, bases, backend=None):
        if backend is None:
            backend = Aer.get_backend('qasm_simulator')

        measured_circuits = []
        for i, qc in enumerate(circuits):
            new_qc = qc.copy()
            if bases[i] == 'X':
                new_qc.h(0)
            new_qc.measure(0, 0)
            measured_circuits.append(new_qc)

        t_circs = transpile(measured_circuits, backend)
        job = backend.run(t_circs, shots=1, memory=True)
        result_obj = job.result()

        results = [int(result_obj.get_memory(i)[0]) for i in range(len(circuits))]
        return results

    def sift(self, alice_bases, bob_bases, alice_bits, bob_bits):
        # Sifting for B92: Bob only keeps bits where he got "1" (conclusive result)
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
