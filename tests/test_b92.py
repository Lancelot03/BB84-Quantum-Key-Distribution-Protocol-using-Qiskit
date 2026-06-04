import pytest
from core import B92Protocol
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

def test_b92_full_no_eve():
    protocol = B92Protocol()
    backend = AerSimulator()
    n = 100

    alice_bits = protocol.generate_bits(n)
    encoded = protocol.encode(alice_bits)

    bob_bases = protocol.generate_bases(n)
    bob_results = protocol.measure(encoded, bob_bases, backend)

    key_a, key_b, _ = protocol.sift(None, bob_bases, alice_bits, bob_results)

    # In B92, keys should match exactly if no noise/Eve
    assert len(key_a) > 0 # Should have some conclusive results
    assert key_a == key_b

def test_b92_sift_logic():
    protocol = B92Protocol()
    alice_bits = [0, 1, 0, 1]
    bob_bases = ['X', 'Z', 'Z', 'X']
    bob_results = [1, 1, 0, 0]

    # Alice 0 (|0>), Bob X -> can measure 1 (conclusive)
    # Alice 1 (|+>), Bob Z -> can measure 1 (conclusive)
    # Alice 0 (|0>), Bob Z -> always measures 0 (inconclusive)
    # Alice 1 (|+>), Bob X -> always measures 0 (inconclusive)

    key_a, key_b, indices = protocol.sift(None, bob_bases, alice_bits, bob_results)

    assert key_a == [0, 1]
    assert key_b == [0, 1]
    assert indices == [0, 1]
