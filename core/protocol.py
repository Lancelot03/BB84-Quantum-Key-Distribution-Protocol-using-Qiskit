from abc import ABC, abstractmethod

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

    @abstractmethod
    def measure(self, circuits, bases, backend=None):
        """
        Measure the quantum circuits using the given bases.
        Returns a tuple of (results, measurement_circuits).
        """
        pass

    @abstractmethod
    def sift(self, alice_bases, bob_bases, alice_bits, bob_bits):
        """Perform key sifting based on basis matching."""
        pass
