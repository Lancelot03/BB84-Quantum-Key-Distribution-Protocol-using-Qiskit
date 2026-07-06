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

        # Eve measures in a random basis
        eve_bases = [random.choice(['Z', 'X']) for _ in range(len(circuits))]
        meas_circuits = []
        for i, qc in enumerate(circuits):
            eve_qc = qc.copy()
            if eve_bases[i] == 'X':
                eve_qc.h(0)
            eve_qc.measure(0, 0)
            meas_circuits.append(eve_qc)

        # Batch Eve's measurements
        t_circs = transpile(meas_circuits, backend)
        job = backend.run(t_circs, shots=1, memory=True)
        result_data = job.result()

        new_circuits = []
        for i in range(len(circuits)):
            res = int(result_data.get_memory(i)[0])
            # Re-encode to send to Bob
            re_qc = QuantumCircuit(1, 1)
            if res == 1:
                re_qc.x(0)
            if eve_bases[i] == 'X':
                re_qc.h(0)
            new_circuits.append(re_qc)

        intercepted_info = {
            'type': 'Intercept-Resend',
            'info_gain': 0.5
        }
        return new_circuits, intercepted_info

class NoisyChannel(Attack):
    def __init__(self, noise_level=0.1):
        self.noise_level = noise_level

    def apply(self, circuits, backend=None):
        new_circuits = []
        for qc in circuits:
            noisy_qc = qc.copy()
            if random.random() < self.noise_level:
                # Use Y-gate for basis-independent noise (flips both Z and X)
                noisy_qc.y(0)
            new_circuits.append(noisy_qc)

        intercepted_info = {
            'type': 'Noisy Channel',
            'info_gain': 0.0
        }
        return new_circuits, intercepted_info

class PhotonNumberSplitting(Attack):
    def apply(self, circuits, backend=None):
        new_circuits = []
        for qc in circuits:
            noisy_qc = qc.copy()
            # PNS is typically very subtle, but we simulate some minimal disturbance
            if random.random() < 0.02:
                noisy_qc.x(0)
            new_circuits.append(noisy_qc)

        intercepted_info = {
            'type': 'Photon Number Splitting',
            'info_gain': 0.25
        }
        return new_circuits, intercepted_info
