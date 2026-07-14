import random
from typing import List, Tuple, Optional, Any
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from core.protocol import QKDProtocol

class B92Protocol(QKDProtocol):
    """
    Implementation of the B92 Quantum Key Distribution protocol.
    Uses two non-orthogonal states: |0> and |+>.
    """
    @property
    def name(self) -> str:
        return "B92"

    def generate_bits(self, n: int) -> List[int]:
        """Generate n random bits for Alice."""
        return [random.randint(0, 1) for _ in range(n)]

    def generate_alice_bases(self, n: int) -> List[str]:
        """B92 always uses a single encoding scheme for Alice."""
        return ["B92"] * n

    def generate_bases(self, n: int) -> List[str]:
        """In B92, Bob chooses between Z and X bases for measurement."""
        return [random.choice(['Z', 'X']) for _ in range(n)]

    def encode(self, bits: List[int], bases: Optional[List[str]] = None) -> List[QuantumCircuit]:
        """Encode bits into |0> (bit 0) and |+> (bit 1) states."""
        circuits = []
        for bit in bits:
            qc = QuantumCircuit(1, 1)
            if bit == 1:
                qc.h(0) # |+> state
            # bit 0 is |0> state (default)
            circuits.append(qc)
        return circuits

    def measure(self, circuits: List[QuantumCircuit], bases: List[str], backend: Optional[Any] = None) -> Tuple[List[int], List[QuantumCircuit]]:
        """Bob measures in Z or X basis to find conclusive results."""
        if backend is None:
            backend = AerSimulator()

        meas_circuits = []
        for i, qc in enumerate(circuits):
            new_qc = qc.copy()
            if bases[i] == 'X':
                new_qc.h(0)
            new_qc.measure(0, 0)
            meas_circuits.append(new_qc)

        t_circs = transpile(meas_circuits, backend)
        job = backend.run(t_circs, shots=1, memory=True)
        result_data = job.result()

        results = []
        for i in range(len(circuits)):
            mem = result_data.get_memory(i)
            results.append(int(mem[0]))
        return results, meas_circuits

    def sift(self, alice_bases: List[str], bob_bases: List[str], alice_bits: List[int], bob_bits: List[int]) -> Tuple[List[int], List[int], List[int]]:
        """Sifting for B92: Bob only keeps bits where he got '1' (conclusive result)."""
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
