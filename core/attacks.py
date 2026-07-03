import random
from abc import ABC, abstractmethod
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

class Attack(ABC):
    @abstractmethod
    def apply(self, circuits, backend):
        """
        Apply attack to the quantum circuits.
        Returns a tuple of (new_circuits, intercepted_info).
        """
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

        # Eve's information gain is roughly 50% in BB84 since she
        # guesses the correct basis half of the time.
        return new_circuits, {"info_gain": 0.5, "type": "Intercept-Resend"}

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
        # Noise alone doesn't give Eve information
        return new_circuits, {"info_gain": 0.0, "type": "Noisy Channel"}

class PhotonNumberSplitting(Attack):
    def apply(self, circuits, backend=None):
        new_circuits = []
        for qc in circuits:
            noisy_qc = qc.copy()
            # PNS is typically very subtle. Eve steals a photon from multi-photon pulses.
            # In our simulation, we model this as Eve getting info without disturbance.
            # We add a tiny bit of noise just for visibility.
            if random.random() < 0.02:
                noisy_qc.x(0)
            new_circuits.append(noisy_qc)

        # In PNS, Eve can gain significant info (e.g. 20-30%) without high QBER.
        return new_circuits, {"info_gain": 0.3, "type": "Photon Number Splitting"}
