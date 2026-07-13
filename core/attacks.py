import random
from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any, Optional
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

class Attack(ABC):
    """
    Abstract base class for quantum channel attacks (eavesdropping).
    """
    @abstractmethod
    def apply(self, circuits: List[QuantumCircuit], backend: Optional[Any]) -> Tuple[List[QuantumCircuit], Dict[str, Any]]:
        """
        Apply attack to the quantum circuits.

        Args:
            circuits: List of QuantumCircuit objects in transit.
            backend: Optional Qiskit backend for Eve's measurements.

        Returns:
            A tuple containing (modified_circuits, attack_metadata).
        """
        pass

class InterceptResend(Attack):
    """
    Eve intercepts a fraction of qubits, measures them in a random basis,
    and resends a new qubit in the measured state to Bob.
    """
    def __init__(self, intercept_probability: float = 1.0):
        self.intercept_probability = intercept_probability

    def apply(self, circuits: List[QuantumCircuit], backend: Optional[Any] = None) -> Tuple[List[QuantumCircuit], Dict[str, Any]]:
        if backend is None:
            backend = AerSimulator()

        # Decide which qubits Eve intercepts
        intercept_indices = [i for i in range(len(circuits)) if random.random() < self.intercept_probability]

        if not intercept_indices:
            intercepted_info = {
                'type': 'Intercept-Resend',
                'info_gain': 0.0
            }
            return [qc.copy() for qc in circuits], intercepted_info

        # Eve measures only the intercepted qubits
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
        result_idx = 0
        for i in range(len(circuits)):
            if i in intercept_indices:
                res = int(result_data.get_memory(result_idx)[0])
                result_idx += 1
                # Re-encode to send to Bob
                re_qc = QuantumCircuit(1, 1)
                if res == 1:
                    re_qc.x(0)
                if eve_bases[i] == 'X':
                    re_qc.h(0)
                new_circuits.append(re_qc)
            else:
                # Pass through the original circuit
                new_circuits.append(circuits[i].copy())

        intercepted_info = {
            'type': 'Intercept-Resend',
            'info_gain': self.intercept_probability * 0.5
        }
        return new_circuits, intercepted_info

class NoisyChannel(Attack):
    """
    Simulates a noisy quantum channel that applies a bit-flip or phase-flip
    with a certain probability.
    """
    def __init__(self, noise_level: float = 0.1):
        self.noise_level = noise_level

    def apply(self, circuits: List[QuantumCircuit], backend: Optional[Any] = None) -> Tuple[List[QuantumCircuit], Dict[str, Any]]:
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
    Simulates a Photon Number Splitting (PNS) attack on multi-photon pulses.
    Eve gains information without introducing errors (in ideal cases).
    """
    def apply(self, circuits: List[QuantumCircuit], backend: Optional[Any] = None) -> Tuple[List[QuantumCircuit], Dict[str, Any]]:
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
