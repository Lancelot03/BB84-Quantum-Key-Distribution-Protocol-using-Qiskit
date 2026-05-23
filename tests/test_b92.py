import pytest
from core.b92 import B92Protocol
from qiskit_aer import AerSimulator

def test_b92_generate_bits():
    protocol = B92Protocol()
    bits = protocol.generate_bits(10)
    assert len(bits) == 10
    assert all(bit in [0, 1] for bit in bits)

def test_b92_full_no_eve():
    protocol = B92Protocol()
    backend = AerSimulator()
    n = 50

    alice_bits = protocol.generate_bits(n)
    alice_bases = protocol.generate_bases(n)
    encoded = protocol.encode(alice_bits, alice_bases)

    import random
    bob_bases = [random.choice(['Z', 'X']) for _ in range(n)]
    bob_results = protocol.measure(encoded, bob_bases, backend)

    key_a, key_b, _ = protocol.sift(alice_bases, bob_bases, alice_bits, bob_results)

    # In B92, keys should match exactly if no noise
    assert key_a == key_b
    # Efficiency is usually around 25% (50% matching basis * 50% probability of conclusive result)
    assert len(key_a) > 0
