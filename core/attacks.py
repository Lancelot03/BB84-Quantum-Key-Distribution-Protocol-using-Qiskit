import random
from abc import ABC, abstractmethod
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

class Attack(ABC):
    @abstractmethod
    def apply(self, circuits, backend):
        """Apply attack to the quantum circuits."""
        pass

class InterceptResend(Attack):
    def apply(self, circuits, backend=None):
        if backend is None:
            backend = Aer.get_backend('qasm_simulator')

        n = len(circuits)
        eve_bases = [random.choice(['Z', 'X']) for _ in range(n)]

        # Prepare circuits for Eve's measurement
        eve_measure_circuits = []
        for i, qc in enumerate(circuits):
            eve_qc = qc.copy()
            if eve_bases[i] == 'X':
                eve_qc.h(0)
            eve_qc.measure(0, 0)
            eve_measure_circuits.append(eve_qc)

        # Batch Eve's measurement
        t_eve_circs = transpile(eve_measure_circuits, backend)
        job = backend.run(t_eve_circs, shots=1, memory=True)
        eve_results = [int(job.result().get_memory(i)[0]) for i in range(n)]

        # Eve re-encodes and sends new qubits to Bob
        new_circuits = []
        for i in range(n):
            re_qc = QuantumCircuit(1, 1)
            if eve_results[i] == 1:
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
                noisy_qc.x(0) # Bit flip noise
            new_circuits.append(noisy_qc)
        return new_circuits

class PhotonNumberSplitting(Attack):
    def apply(self, circuits, backend=None):
        new_circuits = []
        for qc in circuits:
            noisy_qc = qc.copy()
            if random.random() < 0.02:
                noisy_qc.x(0)
            new_circuits.append(noisy_qc)
        return new_circuits
