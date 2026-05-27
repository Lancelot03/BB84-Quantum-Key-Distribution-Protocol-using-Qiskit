import random
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from core.protocol import QKDProtocol
from core import stats

class B92Protocol(QKDProtocol):
    def generate_bits(self, n):
        return [random.randint(0, 1) for _ in range(n)]

    def generate_bases(self, n):
        # In B92, Bob's basis selection is his measurement choice
        return [random.choice(['Z', 'X']) for _ in range(n)]

    def encode(self, bits, bases=None):
        # bases is not strictly used for encoding in B92 as Alice's bits map directly to states
        circuits = []
        for bit in bits:
            qc = QuantumCircuit(1, 1)
            qc.metadata = {'bit': bit}
            if bit == 1:
                qc.h(0) # State |+>
            # bit 0 is State |0>
            circuits.append(qc)
        return circuits

    def measure(self, circuits, bases, backend=None):
        if backend is None:
            backend = AerSimulator()

        meas_circuits = []
        for i, qc in enumerate(circuits):
            mqc = qc.copy()
            if bases[i] == 'X':
                mqc.h(0)
            mqc.measure(0, 0)
            meas_circuits.append(mqc)

        t_circuits = transpile(meas_circuits, backend)
        job = backend.run(t_circuits, shots=1, memory=True)
        result = job.result()

        return [int(result.get_memory(i)[0]) for i in range(len(circuits))]

    def sift(self, alice_bases, bob_bases, alice_bits, bob_results):
        # alice_bases is ignore for B92 sifting
        key_a, key_b = [], []
        indices = []
        for i in range(len(bob_results)):
            if bob_results[i] == 1:
                # Conclusive result
                key_b_bit = 1 if bob_bases[i] == 'Z' else 0
                key_a.append(alice_bits[i])
                key_b.append(key_b_bit)
                indices.append(i)
        return key_a, key_b, indices

def run_b92(n, eve_present, noise_level):
    """
    Legacy wrapper for compatibility during transition.
    """
    from core.attacks import NoisyChannel
    protocol = B92Protocol()
    alice_bits = protocol.generate_bits(n)
    circuits = protocol.encode(alice_bits)

    if eve_present:
        attack = NoisyChannel(noise_level)
        intercepted = attack.apply(circuits)
    else:
        intercepted = circuits

    bob_bases = protocol.generate_bases(n)
    bob_results = protocol.measure(intercepted, bob_bases)

    key_a, key_b, _ = protocol.sift(None, bob_bases, alice_bits, bob_results)
    qber = stats.calculate_qber(key_a, key_b)

    return {
        "alice_bits": alice_bits,
        "alice_bases": ["B92"] * n,
        "bob_bases": bob_bases,
        "bob_results": bob_results,
        "key_a": key_a,
        "key_b": key_b,
        "qber": qber,
        "report": None,
        "encoded_qubits": circuits # Added for visualization
    }
