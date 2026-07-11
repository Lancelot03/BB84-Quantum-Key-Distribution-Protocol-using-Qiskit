from abc import ABC, abstractmethod

from qiskit import QuantumCircuit

class QKDProtocol(ABC):
    """
    Abstract base class for Quantum Key Distribution protocols.
    """
    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the protocol."""
        pass

    @abstractmethod
    def generate_bits(self, n: int) -> list[int]:
        """Generate random bits for Alice."""
        pass

    @abstractmethod
    def generate_alice_bases(self, n: int) -> list[str]:
        """Generate random bases for Alice's encoding."""
        pass

    @abstractmethod
    def generate_bases(self, n: int) -> list[str]:
        """Generate random bases for Bob's measurement."""
        pass

    @abstractmethod
    def encode(self, bits: list[int], bases: list[str]) -> list[QuantumCircuit]:
        """Encode bits into quantum circuits using the given bases."""
        pass

    @abstractmethod
    def measure(self, circuits: list[QuantumCircuit], bases: list[str], backend=None) -> tuple[list[int], list[QuantumCircuit]]:
        """
        Measure the quantum circuits using the given bases.
        Returns a tuple of (results, measurement_circuits).
        """
        pass

    @abstractmethod
    def sift(self, alice_bases: list[str], bob_bases: list[str], alice_bits: list[int], bob_bits: list[int]) -> tuple[list[int], list[int], list[int]]:
        """
        Perform key sifting based on basis matching.
        Returns (sifted_alice, sifted_bob, matched_indices).
        """
        pass
