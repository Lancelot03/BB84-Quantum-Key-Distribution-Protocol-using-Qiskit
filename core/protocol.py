from abc import ABC, abstractmethod
import random

class QKDProtocol(ABC):
    def generate_bits(self, n):
        """Generate random bits for Alice."""
        return [random.randint(0, 1) for _ in range(n)]

    @abstractmethod
    def generate_bases(self, n):
        """Generate random bases for Alice and Bob."""
        pass

    @abstractmethod
    def encode(self, bits, bases):
        """Encode bits into quantum circuits using the given bases."""
        pass

    @abstractmethod
    def measure(self, circuits, bases, backend=None):
        """Perform measurement on quantum circuits."""
        pass

    @abstractmethod
    def sift(self, alice_bases, bob_bases, alice_bits, bob_bits):
        """Perform key sifting based on basis matching."""
        pass
