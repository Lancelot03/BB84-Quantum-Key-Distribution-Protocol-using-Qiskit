import pytest
from core.b92 import B92Protocol
from qiskit_aer import AerSimulator

def test_b92_generate_bits():
    protocol = B92Protocol()
    bits = protocol.generate_bits(10)
    assert len(bits) == 10
    assert all(bit in [0, 1] for bit in bits)

def test_b92_sift():
    protocol = B92Protocol()
    alice_bits = [0, 1, 0, 1]
    bob_bases = ['X', 'Z', 'Z', 'X']
    bob_results = [1, 1, 0, 0] # 1 means conclusive

    key_a, key_b, indices = protocol.sift(None, bob_bases, alice_bits, bob_results)

    # Bob measured 1 in X -> inferred Alice bit 0. Alice sent 0. Correct.
    # Bob measured 1 in Z -> inferred Alice bit 1. Alice sent 1. Correct.
    assert key_a == [0, 1]
    assert key_b == [0, 1]
    assert indices == [0, 1]

def test_b92_full_no_eve():
    protocol = B92Protocol()
    backend = AerSimulator()
    n = 50

    alice_bits = protocol.generate_bits(n)
    encoded = protocol.encode(alice_bits)

    bob_bases = protocol.generate_bases(n)
    bob_results = protocol.measure(encoded, bob_bases, backend)

    key_a, key_b, _ = protocol.sift(None, bob_bases, alice_bits, bob_results)

    # In B92, if no noise, keys must match perfectly (though they are shorter than n)
    assert key_a == key_b
    assert len(key_a) > 0 # With n=50, highly likely to have conclusive bits
