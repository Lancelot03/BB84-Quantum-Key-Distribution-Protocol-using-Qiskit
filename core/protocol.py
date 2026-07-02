from abc import ABC, abstractmethod
from qiskit import transpile
from qiskit_aer import AerSimulator

class QKDProtocol(ABC):
    @property
    @abstractmethod
    def name(self):
        """The name of the protocol."""
        pass

    @abstractmethod
    def generate_bits(self, n):
        """Generate random bits for Alice."""
        pass

    @abstractmethod
    def generate_alice_bases(self, n):
        """Generate random bases for Alice's encoding."""
        pass

    @abstractmethod
    def generate_bases(self, n):
        """Generate random bases for Bob's measurement."""
        pass

    @abstractmethod
    def encode(self, bits, bases):
        """Encode bits into quantum circuits using the given bases."""
        pass

    def measure(self, circuits, bases, backend=None):
        """
        Measure the quantum circuits using the given bases.
        Returns a tuple of (results, measurement_circuits).
        """
        if backend is None:
            backend = AerSimulator()

        # Create measurement circuits
        meas_circuits = []
        for i, qc in enumerate(circuits):
            new_qc = qc.copy()
            if bases[i] == 'X':
                new_qc.h(0)
            new_qc.measure(0, 0)
            meas_circuits.append(new_qc)

        # Batch execution for performance
        t_circs = transpile(meas_circuits, backend)
        job = backend.run(t_circs, shots=1, memory=True)
        result_data = job.result()

        results = []
        for i in range(len(circuits)):
            # Qiskit 1.0.2 memory access for batched jobs
            mem = result_data.get_memory(i)
            results.append(int(mem[0]))

        return results, meas_circuits

    @abstractmethod
    def sift(self, alice_bases, bob_bases, alice_bits, bob_bits):
        """Perform key sifting based on basis matching."""
        pass
