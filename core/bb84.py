import random
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from core.protocol import QKDProtocol

class BB84Protocol(QKDProtocol):
    """
    Implementation of the BB84 Quantum Key Distribution protocol.
    """
    @property
    def name(self) -> str:
        return "BB84"

    def generate_bits(self, n: int) -> list[int]:
        """Generate n random bits."""
        return [random.randint(0, 1) for _ in range(n)]

    def generate_alice_bases(self, n: int) -> list[str]:
        """Generate n random bases ('Z' or 'X') for Alice."""
        return [random.choice(['Z', 'X']) for _ in range(n)]

    def generate_bases(self, n: int) -> list[str]:
        """Generate n random bases ('Z' or 'X') for Bob."""
        return [random.choice(['Z', 'X']) for _ in range(n)]

    def encode(self, bits: list[int], bases: list[str]) -> list[QuantumCircuit]:
        """
        Encodes bits into qubits using the BB84 protocol.
        - Bit 0, Z basis -> |0>
        - Bit 1, Z basis -> |1>
        - Bit 0, X basis -> |+>
        - Bit 1, X basis -> |->
        """
        circuits = []
        for bit, base in zip(bits, bases):
            qc = QuantumCircuit(1, 1)
            if bit == 1:
                qc.x(0)
            if base == 'X':
                qc.h(0)
            circuits.append(qc)
        return circuits

    def measure(self, circuits: list[QuantumCircuit], bases: list[str], backend=None) -> tuple[list[int], list[QuantumCircuit]]:
        if backend is None:
            backend = AerSimulator()

        # Create measurement circuits
        meas_circuits = []
        for i, qc in enumerate(circuits):
            new_qc = qc.copy()
            if bases[i] == 'X':
                new_qc.h(0)
            new_qc.measure(0, 0)
            meas_circuits.append(new_qc)

        # Batch execution for performance
        t_circs = transpile(meas_circuits, backend)
        job = backend.run(t_circs, shots=1, memory=True)
        result_data = job.result()

        results = []
        for i in range(len(circuits)):
            # Qiskit 1.0.2 memory access for batched jobs
            # job.result().get_memory(i) returns the list of memory entries for the i-th circuit
            mem = result_data.get_memory(i)
            results.append(int(mem[0]))

        return results, meas_circuits

    def sift(self, alice_bases: list[str], bob_bases: list[str], alice_bits: list[int], bob_bits: list[int]) -> tuple[list[int], list[int], list[int]]:
        """
        Keeps bits only where Alice and Bob used the same basis.
        """
        sifted_a, sifted_b = [], []
        indices = []
        for i in range(len(alice_bits)):
            if alice_bases[i] == bob_bases[i]:
                sifted_a.append(alice_bits[i])
                sifted_b.append(bob_bits[i])
                indices.append(i)
        return sifted_a, sifted_b, indices
