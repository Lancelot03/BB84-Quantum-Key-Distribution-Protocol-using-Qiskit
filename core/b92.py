import random
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from core.protocol import QKDProtocol
from core import stats

class B92Protocol(QKDProtocol):
    def generate_bits(self, n):
        return [random.randint(0, 1) for _ in range(n)]

    def generate_bases(self, n):
        # B92 uses fixed bases for encoding (Alice) and measurement (Bob)
        # But we'll follow the interface. Bob chooses basis to measure.
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

        n = len(circuits)
        meas_circuits = []
        for i, qc in enumerate(circuits):
            nqc = qc.copy()
            # Bob measures in X-basis for bit 0 and Z-basis for bit 1
            # Wait, B92 logic: Alice sends { |0>, |+> }.
            # Bob measures in { |->, |1> }.
            # If Bob measures in Z and gets 1, Alice must have sent |+>.
            # If Bob measures in X and gets 1, Alice must have sent |0>.
            # bases[i] here represents Bob's choice of measurement basis.
            if bases[i] == 'X':
                nqc.h(0)
            nqc.measure(0, 0)
            meas_circuits.append(nqc)

        t_circs = transpile(meas_circuits, backend)
        job = backend.run(t_circs, shots=1, memory=True)
        job_result = job.result()

        results = [int(job_result.get_memory(i)[0]) for i in range(n)]
        return results

    def sift(self, alice_bases, bob_bases, alice_bits, bob_bits):
        # In B92, alice_bases isn't really used as it's fixed.
        # Bob only keeps bits where he got "1" (conclusive result)
        sifted_a, sifted_b = [], []
        indices = []
        for i in range(len(bob_bits)):
            if bob_bits[i] == 1:
                # If Bob measured 1 in Z (bob_bases[i] == 'Z'), Alice must have sent |+> (1)
                # If Bob measured 1 in X (bob_bases[i] == 'X'), Alice must have sent |0> (0)
                key_b_bit = 1 if bob_bases[i] == 'Z' else 0
                sifted_a.append(alice_bits[i])
                sifted_b.append(key_b_bit)
                indices.append(i)
        return sifted_a, sifted_b, indices

def run_b92(n, eve_present, noise_level):
    """
    Legacy wrapper for B92 simulation.
    """
    protocol = B92Protocol()
    alice_bits = protocol.generate_bits(n)
    alice_bases = ["B92"] * n
    encoded_qubits = protocol.encode(alice_bits)

    if eve_present:
        from core.attacks import NoisyChannel
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
        "report": stats.generate_error_report(alice_bits, bob_results, alice_bases, bob_bases, key_a, key_b)
    }
