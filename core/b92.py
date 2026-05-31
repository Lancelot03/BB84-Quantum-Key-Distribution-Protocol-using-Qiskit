import random
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from core.protocol import QKDProtocol
from core import stats

class B92Protocol(QKDProtocol):
    def generate_bits(self, n):
        return [random.randint(0, 1) for _ in range(n)]

    def generate_bases(self, n):
        # Bob's bases in B92
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

        meas_circuits = []
        for i, qc in enumerate(circuits):
            nqc = qc.copy()
            if bob_bases[i] == 'X':
                nqc.h(0)
            nqc.measure(0, 0)
            meas_circuits.append(nqc)

        t_circs = transpile(meas_circuits, backend)
        job = backend.run(t_circs, shots=1, memory=True)
        result = job.result()

        return [int(result.get_memory(i)[0]) for i in range(len(meas_circuits))]

    def sift(self, alice_bases, bob_bases, alice_bits, bob_results):
        key_a, key_b = [], []
        indices = []
        for i in range(len(alice_bits)):
            if bob_results[i] == 1:
                key_b_bit = 1 if bob_bases[i] == 'Z' else 0
                key_a.append(alice_bits[i])
                key_b.append(key_b_bit)
                indices.append(i)
        return key_a, key_b, indices
