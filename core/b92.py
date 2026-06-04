import random
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from core.protocol import QKDProtocol
from core import stats

class B92Protocol(QKDProtocol):
    def generate_bases(self, n):
        # Bob measures in X-basis for 0 and Z-basis for 1 (convention chosen for B92)
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
            backend = AerSimulator()

        # Batch measurement
        measurement_circuits = []
        for i, qc in enumerate(circuits):
            m_qc = qc.copy()
            if bases[i] == 'X': # Measure in X
                m_qc.h(0)
            m_qc.measure(0, 0)
            measurement_circuits.append(m_qc)

        t_circuits = transpile(measurement_circuits, backend)
        job = backend.run(t_circuits, shots=1, memory=True)
        result_data = job.result()

        results = []
        for i in range(len(circuits)):
            # get_memory(i) returns a list for that circuit, we take the first shot
            res = int(result_data.get_memory(i)[0])
            results.append(res)
        return results

    def sift(self, alice_bases, bob_bases, alice_bits, bob_results):
        # Sifting for B92: Bob only keeps bits where he got "1" (conclusive result)
        key_a, key_b = [], []
        indices = []
        for i in range(len(alice_bits)):
            if bob_results[i] == 1:
                # If Bob measured 1 in Z, Alice must have sent |+> (1)
                # If Bob measured 1 in X, Alice must have sent |0> (0)
                key_b_bit = 1 if bob_bases[i] == 'Z' else 0
                key_a.append(alice_bits[i])
                key_b.append(key_b_bit)
                indices.append(i)
        return key_a, key_b, indices

def run_b92(n, eve_present, noise_level):
    """
    Simulate the B92 protocol (Wrapper for backward compatibility).
    """
    protocol = B92Protocol()
    alice_bits = protocol.generate_bits(n)
    circuits = protocol.encode(alice_bits)

    # Intercept-resend for B92 (Simplified/Noisy)
    if eve_present:
        from core.attacks import NoisyChannel
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
        "report": None
    }
