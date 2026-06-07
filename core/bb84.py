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
            if bit == 1:
                qc.x(0)
            if base == 'X':
                qc.h(0)
            circuits.append(qc)
        return circuits

    def measure(self, circuits, bases, backend=None):
        if backend is None:
            backend = AerSimulator()

        # Prepare circuits for measurement
        measured_circuits = []
        for i, qc in enumerate(circuits):
            m_qc = qc.copy()
            if bases[i] == 'X':
                m_qc.h(0)
            m_qc.measure(0, 0)
            measured_circuits.append(m_qc)

        # Execute all circuits in one batch
        t_circs = transpile(measured_circuits, backend)
        job = backend.run(t_circs, shots=1, memory=True)
        result_data = job.result()

        # Extract results from memory
        results = []
        for i in range(len(circuits)):
            # get_memory(i) returns a list of results for the i-th circuit
            results.append(int(result_data.get_memory(i)[0]))

        return results

    def sift(self, alice_bases, bob_bases, alice_bits, bob_bits):
        sifted_a, sifted_b = [], []
        indices = []
        for i in range(len(alice_bits)):
            if alice_bases[i] == bob_bases[i]:
                sifted_a.append(alice_bits[i])
                sifted_b.append(bob_bits[i])
                indices.append(i)
        return sifted_a, sifted_b, indices
