import random
from qiskit import QuantumCircuit, Aer, execute
import matplotlib.pyplot as plt

# --- Step 1: Alice creates random bits and bases ---
def create_alice_bits(n):
    bits = [random.randint(0, 1) for _ in range(n)]
    bases = [random.choice(['Z', 'X']) for _ in range(n)]
    return bits, bases

# --- Step 2: Alice encodes qubits based on bits and bases ---
def encode_qubits(bits, bases):
    circuits = []
    for bit, base in zip(bits, bases):
        qc = QuantumCircuit(1, 1)
        if bit == 1:
            qc.x(0)
        if base == 'X':
            qc.h(0)
        circuits.append(qc)
    return circuits

# --- Step 3: Eve intercepts and measures ---
def eve_intercept(circuits):
    backend = Aer.get_backend('qasm_simulator')
    eve_bases = [random.choice(['Z', 'X']) for _ in range(len(circuits))]
    new_circuits = []

    for i, qc in enumerate(circuits):
        new_qc = qc.copy()
        new_qc.barrier()

        # Eve measures
        if eve_bases[i] == 'X':
            new_qc.h(0)
        new_qc.measure(0, 0)
        job = execute(new_qc, backend, shots=1, memory=True)
        result = int(job.result().get_memory()[0])

        # Eve re-encodes
        eve_qc = QuantumCircuit(1, 1)
        if result == 1:
            eve_qc.x(0)
        if eve_bases[i] == 'X':
            eve_qc.h(0)
        new_circuits.append(eve_qc)
    return new_circuits, eve_bases

# --- Step 4: Bob measures ---
def measure_qubits(circuits, bob_bases):
    backend = Aer.get_backend('qasm_simulator')
    results = []

    for i, qc in enumerate(circuits):
        qc_copy = qc.copy()
        if bob_bases[i] == 'X':
            qc_copy.h(0)
        qc_copy.measure(0, 0)
        job = execute(qc_copy, backend, shots=1, memory=True)
        result = job.result().get_memory()[0]
        results.append(int(result))
    return results

# --- Step 5: Sift keys ---
def sift_keys(alice_bases, bob_bases, alice_bits, bob_bits):
    sifted_alice = []
    sifted_bob = []
    indices = []

    for i in range(len(alice_bits)):
        if alice_bases[i] == bob_bases[i]:
            sifted_alice.append(alice_bits[i])
            sifted_bob.append(bob_bits[i])
            indices.append(i)
    return sifted_alice, sifted_bob, indices

# --- QBER ---
def calculate_qber(alice_key, bob_key):
    errors = sum([a != b for a, b in zip(alice_key, bob_key)])
    return errors / len(alice_key) if alice_key else 0.0

# --- Visualization ---
def plot_bit_differences(alice_key, bob_key):
    diffs = [a != b for a, b in zip(alice_key, bob_key)]
    plt.figure(figsize=(10, 2))
    plt.title("Bit Differences (1 = Error, 0 = Match)")
    plt.plot(diffs, marker='o', linestyle='-', color='red')
    plt.xlabel("Bit Index")
    plt.ylabel("Difference")
    plt.grid(True)
    plt.show()

def plot_qber_bar(qber):
    plt.figure()
    correct = 100 * (1 - qber)
    incorrect = 100 * qber
    plt.bar(['Correct Bits', 'Incorrect Bits'], [correct, incorrect], color=['green', 'red'])
    plt.title(f"Quantum Bit Error Rate (QBER): {qber*100:.2f}%")
    plt.ylabel("Percentage")
    plt.ylim(0, 100)
    plt.show()

# --- Main Program ---
def main():
    n = 100

    alice_bits, alice_bases = create_alice_bits(n)
    circuits = encode_qubits(alice_bits, alice_bases)

    eve_circuits, eve_bases = eve_intercept(circuits)
    bob_bases = [random.choice(['Z', 'X']) for _ in range(n)]
    bob_results = measure_qubits(eve_circuits, bob_bases)

    alice_key, bob_key, indices = sift_keys(alice_bases, bob_bases, alice_bits, bob_results)
    qber = calculate_qber(alice_key, bob_key)

    print(f"Sifted Key Length: {len(alice_key)}")
    print(f"QBER: {qber*100:.2f}%")

    if qber > 0.15:
        print("⚠️ High QBER! Possible eavesdropping detected.")
    else:
        print("✅ Low QBER. Communication appears secure.")

    # 🔍 Show Visuals
    plot_bit_differences(alice_key, bob_key)
    plot_qber_bar(qber)

if __name__ == "__main__":
    main()

