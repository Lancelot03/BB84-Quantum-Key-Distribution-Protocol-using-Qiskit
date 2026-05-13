import random
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

def generate_alice_bits_and_bases(n):
    """
    Generate Alice's random bits and bases.
    """
    bits = [random.randint(0, 1) for _ in range(n)]
    bases = [random.choice(['Z', 'X']) for _ in range(n)]
    return bits, bases

def encode_qubits(bits, bases):
    """
    Encode Alice's bits into quantum circuits based on chosen bases.
    """
    circuits = []
    for bit, base in zip(bits, bases):
        qc = QuantumCircuit(1, 1)
        # Encode bit
        if bit == 1:
            qc.x(0)
        # Choose basis
        if base == 'X':
            qc.h(0)
        circuits.append(qc)
    return circuits

def generate_bob_bases(n):
    """
    Generate Bob's random bases for measurement.
    """
    return [random.choice(['Z', 'X']) for _ in range(n)]

def measure_qubits(circuits, bob_bases, backend=None):
    """
    Bob measures the received circuits using his chosen bases.
    """
    if backend is None:
        backend = Aer.get_backend('qasm_simulator')

    results = []
    for i, qc in enumerate(circuits):
        qc_copy = qc.copy()
        # Measure in Bob's basis
        if bob_bases[i] == 'X':
            qc_copy.h(0)
        qc_copy.measure(0, 0)

        t_qc = transpile(qc_copy, backend)
        job = backend.run(t_qc, shots=1, memory=True)
        result = int(job.result().get_memory()[0])
        results.append(result)
    return results

def sift_keys(alice_bases, bob_bases, alice_bits, bob_bits):
    """
    Sift the keys by keeping only bits where Alice and Bob used the same basis.
    """
    sifted_alice = []
    sifted_bob = []
    kept_indices = []

    for i in range(len(alice_bases)):
        if alice_bases[i] == bob_bases[i]:
            sifted_alice.append(alice_bits[i])
            sifted_bob.append(bob_bits[i])
            kept_indices.append(i)

    return sifted_alice, sifted_bob, kept_indices
