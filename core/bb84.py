import random
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from core.protocol import QKDProtocol

class BB84Protocol(QKDProtocol):
    def generate_bits(self, n):
        return [random.randint(0, 1) for _ in range(n)]

    def generate_bases(self, n):
        return [random.choice(['Z', 'X']) for _ in range(n)]

    def encode(self, bits, bases):
        circuits = []
        for bit, base in zip(bits, bases):
            qc = QuantumCircuit(1, 1)
            qc.metadata = {'bit': bit, 'base': base}
            if bit == 1:
                qc.x(0)
            if base == 'X':
                qc.h(0)
            circuits.append(qc)
        return circuits

    def measure(self, circuits, bases, backend=None):
        if backend is None:
            backend = AerSimulator()

        # Prepare measurement circuits
        meas_circuits = []
        for i, qc in enumerate(circuits):
            mqc = qc.copy()
            if bases[i] == 'X':
                mqc.h(0)
            mqc.measure(0, 0)
            meas_circuits.append(mqc)

        # Batch transpile and run
        t_circuits = transpile(meas_circuits, backend)
        job = backend.run(t_circuits, shots=1, memory=True)
        result = job.result()

        return [int(result.get_memory(i)[0]) for i in range(len(circuits))]

    def sift(self, alice_bases, bob_bases, alice_bits, bob_bits):
        sifted_a, sifted_b = [], []
        indices = []
        for i in range(len(alice_bits)):
            if alice_bases[i] == bob_bases[i]:
                sifted_a.append(alice_bits[i])
                sifted_b.append(bob_bits[i])
                indices.append(i)
        return sifted_a, sifted_b, indices
