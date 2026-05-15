import random
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from core import metrics

def run_b92(n, eve_present, noise_level):
    """
    Simulate the B92 protocol.
    """
    # Alice sends 0 as |0> and 1 as |+>
    alice_bits = [random.randint(0, 1) for _ in range(n)]
    circuits = []
    for bit in alice_bits:
        qc = QuantumCircuit(1, 1)
        if bit == 1:
            qc.h(0)
        circuits.append(qc)

    # Bob measures in X-basis for 0 and Z-basis for 1 (or vice versa)
    # Actually Bob measures in {|+>, |->} and {|0>, |1>}
    bob_bases = [random.choice(['Z', 'X']) for _ in range(n)]

    # Intercept-resend for B92 (Simplified)
    if eve_present:
        # Just add noise for now
        intercepted = []
        for qc in circuits:
            nqc = qc.copy()
            if random.random() < noise_level:
                nqc.x(0)
            intercepted.append(nqc)
    else:
        intercepted = circuits

    backend = Aer.get_backend('qasm_simulator')
    bob_results = []
    for i, qc in enumerate(intercepted):
        nqc = qc.copy()
        if bob_bases[i] == 'X': # Measure in X
            nqc.h(0)
        nqc.measure(0, 0)
        t_qc = transpile(nqc, backend)
        job = backend.run(t_qc, shots=1, memory=True)
        bob_results.append(int(job.result().get_memory()[0]))

    # Sifting for B92: Bob only keeps bits where he got "1" (conclusive result)
    key_a, key_b = [], []
    for i in range(n):
        if bob_results[i] == 1:
            # If Bob measured 1 in Z, Alice must have sent |+> (1)
            # If Bob measured 1 in X, Alice must have sent |0> (0)
            key_b_bit = 1 if bob_bases[i] == 'Z' else 0
            key_a.append(alice_bits[i])
            key_b.append(key_b_bit)

    qber = metrics.calculate_qber(key_a, key_b)
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
