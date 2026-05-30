import random
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from core.protocol import QKDProtocol
from core import stats

class B92Protocol(QKDProtocol):
    def generate_bits(self, n):
        return [random.randint(0, 1) for _ in range(n)]

    def generate_bases(self, n):
        # In B92, bases are fixed for encoding, but Bob chooses bases for measurement
        return [random.choice(['Z', 'X']) for _ in range(n)]

    def encode(self, bits, bases=None):
        """
        Alice encodes 0 as |0> (Z-basis) and 1 as |+> (X-basis).
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
        Bob measures in X-basis for 0 and Z-basis for 1.
        Wait, in standard B92:
        Alice sends { |0>, |+> }.
        Bob measures in { |->, |1> }.
        If Bob measures |1> in Z-basis (bases[i]=='Z'), he knows Alice sent |+> (1).
        If Bob measures |-> in X-basis (bases[i]=='X'), he knows Alice sent |0> (0).
        Actually, the implementation in run_b92 was:
        Bob measures in X-basis (|+>, |->) if bases[i]=='X'
        Bob measures in Z-basis (|0>, |1>) if bases[i]=='Z'
        If he gets result 1:
        - In X-basis measurement, it means he got |->, so Alice must have sent |0>.
        - In Z-basis measurement, it means he got |1>, so Alice must have sent |+> (1).
        """
        if backend is None:
            backend = AerSimulator()

        measured_circuits = []
        for i, qc in enumerate(circuits):
            new_qc = qc.copy()
            if bases[i] == 'X':
                new_qc.h(0)
            new_qc.measure(0, 0)
            measured_circuits.append(new_qc)

        t_circuits = transpile(measured_circuits, backend)
        job = backend.run(t_circuits, shots=1, memory=True)
        result_obj = job.result()

        results = []
        for i in range(len(circuits)):
            results.append(int(result_obj.get_memory(i)[0]))
        return results

    def sift(self, alice_bases, bob_bases, alice_bits, bob_bits):
        """
        B92 Sifting: Bob only keeps bits where he got a '1' (conclusive result).
        """
        key_a, key_b = [], []
        indices = []
        for i in range(len(bob_bits)):
            if bob_bits[i] == 1:
                # If Bob measured 1 in Z, Alice must have sent |+> (bit 1)
                # If Bob measured 1 in X, Alice must have sent |0> (bit 0)
                bit_b = 1 if bob_bases[i] == 'Z' else 0
                key_a.append(alice_bits[i])
                key_b.append(bit_b)
                indices.append(i)
        return key_a, key_b, indices

def run_b92(n, eve_present, noise_level):
    """
    Legacy wrapper for run_b92 using the new B92Protocol class.
    """
    from core.attacks import NoisyChannel
    protocol = B92Protocol()
    alice_bits = protocol.generate_bits(n)
    alice_bases = ["B92"] * n # For reporting consistency

    encoded_qubits = protocol.encode(alice_bits)

    if eve_present:
        attack = NoisyChannel(noise_level)
        intercepted = attack.apply(encoded_qubits)
    else:
        intercepted = encoded_qubits

    bob_bases = protocol.generate_bases(n)
    bob_results = protocol.measure(intercepted, bob_bases)

    key_a, key_b, sifted_indices = protocol.sift(None, bob_bases, alice_bits, bob_results)

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
