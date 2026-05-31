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

        eve_bases = [random.choice(['Z', 'X']) for _ in range(len(circuits))]
        eve_meas_circuits = []
        for i, qc in enumerate(circuits):
            eve_circuit = qc.copy()
            if eve_bases[i] == 'X':
                eve_circuit.h(0)
            eve_circuit.measure(0, 0)
            eve_meas_circuits.append(eve_circuit)

        t_circs = transpile(eve_meas_circuits, backend)
        job = backend.run(t_circs, shots=1, memory=True)
        result = job.result()
        eve_results = [int(result.get_memory(i)[0]) for i in range(len(eve_meas_circuits))]

        new_circuits = []
        for i, res in enumerate(eve_results):
            re_qc = QuantumCircuit(1, 1)
            if res == 1:
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
                # Depolarizing noise model: X, Y, or Z with equal probability
                noise_type = random.choice(['X', 'Y', 'Z'])
                if noise_type == 'X':
                    noisy_qc.x(0)
                elif noise_type == 'Y':
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
