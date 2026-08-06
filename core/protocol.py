from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Any
from qiskit import QuantumCircuit

class QKDProtocol(ABC):
    """
    Abstract base class for Quantum Key Distribution protocols.
    Defines the standard interface for bit generation, encoding, measurement, and sifting.
    """
    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the protocol."""
        pass

    @abstractmethod
    def generate_bits(self, n: int) -> List[int]:
        """Generate random bits for Alice."""
        pass

    @abstractmethod
    def generate_alice_bases(self, n: int) -> List[str]:
        """Generate random bases for Alice's encoding."""
        pass

    @abstractmethod
    def generate_bases(self, n: int) -> List[str]:
        """Generate random bases for Bob's measurement."""
        pass

    @abstractmethod
    def encode(self, bits: List[int], bases: List[str]) -> List[QuantumCircuit]:
        """Encode bits into quantum circuits using the given bases."""
        pass

    @abstractmethod
    def measure(self, circuits: List[QuantumCircuit], bases: List[str], backend: Optional[Any] = None) -> Tuple[List[int], List[QuantumCircuit]]:
        """
        Measure the quantum circuits using the given bases.
        Returns a tuple of (results, measurement_circuits).
        """
        pass

    @abstractmethod
    def sift(self, alice_bases: List[str], bob_bases: List[str], alice_bits: List[int], bob_bits: List[int]) -> Tuple[List[int], List[int], List[int]]:
        """
        Perform key sifting based on basis matching.
        Returns a tuple of (sifted_alice_key, sifted_bob_key, sifted_indices).
        """
        pass
