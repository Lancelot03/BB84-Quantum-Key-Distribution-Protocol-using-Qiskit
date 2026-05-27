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

        n = len(circuits)
        eve_bases = [random.choice(['Z', 'X']) for _ in range(n)]

        # Eve measures
        meas_circuits = []
        for i, qc in enumerate(circuits):
            mqc = qc.copy()
            if eve_bases[i] == 'X':
                mqc.h(0)
            mqc.measure(0, 0)
            meas_circuits.append(mqc)

        t_circuits = transpile(meas_circuits, backend)
        job = backend.run(t_circuits, shots=1, memory=True)
        results = job.result()

        # Eve resends
        new_circuits = []
        for i in range(n):
            res = int(results.get_memory(i)[0])
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
                # Depolarizing noise model: X, Y, or Z flip with equal probability
                choice = random.choice(['X', 'Y', 'Z'])
                if choice == 'X':
                    noisy_qc.x(0)
                elif choice == 'Y':
                    noisy_qc.y(0)
                else:
                    noisy_qc.z(0)
            new_circuits.append(noisy_qc)
        return new_circuits

class PhotonNumberSplitting(Attack):
    def apply(self, circuits, backend=None):
        # Simplified PNS: Eve occasionally gets the bit without disturbance
        # In this simulation, we'll represent it as very low noise for now
        new_circuits = []
        for qc in circuits:
            noisy_qc = qc.copy()
            if random.random() < 0.01: # Minimal disturbance
                noisy_qc.x(0)
            new_circuits.append(noisy_qc)
        return new_circuits
