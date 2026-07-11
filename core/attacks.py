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
    """
    Simulates an Intercept-Resend attack where Eve measures qubits in random bases.
    """
    def __init__(self, intercept_probability: float = 1.0):
        """
        Args:
            intercept_probability: Probability (0 to 1) that Eve intercepts a given qubit.
        """
        self.intercept_probability = intercept_probability

    def apply(self, circuits: list[QuantumCircuit], backend=None) -> tuple[list[QuantumCircuit], dict]:
        """
        Apply Intercept-Resend attack.

        Eve randomly decides which qubits to intercept based on intercept_probability.
        For intercepted qubits, she measures in a random basis (Z or X) and re-sends.
        """
        if backend is None:
            backend = AerSimulator()

        n = len(circuits)
        intercept_indices = [i for i in range(n) if random.random() < self.intercept_probability]

        if not intercept_indices:
            return [qc.copy() for qc in circuits], {'type': 'Intercept-Resend', 'info_gain': 0.0}

        # Eve measures in a random basis for intercepted qubits
        eve_bases = {i: random.choice(['Z', 'X']) for i in intercept_indices}
        meas_circuits = []
        for i in intercept_indices:
            eve_qc = circuits[i].copy()
            if eve_bases[i] == 'X':
                eve_qc.h(0)
            eve_qc.measure(0, 0)
            meas_circuits.append(eve_qc)

        # Batch Eve's measurements
        t_circs = transpile(meas_circuits, backend)
        job = backend.run(t_circs, shots=1, memory=True)
        result_data = job.result()

        new_circuits = []
        meas_idx = 0
        for i in range(n):
            if i in intercept_indices:
                res = int(result_data.get_memory(meas_idx)[0])
                meas_idx += 1
                # Re-encode to send to Bob
                re_qc = QuantumCircuit(1, 1)
                if res == 1:
                    re_qc.x(0)
                if eve_bases[i] == 'X':
                    re_qc.h(0)
                new_circuits.append(re_qc)
            else:
                # Passive bypass
                new_circuits.append(circuits[i].copy())

        intercepted_info = {
            'type': 'Intercept-Resend',
            'info_gain': self.intercept_probability * 0.5 # Theoretical max info gain is 0.5 per qubit
        }
        return new_circuits, intercepted_info

class NoisyChannel(Attack):
    """
    Simulates a noisy quantum channel that introduces random bit/phase flips.
    """
    def __init__(self, noise_level: float = 0.1):
        """
        Args:
            noise_level: Probability (0 to 1) of a flip occurring on each qubit.
        """
        self.noise_level = noise_level

    def apply(self, circuits: list[QuantumCircuit], backend=None) -> tuple[list[QuantumCircuit], dict]:
        """
        Apply noise to the circuits.
        """
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
    """
    Simulates a Photon Number Splitting (PNS) attack.
    In this attack, Eve gains information from multi-photon pulses without increasing QBER.
    """
    def apply(self, circuits: list[QuantumCircuit], backend=None) -> tuple[list[QuantumCircuit], dict]:
        """
        Apply PNS attack simulation.
        """
        new_circuits = []
        for qc in circuits:
            noisy_qc = qc.copy()
            # PNS is typically very subtle, but we simulate some minimal disturbance
            # In a true PNS attack on a perfect single-photon source, it would do nothing to the state.
            if random.random() < 0.02:
                noisy_qc.x(0)
            new_circuits.append(noisy_qc)

        intercepted_info = {
            'type': 'Photon Number Splitting',
            'info_gain': 0.25 # Typical value for PNS information gain
        }
        return new_circuits, intercepted_info
