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

        # Eve generates her own bases
        eve_bases = [random.choice(['Z', 'X']) for _ in range(len(circuits))]

        # Prepare circuits for Eve's measurement
        measured_circuits = []
        for i, qc in enumerate(circuits):
            eve_qc = qc.copy()
            if eve_bases[i] == 'X':
                eve_qc.h(0)
            eve_qc.measure(0, 0)
            measured_circuits.append(eve_qc)

        # Batch execution of Eve's measurements
        t_circs = transpile(measured_circuits, backend)
        job = backend.run(t_circs, shots=1, memory=True)
        result_data = job.result()

        # Eve re-encodes and sends to Bob
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
                noisy_qc.y(0) # Use Y gate for basis-independent noise
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
