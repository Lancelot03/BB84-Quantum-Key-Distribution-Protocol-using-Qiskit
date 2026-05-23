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

        new_circuits = []
        eve_bases = [random.choice(['Z', 'X']) for _ in range(len(circuits))]
        for i, qc in enumerate(circuits):
            eve_circuit = qc.copy()
            if eve_bases[i] == 'X':
                eve_circuit.h(0)
            eve_circuit.measure(0, 0)
            t_qc = transpile(eve_circuit, backend)
            job = backend.run(t_qc, shots=1)
            counts = job.result().get_counts()
            result = int(max(counts, key=counts.get))

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
                # Depolarizing noise: apply X, Y, or Z with 1/3 probability each
                choice = random.random()
                if choice < 1/3:
                    noisy_qc.x(0)
                elif choice < 2/3:
                    noisy_qc.y(0)
                else:
                    noisy_qc.z(0)
            new_circuits.append(noisy_qc)
        return new_circuits

class PhotonNumberSplitting(Attack):
    def apply(self, circuits, backend=None):
        new_circuits = []
        for qc in circuits:
            noisy_qc = qc.copy()
            if random.random() < 0.02: # Very low disturbance
                noisy_qc.x(0)
            new_circuits.append(noisy_qc)
        return new_circuits
