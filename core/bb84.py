import random
from typing import List, Tuple, Optional, Any
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from core.protocol import QKDProtocol

class BB84Protocol(QKDProtocol):
    """
    Implementation of the BB84 Quantum Key Distribution protocol.
    Uses four states: |0>, |1> (Z-basis) and |+>, |-> (X-basis).
    """
    @property
    def name(self) -> str:
        return "BB84"

    def generate_bits(self, n: int) -> List[int]:
        """Generate n random bits for Alice."""
        return [random.randint(0, 1) for _ in range(n)]

    def generate_alice_bases(self, n: int) -> List[str]:
        """Generate n random bases ('Z' or 'X') for Alice."""
        return [random.choice(['Z', 'X']) for _ in range(n)]

    def generate_bases(self, n: int) -> List[str]:
        """Generate n random bases ('Z' or 'X') for Bob."""
        return [random.choice(['Z', 'X']) for _ in range(n)]

    def encode(self, bits: List[int], bases: List[str]) -> List[QuantumCircuit]:
        """Encode bits into quantum circuits using BB84 states."""
        circuits = []
        for bit, base in zip(bits, bases):
            qc = QuantumCircuit(1, 1)
            if bit == 1:
                qc.x(0)
            if base == 'X':
                qc.h(0)
            circuits.append(qc)
        return circuits

    def measure(self, circuits: List[QuantumCircuit], bases: List[str], backend: Optional[Any] = None) -> Tuple[List[int], List[QuantumCircuit]]:
        """Measure the received circuits in the specified bases."""
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
            # Qiskit memory access for batched jobs
            mem = result_data.get_memory(i)
            results.append(int(mem[0]))

        return results, meas_circuits

    def sift(self, alice_bases: List[str], bob_bases: List[str], alice_bits: List[int], bob_bits: List[int]) -> Tuple[List[int], List[int], List[int]]:
        """Perform key sifting where Alice and Bob compare bases."""
        sifted_a, sifted_b = [], []
        indices = []
        for i in range(len(alice_bits)):
            if alice_bases[i] == bob_bases[i]:
                sifted_a.append(alice_bits[i])
                sifted_b.append(bob_bits[i])
                indices.append(i)
        return sifted_a, sifted_b, indices
