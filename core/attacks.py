import random
from abc import ABC, abstractmethod
from qiskit import QuantumCircuit, transpile

class Attack(ABC):
    @abstractmethod
    def apply(self, circuits, backend):
        """Apply attack to the quantum circuits."""
        pass

class InterceptResend(Attack):
    def apply(self, circuits, backend):
        new_circuits = []
        eve_bases = [random.choice(['Z', 'X']) for _ in range(len(circuits))]
        for i, qc in enumerate(circuits):
            eve_circuit = qc.copy()
            if eve_bases[i] == 'X':
                eve_circuit.h(0)
            eve_circuit.measure(0, 0)
            t_qc = transpile(eve_circuit, backend)
            job = backend.run(t_qc, shots=1, memory=True)
            result = int(job.result().get_memory()[0])

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

    def apply(self, circuits, backend):
        new_circuits = []
        for qc in circuits:
            noisy_qc = qc.copy()
            if random.random() < self.noise_level:
                noisy_qc.x(0) # Bit flip noise
            new_circuits.append(noisy_qc)
        return new_circuits

class PhotonNumberSplitting(Attack):
    def apply(self, circuits, backend):
        new_circuits = []
        for qc in circuits:
            noisy_qc = qc.copy()
            if random.random() < 0.02: # Very low disturbance
                noisy_qc.x(0)
            new_circuits.append(noisy_qc)
        return new_circuits
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

def intercept_resend(circuits, backend=None):
    """
    Eve intercepts the qubits, measures them in a random basis,
    and resends them to Bob in the state she measured.
    """
    if backend is None:
        backend = Aer.get_backend('qasm_simulator')

    eve_bases = [random.choice(['Z', 'X']) for _ in range(len(circuits))]
    intercepted_circuits = []

    for i, qc in enumerate(circuits):
        eve_qc = qc.copy()
        if eve_bases[i] == 'X':
            eve_qc.h(0)
        eve_qc.measure(0, 0)

        t_qc = transpile(eve_qc, backend)
        job = backend.run(t_qc, shots=1, memory=True)
        result = int(job.result().get_memory()[0])

        # Resend a new qubit in the measured state and basis
        resend_qc = QuantumCircuit(1, 1)
        if result == 1:
            resend_qc.x(0)
        if eve_bases[i] == 'X':
            resend_qc.h(0)
        intercepted_circuits.append(resend_qc)

    return intercepted_circuits, eve_bases

def noisy_channel(circuits, noise_level=0.1):
    """
    Simulates a noisy channel by applying bit-flip noise (X gates)
    with a certain probability.
    """
    noisy_circuits = []
    for qc in circuits:
        nqc = qc.copy()
        if random.random() < noise_level:
            nqc.x(0)
        noisy_circuits.append(nqc)
    return noisy_circuits

def photon_number_splitting(circuits, disturbance=0.02):
    """
    Simulates PNS attack. In a real scenario, Eve would split multi-photon pulses.
    Here we simulate it as a low-disturbance attack where Eve gets some info
    without introducing significant QBER.
    """
    pns_circuits = []
    for qc in circuits:
        pqc = qc.copy()
        # Very low disturbance simulation
        if random.random() < disturbance:
            pqc.x(0)
        pns_circuits.append(pqc)
    return pns_circuits
