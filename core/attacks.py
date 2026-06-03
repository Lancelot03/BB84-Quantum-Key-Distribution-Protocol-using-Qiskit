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

        # Eve measures the qubits in random bases
        eve_bases = [random.choice(['Z', 'X']) for _ in range(len(circuits))]
        eve_measurement_circuits = []
        for i, qc in enumerate(circuits):
            eve_qc = qc.copy()
            if eve_bases[i] == 'X':
                eve_qc.h(0)
            eve_qc.measure(0, 0)
            eve_measurement_circuits.append(eve_qc)

        # Batch measurement
        t_eve_circuits = transpile(eve_measurement_circuits, backend)
        job = backend.run(t_eve_circuits, shots=1, memory=True)
        result_data = job.result()

        # Resend new qubits based on results
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
                # Using Y-gate for basis-independent noise (applies both bit and phase flip)
                noisy_qc.y(0)
            new_circuits.append(noisy_qc)
        return new_circuits

class PhotonNumberSplitting(Attack):
    """
    Simulates a Photon Number Splitting (PNS) attack where Eve exploits multi-photon pulses.
    In this simplified simulation, it introduces minor noise but allows Eve to gain info
    without significantly increasing QBER if pulses were multi-photon.
    """
    def apply(self, circuits, backend=None):
        new_circuits = []
        for qc in circuits:
            noisy_qc = qc.copy()
            # PNS in real life might not introduce any error if Eve only takes the extra photon.
            # Here we simulate some small disturbance or specific noise.
            if random.random() < 0.05:
                noisy_qc.y(0)
            new_circuits.append(noisy_qc)
        return new_circuits
