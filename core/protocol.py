from abc import ABC, abstractmethod

class QKDProtocol(ABC):
    @abstractmethod
    def generate_bits(self, n):
        """Generate random bits for Alice."""
        pass

    @abstractmethod
    def generate_bases(self, n):
        """Generate random bases for Alice and Bob."""
        pass

    def generate_alice_bases(self, n):
        """Default: Alice uses same logic as generic bases."""
        return self.generate_bases(n)

    def generate_bob_bases(self, n):
        """Default: Bob uses same logic as generic bases."""
        return self.generate_bases(n)

    @abstractmethod
    def encode(self, bits, bases):
        """Encode bits into quantum circuits using the given bases."""
        pass

    @abstractmethod
    def measure(self, circuits, bases, backend=None):
        """Measure the quantum circuits using the given bases."""
        pass

    @abstractmethod
    def sift(self, alice_bases, bob_bases, alice_bits, bob_bits):
        """Perform key sifting based on basis matching."""
        pass
