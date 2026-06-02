import pytest
from core.b92 import B92Protocol
from qiskit_aer import AerSimulator

def test_b92_generate_bits():
    protocol = B92Protocol()
    bits = protocol.generate_bits(10)
    assert len(bits) == 10
    assert all(bit in [0, 1] for bit in bits)

def test_b92_generate_bases():
    protocol = B92Protocol()
    bases = protocol.generate_bases(10)
    assert len(bases) == 10
    assert all(base in ['Z', 'X'] for base in bases)

def test_b92_sift():
    protocol = B92Protocol()
    alice_bits = [0, 1, 0, 1]
    bob_bases = ['X', 'X', 'Z', 'Z']
    bob_bits = [1, 0, 1, 0] # Bob got 1 only in indices 0 and 2

    # Bob measures 1 in X (index 0) -> Alice sent 0
    # Bob measures 1 in Z (index 2) -> Alice sent 1

    key_a, key_b, indices = protocol.sift(None, bob_bases, alice_bits, bob_bits)

    assert key_a == [0, 0] # bits at index 0 and 2 are 0 and 0
    assert key_b == [0, 1] # inferred from bob_bases X and Z
    assert indices == [0, 2]

def test_b92_full_no_eve():
    protocol = B92Protocol()
    backend = AerSimulator()
    n = 50

    alice_bits = protocol.generate_bits(n)
    encoded = protocol.encode(alice_bits)

    bob_bases = protocol.generate_bases(n)
    bob_results = protocol.measure(encoded, bob_bases, backend)

    key_a, key_b, _ = protocol.sift(None, bob_bases, alice_bits, bob_results)

    # In B92, if Alice and Bob are honest and no noise, key_a MUST equal key_b
    assert key_a == key_b
    # Also, we expect some bits to be sifted (conclusive results happen ~25% of the time)
    assert len(key_a) > 0
