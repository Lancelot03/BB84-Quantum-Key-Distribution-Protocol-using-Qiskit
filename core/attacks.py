import random
from abc import ABC, abstractmethod
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

class Attack(ABC):
    @abstractmethod
    def apply(self, circuits, backend):
        """Apply attack to the quantum circuits."""
        pass

class InterceptResend(Attack):
    def apply(self, circuits, backend=None):
        if backend is None:
            backend = AerSimulator()

        # Eve chooses random bases
        eve_bases = [random.choice(['Z', 'X']) for _ in range(len(circuits))]

        # Batch measurement for Eve
        eve_measure_circs = []
        for i, qc in enumerate(circuits):
            e_qc = qc.copy()
            if eve_bases[i] == 'X':
                e_qc.h(0)
            e_qc.measure(0, 0)
            eve_measure_circs.append(e_qc)

        t_circuits = transpile(eve_measure_circs, backend)
        job = backend.run(t_circuits, shots=1, memory=True)
        result_data = job.result()

        # Resend qubits based on Eve's measurements
        new_circuits = []
        for i in range(len(circuits)):
            result = int(result_data.get_memory(i)[0])
            re_qc = QuantumCircuit(1, 1)
            if result == 1:
                re_qc.x(0)
            if eve_bases[i] == 'X':
                re_qc.h(0)
            new_circuits.append(re_qc)

        return new_circuits

class NoisyChannel(Attack):
    def __init__(self, noise_level=0.1):
        self.noise_level = noise_level

    def apply(self, circuits, backend=None):
        new_circuits = []
        for qc in circuits:
            noisy_qc = qc.copy()
            if random.random() < self.noise_level:
                # Use Y gate for basis-independent noise (flips both Z and X)
                noisy_qc.y(0)
            new_circuits.append(noisy_qc)
        return new_circuits

class PhotonNumberSplitting(Attack):
    def apply(self, circuits, backend=None):
        new_circuits = []
        for qc in circuits:
            noisy_qc = qc.copy()
            if random.random() < 0.02: # Very low disturbance
                noisy_qc.y(0)
            new_circuits.append(noisy_qc)
        return new_circuits
